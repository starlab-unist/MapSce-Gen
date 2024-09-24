import math
import random

from Concretization.NPC import VehicleLib, PedestrianLib
from Concretization.ScenarioObjects.Pedestrian import Pedestrian
from Concretization.ScenarioObjects.Vehicle import Vehicle
from InputGeneration.RoadGraph import RoadGraph
from Utils.ComplexScenario import ComplexScenario

# Actor Attributes
WALKER_MAX_SPEED = 5  # m/s

# Map Attributes
VEHICLE_NUM_FOR_MAP = {
    'Town01': 120,      # sps: 255
    'Town02': 70,       # sps: 101
    'Town03': 70,       # sps: 265
    'Town04': 150,      # sps: 372
    'Town05': 120,      # sps: 302
    'Town10HD': 70      # sps: 155
}


class ObjectManager:

    def __init__(self, client, hd_map_name):
        self.client = client
        self.world = self.client.load_world(hd_map_name)
        self.world.wait_for_tick()

        self.road_graph = RoadGraph(self.client, hd_map_name)

        self.vehicle_lib = list()
        for v in VehicleLib.values():
            self.vehicle_lib += v

        self.walker_lib = list()
        for p in PedestrianLib.values():
            self.walker_lib += p

    def generate_traffic(self, scenario: ComplexScenario):
        sps = self.world.get_map().get_spawn_points()
        sps = random.sample(sps, VEHICLE_NUM_FOR_MAP[self.road_graph.hd_map_name])
        for sp in sps:
            bp_str = random.choice(self.vehicle_lib)
            bp = self.world.get_blueprint_library().find(bp_str)
            actor = self.world.try_spawn_actor(bp, sp)
            ex = actor.bounding_box.extent.x
            ey = actor.bounding_box.extent.y
            if actor is None:
                print("ACTOR ERROR")
            scenario.add_vehicle(Vehicle(bp_str, sp, ex, ey))

    def generate_relative_vehicles(self, scenario: ComplexScenario):
        junction = self.road_graph.junction_dict[scenario.target]
        area_lanes, road_set = junction.get_incoming_area(self.road_graph)
        # print(f"# of lanes: {len(area_lanes)}")
        actors = list()
        for s_lane in area_lanes:
            n = round(s_lane.road_length / 20)
            n = random.randint(0, n)
            # print(n)
            for i in range(n):
                ratio = random.random()
                sp = self.road_graph.carla_map.get_waypoint_xodr(
                    int(s_lane.road_id),
                    int(s_lane.lane_id),
                    s_lane.road_length * (1 - ratio)
                ).transform
                if sp.location.distance(scenario.sp_loc) < 5:
                    continue
                skip = False
                for curr_actor in actors:
                    if sp.location.distance(curr_actor.get_location()) < 7:
                        skip = True
                if skip:
                    continue
                bp_str = random.choice(self.vehicle_lib)
                bp = self.world.get_blueprint_library().find(bp_str)
                actor = self.world.try_spawn_actor(bp, sp)
                self.world.wait_for_tick()
                while actor is None:
                    sp.location.z += 0.01
                    actor = self.world.try_spawn_actor(bp, sp)
                    self.world.wait_for_tick()
                ex = actor.bounding_box.extent.x
                ey = actor.bounding_box.extent.y
                actors.append(actor)
                v = Vehicle(bp_str, sp, ex, ey)
                if random.random() < 0.2:
                    v.ignore_traffic = True

                scenario.add_vehicle(v)

    def generate_linear_pedestrian(self, scenario: ComplexScenario, ped_num):
        if ped_num == 0:
            return -1
        p_num = ped_num

        while p_num > 0:
            route = scenario.route

            road = None
            while road is None:
                route_lane = random.choice(route)
                road = self.road_graph.whole_road[route_lane[0]]
                if road.num_sidewalk == 0:
                    road = None

            s_lane = None
            while s_lane is None:
                s_lane = random.choice(list(road.lane_dict.values()))
                if s_lane.lane_type != "sidewalk":
                    s_lane = None

            ratio = random.random()

            sp = self.road_graph.carla_map.get_waypoint_xodr(
                int(s_lane.road_id),
                int(s_lane.lane_id),
                s_lane.road_length * (1 - ratio)
            ).transform

            dp = self.road_graph.carla_map.get_waypoint_xodr(
                int(route_lane[0]),
                int(route_lane[1]),
                s_lane.road_length * (1 - ratio)
            ).transform

            sp.location.x += random.random() * 2 - 1
            sp.location.y += random.random() * 2 - 1

            sp.rotation.yaw = random.randint(0, 360)

            bp_str = random.choice(self.walker_lib)
            bp = self.world.get_blueprint_library().find(bp_str)

            actor = self.world.try_spawn_actor(bp, sp)
            self.world.wait_for_tick()

            while actor is None:
                sp.location.z += 0.01
                actor = self.world.try_spawn_actor(bp, sp)
                self.world.wait_for_tick()

            ex = actor.bounding_box.extent.x
            ey = actor.bounding_box.extent.y

            speed = random.uniform(2, WALKER_MAX_SPEED)
            td = random.uniform(10, 20)

            scenario.add_pedestrian(Pedestrian(bp_str, sp, dp, speed, td, ex, ey))

            scenario.add_pedestrian(Pedestrian(bp_str, sp, dp, speed, td, ex, ey, 1))
            p_num -= 1

    def generate_legal_pedestrian(self, scenario: ComplexScenario, ped_num):
        if ped_num == 0:
            return -1
        p_num = ped_num

        route = scenario.route
        junction = self.road_graph.junction_dict[scenario.target]

        t = None

        for pivot in range(len(route)):
            for _road in list(junction.road_dict.values()):
                if route[pivot][0] == _road.road_id:
                    t = pivot
                    break
            if t is not None:
                break

        if t is None:
            return -1

        prev_l = route[t - 1]
        next_l = route[t + 1]

        if self.road_graph.whole_road[prev_l[0]].num_sidewalk == 0 and self.road_graph.whole_road[next_l[0]] == 0:
            return -1

        while p_num > 0:
            if random.random() > 0.5:
                g_road = self.road_graph.whole_road[prev_l[0]]
                target_l = prev_l
            else:
                g_road = self.road_graph.whole_road[next_l[0]]
                target_l = next_l

            s_lane = None
            if g_road.num_sidewalk == 0:
                continue

            while s_lane is None:
                s_lane = random.choice(list(g_road.lane_dict.values()))
                if s_lane.lane_type != "sidewalk":
                    s_lane = None

            ratio = 0.99 if s_lane.travel_dir == "backward" else 0.01

            sp = self.road_graph.carla_map.get_waypoint_xodr(
                int(s_lane.road_id),
                int(s_lane.lane_id),
                s_lane.road_length * ratio
            ).transform

            d_lane = self.road_graph.whole_road[target_l[0]].lane_dict[target_l[1]]

            ratio = 0.99 if d_lane.travel_dir == "backward" else 0.01

            dp = self.road_graph.carla_map.get_waypoint_xodr(
                int(target_l[0]),
                int(target_l[1]),
                s_lane.road_length * ratio
            ).transform

            sp.location.x += random.random() * 2 - 1
            sp.location.y += random.random() * 2 - 1

            radian_yaw = math.atan2(dp.location.y - sp.location.y, dp.location.x - sp.location.x)
            yaw = math.degrees(radian_yaw)
            sp.rotation.yaw = yaw

            bp_str = random.choice(self.walker_lib)
            bp = self.world.get_blueprint_library().find(bp_str)

            actor = self.world.try_spawn_actor(bp, sp)
            self.world.wait_for_tick()

            while actor is None:
                sp.location.z += 0.01
                actor = self.world.try_spawn_actor(bp, sp)
                self.world.wait_for_tick()

            ex = actor.bounding_box.extent.x
            ey = actor.bounding_box.extent.y

            speed = random.uniform(2, WALKER_MAX_SPEED)
            td = random.uniform(10, 20)

            scenario.add_pedestrian(Pedestrian(bp_str, sp, dp, speed, td, ex, ey))
            p_num -= 1

    def generate_route_aware_pedestrians(self, scenario: ComplexScenario):
        route = scenario.route
        p_num = 0
        for route_lane in route:
            road = self.road_graph.whole_road[route_lane[0]]
            for s_lane in list(road.lane_dict.values()):
                if s_lane.lane_type == "sidewalk":
                    n = round(s_lane.road_length / 30)
                    n = random.randint(0, n)
                    p_num += n
                    while n > 0:
                        ratio = random.random()

                        sp = self.road_graph.carla_map.get_waypoint_xodr(
                            int(s_lane.road_id),
                            int(s_lane.lane_id),
                            s_lane.road_length * (1 - ratio)
                        ).transform

                        dp = self.road_graph.carla_map.get_waypoint_xodr(
                            int(route_lane[0]),
                            int(route_lane[1]),
                            s_lane.road_length * (1 - ratio)
                        ).transform

                        sp.location.x += random.random() * 2 - 1
                        sp.location.y += random.random() * 2 - 1

                        radian_yaw = math.atan2(dp.location.y - sp.location.y, dp.location.x - sp.location.x)
                        yaw = math.degrees(radian_yaw)
                        sp.rotation.yaw = yaw

                        bp_str = random.choice(self.walker_lib)
                        bp = self.world.get_blueprint_library().find(bp_str)

                        actor = self.world.try_spawn_actor(bp, sp)
                        self.world.wait_for_tick()

                        while actor is None:
                            sp.location.z += 0.01
                            actor = self.world.try_spawn_actor(bp, sp)
                            self.world.wait_for_tick()

                        ex = actor.bounding_box.extent.x
                        ey = actor.bounding_box.extent.y

                        speed = random.uniform(2, WALKER_MAX_SPEED)
                        td = random.uniform(10, 20)

                        scenario.add_pedestrian(Pedestrian(bp_str, sp, dp, speed, td, ex, ey))
                        n -= 1
        return p_num
