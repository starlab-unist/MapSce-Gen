import os
import time

from pathlib import Path
from multiprocessing import Process

from Concretization.ObjectManager import ObjectManager
from Concretization.WeatherManager import generate_weather, mutate_weather
from Utils.SimpleScenario import SimpleScenario
from Utils.ComplexScenario import ComplexScenario


def complicate_seed(args):
    while not args.all_complex():
        complicate_p = Process(
            target=os.system,
            args=(f"python3 complicate.py "
                  f"-d {args.round_dir} "
                  f"-s {args.sample_seed} "
                  f"-n {args.npc_type} "
                  f"-p {args.pedestrian_exist}",)
        )

        complicate_p.start()
        complicate_p.join()
        time.sleep(2)

    # while not args.all_complex():
    #     complicate_p = Process(
    #         target=os.system,
    #         args=(f"python3 complicate.py "
    #               f"-d {args.round_dir} "
    #               f"-s {args.sample_seed} "
    #               f"-n {args.npc_type} "
    #               f"-p {args.pedestrian_exist}",)
    #     )
    #
    #     complicate_p.start()
    #     complicate_p.join()
    #     time.sleep(2)


class Complicator:
    def __init__(self, client, args):
        self.npc_type = args.npc_type
        self.pedestrian_exist = args.pedestrian_exist
        self.fuzzing_type = args.fuzzing_type

        self.client = client
        self.round_dir = args.round_dir
        self.test_model = "vehicle.tesla.model3"

        self.seed_path = args.seed_path
        self.scenario_name = os.path.basename(args.seed_path)
        self.map_name = SimpleScenario(args.seed_path).map

        self.scenario = ComplexScenario(args.seed_path)

        self.object_manager = ObjectManager(self.client, self.map_name)

    def generate_predefined_weather(self):
        generate_weather(self.scenario)
        new_scenario = ComplexScenario(self.round_dir / self.test_model / "scenario" / self.scenario_name)
        new_scenario.weather = self.scenario.weather
        new_scenario.save_scenario()
        self.scenario = new_scenario

    def update_model_z(self):
        new_scenario = ComplexScenario(self.round_dir / self.test_model / "scenario" / self.scenario_name)

        world = self.client.load_world(self.map_name)
        world.wait_for_tick()
        bp = world.get_blueprint_library().find(self.test_model)
        sp = new_scenario.sp_transform
        dp = new_scenario.dp_transform

        actor = world.try_spawn_actor(bp, sp)
        world.wait_for_tick()

        while actor is None:
            sp.location.z += 0.01
            actor = world.try_spawn_actor(bp, sp)
            world.wait_for_tick()

        actor = world.try_spawn_actor(bp, dp)
        world.wait_for_tick()

        while actor is None:
            dp.location.z += 0.01
            actor = world.try_spawn_actor(bp, dp)
            world.wait_for_tick()

        new_scenario.ego_model = {
            "name": self.test_model,
            "extent_x": actor.bounding_box.extent.x,
            "extent_y": actor.bounding_box.extent.y
        }

        new_scenario.update_sz(sp.location.z)
        new_scenario.update_dz(dp.location.z)
        new_scenario.save_scenario()
        self.scenario = new_scenario

    def generate_traffic(self):
        self.object_manager.generate_relative_vehicles(self.scenario)
        new_scenario = ComplexScenario(self.round_dir / self.test_model / "scenario" / self.scenario_name)
        new_scenario.npc = self.scenario.npc
        new_scenario.ego_model = self.scenario.ego_model
        new_scenario.save_scenario()

    def generate_dynamic_npc(self):

        if self.npc_type == "random":
            print("    Random Generation")
            self.object_manager.generate_relative_vehicles(self.scenario)
            
        elif self.npc_type == "reasonable":
            print("    Reasonable Generation")
            self.object_manager.generate_relative_vehicles(self.scenario)

        if self.pedestrian_exist:
            print("    Pedestrian Exist")
            self.object_manager.generate_route_aware_pedestrians(self.scenario)

        new_scenario = ComplexScenario(self.round_dir / self.test_model / "scenario" / self.scenario_name)
        new_scenario.npc = self.scenario.npc
        new_scenario.change_path(self.round_dir / self.test_model / "scenario" / "scenario.json")
        new_scenario.save_scenario()

    def generate_pedestrian_class(self):
        import copy

        # self.object_manager.generate_relative_vehicles(self.scenario)

        linear_scenario = copy.deepcopy(self.scenario)
        linear_scenario.change_path(self.round_dir / self.test_model / "scenario" / "lp_scenario.json")

        legal_scenario = copy.deepcopy(self.scenario)
        legal_scenario.change_path(self.round_dir / self.test_model / "scenario" / "gp_scenario.json")

        expansive_scenario = copy.deepcopy(self.scenario)
        expansive_scenario.change_path(self.round_dir / self.test_model / "scenario" / "xp_scenario.json")

        print("expansive")
        p_num = self.object_manager.generate_route_aware_pedestrians(expansive_scenario)
        expansive_scenario.save_scenario()

        print("linear")
        self.object_manager.generate_linear_pedestrian(linear_scenario, p_num)
        linear_scenario.save_scenario()

        print("legal")
        self.object_manager.generate_legal_pedestrian(legal_scenario, p_num)
        legal_scenario.save_scenario()

    def mutate_ego_vehicle(self):
        import random
        from InputGeneration.RouteDictionary import RouteDictionary
        from InputGeneration.RoadGraph import RoadGraph

        rg = RoadGraph(self.client, self.map_name)

        sl = rg.whole_road[self.scenario.route[0][0]].lane_dict[self.scenario.route[0][1]]
        dl = rg.whole_road[self.scenario.route[-1][0]].lane_dict[self.scenario.route[-1][1]]

        route = RouteDictionary.Route(None, [sl, dl], None, self.scenario.target)

        r1 = self.scenario.mission["start"]["ratio"] + (random.random() * 0.2 - 0.1)
        r2 = self.scenario.mission["dest"]["ratio"] + (random.random() * 0.2 - 0.1)

        r1 = 0 if r1 < 0 else r1
        r2 = 0 if r2 < 0 else r2

        r1 = 1 if r1 > 1 else r1
        r2 = 1 if r2 > 1 else r2

        sp, dp = route.get_coordinate_with_ratio(rg.carla_map, r1, r2)

        # for model in self.test_models:
        #     new_scenario = ComplexScenario(self.round_dir / model / "scenario" / self.scenario_name)
        #     new_scenario.update_sp(sp)
        #     new_scenario.update_dp(dp)
        #     new_scenario.save_scenario()

    def mutate_weather(self):
        mutate_weather(self.scenario)
        new_scenario = ComplexScenario(self.round_dir / self.test_model / "scenario" / self.scenario_name)
        new_scenario.weather = self.scenario.weather
        new_scenario.save_scenario()
