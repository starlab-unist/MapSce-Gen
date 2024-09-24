import random
import math
from InputGeneration.utils import get_random_value


class ScenarioArea:
    def __init__(self, road_graph):
        self.road_graph = road_graph
        self.points, ego_ways, main_junc = road_graph.get_lane_route()
        prev_ways, next_ways, adj_ways = self.road_graph.get_all_ways(main_junc)

        self.sp = self.points[0]
        self.dp = self.points[2]
        self.main_junc = main_junc
        self.ego_st = {"road_id": ego_ways[0], "lane_id": ego_ways[3]}
        self.ego_ed = {"road_id": ego_ways[1], "lane_id": ego_ways[4]}
        self.ego_md = {"road_id": ego_ways[2], "lane_id": ego_ways[5]}
        self.ego_ways = [self.ego_st, self.ego_md, self.ego_ed]
        self.prev_ways = prev_ways
        self.next_ways = next_ways
        self.adj_ways = adj_ways

        if self.ego_st in self.prev_ways:
            self.prev_ways.remove(self.ego_st)
        if self.ego_st in self.adj_ways:
            self.adj_ways.remove(self.ego_st)
        if self.ego_md in self.adj_ways:
            self.adj_ways.remove(self.ego_md)
        if self.ego_ed in self.adj_ways:
            self.adj_ways.remove(self.ego_ed)

    def get_route(self):
        return [
            (self.points[0].location.x, self.points[0].location.y),
            (self.points[3].location.x, self.points[3].location.y)
        ]

    def get_sp(self):
        return self.sp

    def get_dp(self):
        return self.dp

    def get_sw_lengths(self):
        s = set()
        length = 0
        for way in self.prev_ways:
            s.add(way["road_id"])
        for r in list(s):
            length += int(self.road_graph.road_dict[r].length)
        return length

    def get_npc_vehicle_way(self):
        sw = get_random_value(self.prev_ways)
        dw = get_random_value(self.next_ways)

        distance = 0
        while distance < 3:
            sp = self.road_graph.carla_map.get_waypoint_xodr(
                int(sw["road_id"]),
                int(sw["lane_id"]),
                self.road_graph.road_dict[sw["road_id"]].length * random.random()
            ).transform
            distance = sp.location.distance(self.sp.location)

        dp = self.road_graph.carla_map.get_waypoint_xodr(
            int(dw["road_id"]),
            int(dw["lane_id"]),
            self.road_graph.road_dict[dw["road_id"]].length * random.random()
        ).transform

        sp.location.z += 0.5

        return sp, dp

    def get_npc_dynamic_linear_way(self, road=None):
        if road is None:
            overlap_w = random.choice([self.ego_st, self.ego_ed])
        else:
            overlap_w = road

        # try:
        length = self.road_graph.road_dict[overlap_w["road_id"]].length
        available = list(self.road_graph.road_dict[overlap_w["road_id"]].child.keys())

        # except KeyError:
        #     length = self.main_junc.find_road(overlap_w["road_id"]).length
        #     available = list(self.main_junc.find_road(overlap_w["road_id"]).child.keys())

        ratio = random.random()
        overlap_p = self.road_graph.carla_map.get_waypoint_xodr(
            int(overlap_w["road_id"]),
            int(overlap_w["lane_id"]),
            length * ratio
        ).transform

        if overlap_w["lane_id"] in available:
            available.remove(overlap_w["lane_id"])

        sp = self.road_graph.carla_map.get_waypoint_xodr(
            int(overlap_w["road_id"]),
            int(random.choice(available)),
            length * ratio
        ).transform
        sp.location.x += random.random() * 2 - 1
        sp.location.y += random.random() * 2 - 1

        radian_yaw = math.atan2(overlap_p.location.y - sp.location.y, overlap_p.location.x - sp.location.x)
        yaw = math.degrees(radian_yaw)
        sp.rotation.yaw = yaw
        sp.location.z += 2
        return sp, overlap_p

    def get_static_location(self):
        adj_w = get_random_value(self.adj_ways)

        adj_p = self.road_graph.carla_map.get_waypoint_xodr(
            int(adj_w["road_id"]),
            int(adj_w["lane_id"]),
            self.road_graph.road_dict[adj_w["road_id"]].length * random.random()
        ).transform

        return adj_p