import os
import json

import carla
from pathlib import Path
from typing import Dict, List, Set
from InputGeneration.RoadGraph import RoadGraph


def get_transform(carla_map, lane: RoadGraph.Lane, ratio) -> carla.Transform:
    if lane.travel_dir == "backward":
        ratio = 1 - ratio
    return carla_map.get_waypoint_xodr(
        int(lane.road_id),
        int(lane.lane_id),
        lane.road_length * ratio
    ).transform


class RouteDictionary:
    def __init__(self, road_graph: RoadGraph, route_dir: Path = None):

        self.road_graph = road_graph
        self.carla_map = self.road_graph.carla_map
        self.hd_map_name = self.road_graph.hd_map_name

        self.__route_dictionary: Dict[str, List[RouteDictionary.Route]] = dict()

        if route_dir is not None:
            # Update __route_dictionary
            self.extract_routes()
            self.route_dir = route_dir / self.hd_map_name
            self.route_dir.mkdir(exist_ok=True)
            self.save_seeds_to_file()

    @property
    def route_keys(self) -> List:
        return list(self.__route_dictionary.keys())

    def get_number(self, r_key):
        return len(self.__route_dictionary[r_key])

    @property
    def route_dictionary(self):
        return self.__route_dictionary

    def save_seeds_to_file(self):
        for route_key in self.__route_dictionary.keys():
            save_path = self.route_dir / str(route_key)
            if not save_path.exists():
                save_path.mkdir(parents=True, exist_ok=False)

            scene_num = 0
            for route in self.__route_dictionary[route_key]:
                scene_num += 1
                with open(os.path.join(save_path, self.hd_map_name + "_" + str(scene_num) + ".json"), "w") as fp:
                    json.dump(
                        route.to_seed(
                            self.carla_map,
                            self.hd_map_name
                        ), fp)

    def extract_routes(self):
        for junction in self.road_graph.junction_dict.values():
            for road in junction.road_dict.values():
                for criteria_lane in road.lane_dict.values():
                    if criteria_lane.lane_type == "sidewalk":
                        continue
                    # print("Criteria:", road.road_id, criteria_lane.lane_id)
                    prev_type, prev_id, prev_lane_id = criteria_lane.predecessor

                    # Previous road of junction road is always road type.
                    # I checked all official HD-Map in carla.
                    # if prev_type != "road":
                    #     print("-" * 5, "Not Road-prev")
                    prev_road = self.road_graph.road_dict[prev_id]
                    # print("Previous:", prev_id, prev_lane_id)
                    prev_lane = prev_road.lane_dict[prev_lane_id]

                    prev_lanes = [prev_lane]
                    while True:
                        prev_type, prev_id, prev_lane_id = prev_lanes[0].predecessor
                        # print("=" * 3, "Previous Lane Analyzing:", prev_type, prev_id, prev_lane_id)
                        # print(prev_lanes)
                        if prev_type == "junction":
                            break
                        elif prev_type == "road":
                            prev_road = self.road_graph.road_dict[prev_id]
                            prev_lane = prev_road.lane_dict[prev_lane_id]
                            prev_lanes.insert(0, prev_lane)
                        else:
                            print("prev_type Error:", prev_type)

                    next_type, next_id, next_lane_id = criteria_lane.successor

                    # if next_type != "road":
                    #     print("-" * 5, "Not Road-next")
                    next_road = self.road_graph.road_dict[next_id]
                    # print("Next:", next_id, next_lane_id)
                    next_lane = next_road.lane_dict[next_lane_id]

                    next_lanes = [next_lane]
                    while True:
                        next_type, next_id, next_lane_id = next_lanes[-1].successor
                        # print("=" * 3, "Next Lane Analyzing:", next_type, next_id, next_lane_id)
                        # print(next_lanes)
                        if next_type == "junction":
                            break
                        elif next_type == "road":
                            next_road = self.road_graph.road_dict[next_id]
                            next_lane = next_road.lane_dict[next_lane_id]
                            next_lanes.append(next_lane)
                        else:
                            print("next_type Error:", next_type)

                    route = prev_lanes + [criteria_lane] + next_lanes
                    sl = set()
                    jl = set()

                    junc_key = int(criteria_lane.lane_key, 2)
                    prev_key = 0
                    next_key = 0

                    max_lane_num = 0
                    for ln in prev_lanes:
                        lane_num = int(ln.lane_key[5:], 2)
                        max_lane_num = max(max_lane_num, lane_num)
                        prev_key = prev_key | int(ln.lane_key[:5], 2)
                        sl.add("{0:x}".format((int(ln.lane_key[:5], 2) << 3) + (lane_num % 7)).zfill(2))

                    max_lane_num %= 7
                    prev_key = (prev_key << 3) + max_lane_num
                    sl.add("{0:x}".format(prev_key).zfill(2))

                    max_lane_num = 0
                    for ln in next_lanes:
                        lane_num = int(ln.lane_key[5:], 2)
                        max_lane_num = max(max_lane_num, lane_num)
                        next_key = next_key | int(ln.lane_key[:5], 2)
                        sl.add("{0:x}".format((int(ln.lane_key[:5], 2) << 3) + (lane_num % 7)).zfill(2))

                    max_lane_num %= 7
                    next_key = (next_key << 3) + max_lane_num
                    sl.add("{0:x}".format(next_key).zfill(2))
                    jl.add("{0:x}".format(junc_key).zfill(2))

                    route_key = (
                        "{0:x}".format(prev_key).zfill(2) +
                        "{0:x}".format(junc_key).zfill(2) +
                        "{0:x}".format(next_key).zfill(2)
                    )
                    self.add_route(self.Route(route_key, route, criteria_lane, junction.junction_id, sl, jl))

    def extract_simple_routes(self):
        for junction in self.road_graph.junction_dict.values():
            for road in junction.road_dict.values():
                for criteria_lane in road.lane_dict.values():
                    if criteria_lane.lane_type == "sidewalk":
                        continue
                    prev_type, prev_id, prev_lane_id = criteria_lane.predecessor

                    prev_road = self.road_graph.road_dict[prev_id]
                    prev_lane = prev_road.lane_dict[prev_lane_id]

                    prev_lanes = [prev_lane]

                    next_type, next_id, next_lane_id = criteria_lane.successor

                    next_road = self.road_graph.road_dict[next_id]
                    next_lane = next_road.lane_dict[next_lane_id]

                    next_lanes = [next_lane]

                    route = prev_lanes + [criteria_lane] + next_lanes
                    sl = set()
                    jl = set()

                    junc_key = int(criteria_lane.lane_key, 2)
                    prev_key = 0
                    next_key = 0

                    max_lane_num = 0
                    for ln in prev_lanes:
                        lane_num = int(ln.lane_key[5:], 2)
                        max_lane_num = max(max_lane_num, lane_num)
                        prev_key = prev_key | int(ln.lane_key[:5], 2)

                    max_lane_num %= 7
                    prev_key = (prev_key << 3) + max_lane_num
                    sl.add("{0:x}".format(prev_key).zfill(2))

                    max_lane_num = 0
                    for ln in next_lanes:
                        lane_num = int(ln.lane_key[5:], 2)
                        max_lane_num = max(max_lane_num, lane_num)
                        next_key = next_key | int(ln.lane_key[:5], 2)

                    max_lane_num %= 7
                    next_key = (next_key << 3) + max_lane_num
                    sl.add("{0:x}".format(next_key).zfill(2))
                    jl.add("{0:x}".format(junc_key).zfill(2))

                    route_key = (
                        "{0:x}".format(junc_key).zfill(2)
                    )
                    self.add_route(self.Route(route_key, route, criteria_lane, junction.junction_id, sl, jl))

    def add_route(self, route):
        if route.key in self.__route_dictionary:
            self.__route_dictionary[route.key].append(route)
        else:
            self.__route_dictionary[route.key] = [route]

    class Route:
        def __init__(self, route_key, route: List[RoadGraph.Lane], criteria_lane, junction_id, sl, jl):
            self.route_key = route_key
            self.route = route
            self.criteria_lane = criteria_lane
            self.junction_id = junction_id
            self.covered_sl = sl
            self.covered_jl = jl

        @property
        def key(self) -> str:
            return self.route_key

        @property
        def start_lane(self) -> RoadGraph.Lane:
            return self.route[0]

        @property
        def dest_lane(self) -> RoadGraph.Lane:
            return self.route[-1]

        @property
        def covered(self) -> Set:
            return self.covered_sl

        @property
        def j_key(self) -> Set:
            return self.covered_jl

        def get_coordinate(self, carla_map: carla.Map):
            s_lane = self.route[0]
            d_lane = self.route[-1]

            sp = get_transform(carla_map, s_lane, 0.1)
            dp = get_transform(carla_map, d_lane, 0.9)

            return sp, dp

        def get_coordinate_with_ratio(self, carla_map: carla.Map, r1, r2):
            s_lane = self.route[0]
            d_lane = self.route[-1]

            sp = get_transform(carla_map, s_lane, r1)
            dp = get_transform(carla_map, d_lane, r2)

            return sp, dp

        def to_seed(self, carla_map: carla.Map, map_name: str):
            sp, dp = self.get_coordinate(carla_map)
            if sp is not None and dp is not None:
                return _to_seed_dict(map_name, self.start_lane, self.dest_lane, sp, dp, self.route, self.junction_id)
            else:
                return None


def _to_seed_dict(map_name, sl, dl, sp, dp, route, junction_id):
    route_list = list()
    for route_lane in route:
        route_list.append((route_lane.road_id, route_lane.lane_id))

    return {
        "map": map_name,
        "mutation": 0,
        "ego_model": {
            "name": None,
            "extent_x": None,
            "extent_y": None,
        },
        "mission": {
            "start": {
                "road_id": sl.road_id,
                "lane_id": sl.lane_id,
                "ratio": 0.1,
                "x": sp.location.x,
                "y": sp.location.y,
                "z": sp.location.z,
                "roll": sp.rotation.roll,
                "pitch": sp.rotation.pitch,
                "yaw": sp.rotation.yaw
            },
            "dest": {
                "road_id": dl.road_id,
                "lane_id": dl.lane_id,
                "ratio": 0.9,
                "x": dp.location.x,
                "y": dp.location.y,
                "z": dp.location.z,
                "roll": dp.rotation.roll,
                "pitch": dp.rotation.pitch,
                "yaw": dp.rotation.yaw
            },
            "route": route_list
        },
        "target": junction_id,
        "npc": {
            "vehicles": [],
            "pedestrians": []
        },
        "weather": {
            'cloud': 0,
            'rain': 0,
            'puddle': 0,
            'wind': 0,
            'fog': 0,
            'wetness': 0,
            'angle': 0,
            'altitude': 60
        },
        "puddles": []
    }
