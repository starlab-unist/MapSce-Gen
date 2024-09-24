import os
import sys
import time
from typing import Dict, Any

STRAIGHT = 0
LEFT_CURV = 1
RIGHT_CURV = 2
COMPLEX_CURV = 3

FLAT = 0
DOWNHILL = 1
UPHILL = 2
COMPLEX_HILL = 3

NORMAL_SPEED = 0
HIGH_SPEED = 1


class RoadGraph:
    def __init__(self, client, hd_map_name, auto=True):
        self.whole_road: Dict[str, RoadGraph.Road] = dict()
        self.road_dict: Dict[str, RoadGraph.Road] = dict()
        self.junction_dict: Dict[str, RoadGraph.Junction] = dict()
        self.hd_map_name = hd_map_name
        self.client = client

        if auto:
            world = self.client.load_world(self.hd_map_name)

            world.wait_for_tick()
            self.carla_map = world.get_map()
            xodr = self.carla_map.to_opendrive()

            try:
                self.parse_lane(xodr)
            except Exception as e:
                print(f"[-] HD-Map is not specific to parse: {e}")
                sys.exit(-1)

    def save_map(self):
        self.carla_map.save_to_disk(os.getcwd() + "/InputGeneration/HD-Map/" + self.hd_map_name + ".xodr")

    def parse_lane(self, hd_map_str):
        import xml.etree.ElementTree as ET

        sim_map_tree = ET.fromstring(hd_map_str)

        """
        Junction Analysis
        """
        for junction in sim_map_tree.findall("junction"):
            connected_road = set()
            for connection in junction.findall("connection"):
                connected_road.add(connection.get("incomingRoad"))
            self.junction_dict[junction.get("id")] = self.Junction(junction.get("id"), connected_road)

        """
        Road Analysis
        """
        for road in sim_map_tree.findall("road"):
            lane_dict = dict()
            link = road.find("link")
            road_length = road.get("length")

            """
            Curvature Analysis 
            """
            curvature_state = STRAIGHT
            curvature_left = False
            curvature_right = False

            pv = road.find("planView")
            for geometry in pv.findall("geometry"):
                if geometry.find("arc") is not None:
                    curvature = float(geometry.find("arc").get("curvature"))
                    if curvature > 0.02:
                        curvature_left = True
                    if curvature < -0.02:
                        curvature_right = True
            if curvature_left:
                curvature_state = LEFT_CURV
                if curvature_right:
                    curvature_state = COMPLEX_CURV
            elif curvature_right:
                curvature_state = RIGHT_CURV

            """
            Elevation Analysis
            """
            elevation_state = FLAT

            if road.get("junction") == "-1":
                ep = road.find("elevationProfile")
                elev_list = list()
                for ev in ep.findall("elevation"):
                    a = float(ev.get("a"))
                    b = float(ev.get("b"))
                    c = float(ev.get("c"))
                    d = float(ev.get("d"))
                    elev = a + b + c + d
                    elev_list.append(elev)
                if max(elev_list) != 0 or min(elev_list) != 0:
                    z = max(elev_list) - min(elev_list)
                    if z > 3:
                        if elev_list == sorted(elev_list):
                            elevation_state = UPHILL
                        elif elev_list == sorted(elev_list, reverse=True):
                            elevation_state = DOWNHILL
                        else:
                            elevation_state = COMPLEX_HILL

            """
            Speed Limit Analysis
            """
            speed_state = NORMAL_SPEED

            if road.get("junction") == "-1":
                tp = road.find("type")

                sp = tp.find("speed")
                speed_limit = int(float(sp.get("max")))
                if speed_limit > 55:
                    speed_state = HIGH_SPEED

            """
            Lane Classification
            """
            for lanes in road.findall("lanes"):
                lane_section_checked = False
                for lane_section in lanes.findall("laneSection"):
                    if not lane_section_checked:
                        lane_section_checked = True
                        if lane_section.find("left") is not None:
                            for lane in lane_section.find("left").findall("lane"):

                                predecessor_lane = None
                                successor_lane = None
                                if lane.find("link") is not None:
                                    if lane.find("link").find("predecessor") is not None:
                                        predecessor_lane = lane.find("link").find("predecessor").get("id")
                                if lane.find("link") is not None:
                                    if lane.find("link").find("successor") is not None:
                                        successor_lane = lane.find("link").find("successor").get("id")

                                if lane.get("type") == "sidewalk" or lane.get("type") == "driving":
                                    ud = lane.find("userData")
                                    vl = ud.find("vectorLane")

                                    lane_object = self.Lane(
                                        lane.get("id"),
                                        lane.get("type"),
                                        vl.get("travelDir"),
                                        road.get("id"),
                                        curvature_state,
                                        elevation_state,
                                        speed_state,
                                        link.find("predecessor").get("elementType") if link.find(
                                            "predecessor") is not None else None,
                                        link.find("predecessor").get("elementId") if link.find(
                                            "predecessor") is not None else None,
                                        link.find("successor").get("elementType") if link.find(
                                            "successor") is not None else None,
                                        link.find("successor").get("elementId") if link.find(
                                            "successor") is not None else None,
                                        predecessor_lane,
                                        successor_lane
                                    )
                                    lane_dict[lane.get("id")] = lane_object

                        if lane_section.find("right") is not None:
                            for lane in lane_section.find("right").findall("lane"):

                                predecessor_lane = None
                                successor_lane = None
                                if lane.find("link") is not None:
                                    if lane.find("link").find("predecessor") is not None:
                                        predecessor_lane = lane.find("link").find("predecessor").get("id")
                                if lane.find("link") is not None:
                                    if lane.find("link").find("successor") is not None:
                                        successor_lane = lane.find("link").find("successor").get("id")

                                if lane.get("type") == "sidewalk" or lane.get("type") == "driving":
                                    ud = lane.find("userData")
                                    vl = ud.find("vectorLane")

                                    lane_object = self.Lane(
                                            lane.get("id"),
                                            lane.get("type"),
                                            vl.get("travelDir"),
                                            road.get("id"),
                                            curvature_state,
                                            elevation_state,
                                            speed_state,
                                            link.find("predecessor").get("elementType") if link.find("predecessor") is not None else None,
                                            link.find("predecessor").get("elementId") if link.find("predecessor") is not None else None,
                                            link.find("successor").get("elementType") if link.find("successor") is not None else None,
                                            link.find("successor").get("elementId") if link.find("successor") is not None else None,
                                            predecessor_lane,
                                            successor_lane
                                    )
                                    lane_dict[lane.get("id")] = lane_object

                    # We Supposed the latest lane section is followed in s coordinate
                    else:
                        tmp = dict()
                        for ln in lane_dict.keys():
                            tmp[ln] = lane_dict[ln]

                        if lane_section.find("left") is not None:
                            for lane in lane_section.find("left").findall("lane"):
                                if lane.get("type") == "sidewalk" or lane.get("type") == "driving":
                                    link = lane.find("link")
                                    connected_prev_lane_id = link.find("predecessor").get("id")
                                    connected_next_lane_id = link.find("successor").get("id")
                                    for i in tmp.keys():
                                        if tmp[i].link is not None:
                                            if tmp[i].link[-1] == connected_prev_lane_id:
                                                lane_dict[i].successor_lane_id = connected_next_lane_id
                                                lane_dict[i].link.append(lane.get("id"))
                                                tmp.pop(i)
                                                break
                                        elif tmp[i].lane_id == connected_prev_lane_id:
                                            lane_dict[i].successor_lane_id = connected_next_lane_id
                                            lane_dict[i].link = [lane.get("id")]
                                            tmp.pop(i)
                                            break

                        if lane_section.find("right") is not None:
                            for lane in lane_section.find("right").findall("lane"):
                                if lane.get("type") == "sidewalk" or lane.get("type") == "driving":
                                    link = lane.find("link")
                                    connected_prev_lane_id = link.find("predecessor").get("id")
                                    connected_next_lane_id = link.find("successor").get("id")
                                    for i in tmp.keys():
                                        if tmp[i].link is not None:
                                            if tmp[i].link[-1] == connected_prev_lane_id:
                                                lane_dict[i].successor_lane_id = connected_next_lane_id
                                                lane_dict[i].link.append(lane.get("id"))
                                                tmp.pop(i)
                                                break
                                        elif tmp[i].lane_id == connected_prev_lane_id:
                                            lane_dict[i].successor_lane_id = connected_next_lane_id
                                            lane_dict[i].link = [lane.get("id")]
                                            tmp.pop(i)
                                            break

            new_road = self.Road(road.get("id"), "road", road_length, lane_dict)

            if road.get("junction") == "-1":

                self.road_dict[road.get("id")] = new_road
                self.whole_road[road.get("id")] = new_road
            else:
                self.junction_dict[road.get("junction")].add_road(new_road)
                self.whole_road[road.get("id")] = new_road

    class Lane:
        def __init__(self, lane_id, lane_type, travel_dir, road_id,
                     curvature_state, elevation_state, speed_state,
                     predecessor_type, predecessor_id,
                     successor_type, successor_id,
                     predecessor_lane_id, successor_lane_id):

            self._curvature_state = curvature_state
            self._elevation_state = elevation_state
            self._speed_state = speed_state

            self.__lane_info: Dict[str, Any] = {
                "id": lane_id,
                "link": None,
                "type": lane_type,
                "travelDir": travel_dir,
                "road_id": road_id,
                "road_length": None,
                "coverage": False,
                "predecessor_type": predecessor_type,
                "predecessor_id": predecessor_id,
                "predecessor_lane_id": predecessor_lane_id,
                "successor_type": successor_type,
                "successor_id": successor_id,
                "successor_lane_id": successor_lane_id,
                "curvature": curvature_state,
                "lane_key": None,
            }

        def adjust_travel_direction(self):
            curvature_state = self._curvature_state
            elevation_state = self._elevation_state
            pt, pi, pl = self.predecessor
            st, si, sl = self.successor
            predecessor_type = pt
            predecessor_id = pi
            predecessor_lane_id = pl
            successor_type = st
            successor_id = si
            successor_lane_id = sl

            if self.travel_dir == "backward":
                if self._curvature_state == LEFT_CURV:
                    curvature_state = RIGHT_CURV
                elif self._curvature_state == RIGHT_CURV:
                    curvature_state = LEFT_CURV
                if self._elevation_state == UPHILL:
                    elevation_state = DOWNHILL
                elif self._elevation_state == DOWNHILL:
                    elevation_state = UPHILL
                predecessor_type = st
                predecessor_id = si
                predecessor_lane_id = sl
                successor_type = pt
                successor_id = pi
                successor_lane_id = pl

            base_lane_key = (curvature_state * (2 ** 6)) + (elevation_state * (2 ** 4)) + (self._speed_state * (2 ** 3))
            self.__lane_info["lane_key"] = str(base_lane_key)
            self.__lane_info["predecessor_type"] = predecessor_type
            self.__lane_info["predecessor_id"] = predecessor_id
            self.__lane_info["predecessor_lane_id"] = predecessor_lane_id

            self.__lane_info["successor_type"] = successor_type
            self.__lane_info["successor_id"] = successor_id
            self.__lane_info["successor_lane_id"] = successor_lane_id
            self.__lane_info["curvature"] = curvature_state

        @property
        def lane_id(self) -> str:
            return self.__lane_info["id"]

        @property
        def lane_type(self) -> str:
            return self.__lane_info["type"]

        @property
        def link(self) -> list:
            return self.__lane_info["link"]

        @property
        def lane_key(self) -> str:
            return self.__lane_info["lane_key"]

        @property
        def successor_lane_id(self) -> str:
            return self.__lane_info["successor_lane_id"]

        @property
        def predecessor_lane_id(self) -> str:
            return self.__lane_info["predecessor_lane_id"]

        @property
        def coverage(self) -> bool:
            return self.__lane_info["coverage"]

        @property
        def travel_dir(self) -> str:
            return self.__lane_info["travelDir"]

        @property
        def road_id(self) -> str:
            return self.__lane_info["road_id"]

        @property
        def road_length(self) -> float:
            return float(self.__lane_info["road_length"])

        @property
        def curvature(self) -> int:
            return self.__lane_info["curvature"]

        @property
        def predecessor(self) -> (str, str, str):
            return (self.__lane_info["predecessor_type"],
                    self.__lane_info["predecessor_id"],
                    self.__lane_info["predecessor_lane_id"])

        @property
        def successor(self) -> (str, str, str):
            return (self.__lane_info["successor_type"],
                    self.__lane_info["successor_id"],
                    self.__lane_info["successor_lane_id"])

        @link.setter
        def link(self, _link) -> None:
            self.__lane_info["link"] = _link

        @lane_key.setter
        def lane_key(self, _lane_key: str) -> None:
            self.__lane_info["lane_key"] = _lane_key

        @road_length.setter
        def road_length(self, _road_length) -> None:
            self.__lane_info["road_length"] = _road_length

        @successor_lane_id.setter
        def successor_lane_id(self, _successor_lane_id: str) -> None:
            self.__lane_info["successor_lane_id"] = _successor_lane_id

        @predecessor_lane_id.setter
        def predecessor_lane_id(self, _predecessor_lane_id: str) -> None:
            self.__lane_info["predecessor_lane_id"] = _predecessor_lane_id

        @coverage.setter
        def coverage(self, _coverage) -> None:
            self.__lane_info["coverage"] = _coverage

    class Road:
        def __init__(self, road_id, road_type, road_length, lane_dict):

            self.road_id = road_id
            self.road_type = road_type
            self.road_length = road_length
            self.num_sidewalk = 0
            self.num_driving = 0
            self.lane_dict = lane_dict

            for lane in lane_dict.values():
                if lane.lane_type == "sidewalk":
                    self.num_sidewalk += 1
                elif lane.lane_type == "driving":
                    self.num_driving += 1

            for lane in lane_dict.values():
                lane.road_length = self.road_length
                lane.adjust_travel_direction()
                lane.lane_key = "{0:b}".format(int(lane.lane_key) + self.num_driving).zfill(8)

        @property
        def id(self) -> str:
            return self.road_id

    class Junction:
        def __init__(self, junction_id, connected_road):
            self.junction_id = junction_id
            self.num_connected_road = len(connected_road)
            self.road_dict: Dict[str, RoadGraph.Road] = dict()

        def add_road(self, road):
            for lane in road.lane_dict.values():
                lane.lane_key = "{0:b}".format(lane.curvature * (2 ** 4) + self.num_connected_road).zfill(8)
            self.road_dict[road.id] = road

        def get_incoming_area(self, road_graph):
            in_roads = list(self.road_dict.values())
            lanes = list()
            connected_junction_roads_set = set()
            for road in in_roads:
                for lane in list(road.lane_dict.values()):
                    if lane.lane_type == "sidewalk":
                        continue
                    area_count = 0
                    prev_type, prev_id, prev_lane_id = lane.predecessor
                    prev_road = road_graph.road_dict[prev_id]
                    prev_lane = prev_road.lane_dict[prev_lane_id]
                    prev_lanes = [prev_lane]

                    while True:
                        prev_type, prev_id, prev_lane_id = prev_lanes[0].predecessor
                        if prev_type == "road":
                            connected_junction_roads_set.add(prev_road)
                            prev_road = road_graph.road_dict[prev_id]
                            prev_lane = prev_road.lane_dict[prev_lane_id]
                            prev_lanes.insert(0, prev_lane)
                        if prev_type == "junction":
                            if area_count > 1:
                                break
                            else:
                                area_count += 1
                                for j in list(road_graph.junction_dict.values()):
                                    if prev_id in list(j.road_dict.keys()):
                                        prev_road = j.road_dict[prev_id]
                                        prev_lane = prev_road.lane_dict[prev_lane_id]
                                        prev_lanes.insert(0, prev_lane)

                    lanes += prev_lanes

            return lanes, connected_junction_roads_set


def get_from_file(client, xodr_file) -> RoadGraph:
    hd_map = open(xodr_file, 'r')
    hd_map_str = hd_map.read()
    hd_map.close()

    rg = RoadGraph(client, os.path.basename(xodr_file), False)
    rg.client.generate_opendrive_world(hd_map_str)
    time.sleep(3)
    world = client.get_world()
    rg.carla_map = world.get_map()
    rg.parse_lane(hd_map_str)

    return rg
