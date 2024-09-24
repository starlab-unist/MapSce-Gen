import os
import json
import random
import shutil
import argparse

from pathlib import Path
from datetime import datetime


class Arguments:
    def __init__(self, args):
        self.sim_host = "127.0.0.1"
        self.sim_port = 2000
        self.sim_tm_port = 8000

        """
        Fuzzing Phase
        """
        self.max_cycles = args.max_cycles
        self.max_mutations = args.max_mutations
        self.verbose = args.verbose
        self.off_screen = args.off_screen == 0
        self.test_model = "vehicle.tesla.model3"
        self.cycle = 0
        self.round = 0

        """
        Fuzzing Settings
        """
        self.fuzzing_type = args.fuzzing_type
        self.npc_type = args.npc_type
        self.pedestrian_exist = args.pedestrian_exist
        if self.fuzzing_type == "generation":
            print(f"[+] Start Generation-based Fuzzing")
        elif self.fuzzing_type == "mutation":
            print(f"[+] Start Mutation-based Fuzzing")

        """
        Input Directory
        """
        self.seed_dir = Path(args.seed_dir) / args.town
        self.route_key = None
        self.seed_file_name = None
        self.seed_path = None

        """
        Output Directory
        """
        now = datetime.now()
        time_str = now.strftime("%Y_%m_%d_%H_%M_%S")
        self.out_dir = Path(args.out_dir) / time_str
        os.mkdir(self.out_dir)
        self.cycle_dir = None
        self.round_dir = None
        self.out_seed_dir = None
        self.sample_seed = None
        self.model_dir = None
        self.scenario = None
        self.scenario_list = list()
        self.log_dir_list = list()

    def next_cycle(self):
        self.cycle += 1
        self.round = 0
        self.model_dir = None
        self.scenario = None
        self.scenario_list = list()
        self.log_dir_list = list()
        if self.cycle > self.max_cycles:
            print(f"\n\n{'=' * 30} All Fuzzing Cycles Complete")
            return False
        else:
            print(f"\n\n{'=' * 10} Cycle {self.cycle} {'=' * 10}\n")
            self.cycle_dir = self.out_dir / f"cycle_{str(self.cycle)}"
            os.mkdir(self.cycle_dir)
            return True

    def next_mutation(self):
        self.round += 1
        self.model_dir = None
        self.scenario = None
        self.scenario_list = list()
        self.log_dir_list = list()
        if self.round > self.max_mutations:
            print(f"\n\n{'=' * 20} All Mutation Rounds Complete")
            return False
        else:
            print(f"\n\n{'=' * 5} Round {self.round} {'=' * 5}\n")
            self.round_dir = self.cycle_dir / f"round_{str(self.round)}"
            os.mkdir(self.round_dir)
            return True

    def random_select_seed(self):
        sample_seed_dir = self.seed_dir
        rk_list = os.listdir(sample_seed_dir)

        self.route_key = random.choice(rk_list)
        self.seed_file_name = random.choice(os.listdir(sample_seed_dir / self.route_key))
        sample_seed_file = sample_seed_dir / self.route_key / self.seed_file_name
        print(f"[+] Selected Route: {sample_seed_file}")
        return sample_seed_file

    def uncovered_seed(self):
        from Utils.SimpleScenario import SimpleScenario

        uncovered = json.load(Path("/home/dk-kling/Documents/Fuzz4AV/InputGeneration/Seed/uncovered.json").open())

        sample_seed_dir = Path("/home/dk-kling/Documents/Fuzz4AV/InputGeneration/RouteDictionary")
        rk_list = os.listdir(sample_seed_dir)
        break_cond = False
        while not break_cond:
            self.route_key = random.choice(rk_list)

            self.seed_file_name = random.choice(os.listdir(sample_seed_dir / self.route_key))
            sample_seed_file = sample_seed_dir / self.route_key / self.seed_file_name
            _scenario = SimpleScenario(sample_seed_file)

            for lane in _scenario.route:
                if lane in uncovered[_scenario.map]:
                    break_cond = True

        print(f"[+] Selected Route: {sample_seed_file}")

        return sample_seed_file

    def study_seed(self):
        from Utils.SimpleScenario import SimpleScenario
        sample_seed_dir = Path("/home/dk-kling/Documents/Fuzz4AV/InputGeneration/RouteDictionary")
        rk_list = os.listdir(sample_seed_dir)
        break_cond = False
        while not break_cond:
            self.route_key = random.choice(rk_list)

            self.seed_file_name = random.choice(os.listdir(sample_seed_dir / self.route_key))
            sample_seed_file = sample_seed_dir / self.route_key / self.seed_file_name
            _scenario = SimpleScenario(sample_seed_file)

            if len(_scenario.route) > 3:
                print("extended scenario")
                break_cond = True

            prev_lane = "{0:b}".format(int(self.route_key, base=16)).zfill(24)[:8]
            next_lane = "{0:b}".format(int(self.route_key, base=16)).zfill(24)[16:]

            # if prev_lane[:2] == "01":
            #     print("prev = left curv")
            #     break_cond = True
            # elif prev_lane[:2] == "10":
            #     print("prev = right curv")
            #     break_cond = True
            # elif prev_lane[:2] == "11":
            #     print("prev = complex curv")
            #     break_cond = True
            #
            # if next_lane[:2] == "01":
            #     print("next = left curv")
            #     break_cond = True
            # elif next_lane[:2] == "10":
            #     print("next = right curv")
            #     break_cond = True
            # elif next_lane[:2] == "11":
            #     print("next = complex curv")
            #     break_cond = True


            # if prev_lane[2:4] == "01":
            #     print("prev = down elev")
            #     break_cond = True
            # elif prev_lane[2:4] == "10":
            #     print("prev = up elev")
            #     break_cond = True
            # elif prev_lane[2:4] == "11":
            #     print("prev = complex elev")
            #     break_cond = True
            # if next_lane[2:4] == "01":
            #     print("next = down elev")
            #     break_cond = True
            # elif next_lane[2:4] == "10":
            #     print("next = up elev")
            #     break_cond = True
            # elif next_lane[2:4] == "11":
            #     print("next = complex elev")
            #     break_cond = True

        print(f"[+] Selected Route: {sample_seed_file}")

        return sample_seed_file

    def set_seed(self, seed_file):
        self.out_seed_dir = self.cycle_dir / "seed"
        os.mkdir(self.out_seed_dir)

        self.sample_seed = Path(shutil.copy(seed_file, self.out_seed_dir))

    # def prepare_seed_croco_fuzz(self):
    #     for model in self.test_models:
    #         self.model_dir_list.append(self.round_dir / model)
    #         os.mkdir(self.round_dir / model)
    #
    #         scenario_dir = self.round_dir / model / "scenario"
    #         os.mkdir(scenario_dir)
    #
    #         log_dir = self.round_dir / model / "logs"
    #         os.mkdir(log_dir)
    #
    #         self.scenario_list.append(Path(shutil.copy(self.sample_seed, scenario_dir)))
    #         self.log_dir_list.append(log_dir)

    def prepare_seed_experiment(self):

        self.model_dir = self.round_dir / self.test_model
        os.mkdir(self.model_dir)

        scenario_dir = self.round_dir / self.test_model / "scenario"
        os.mkdir(scenario_dir)

        log_dir = self.round_dir / self.test_model / "logs"
        os.mkdir(log_dir)
        os.mkdir(log_dir / "lp_scenario")
        os.mkdir(log_dir / "gp_scenario")
        os.mkdir(log_dir / "xp_scenario")

        self.scenario = Path(shutil.copy(self.sample_seed, scenario_dir))
        self.scenario_list = [
            scenario_dir / "lp_scenario.json",
            scenario_dir / "gp_scenario.json",
            scenario_dir / "xp_scenario.json"
        ]
        self.log_dir_list = [
            log_dir / "lp_scenario",
            log_dir / "gp_scenario",
            log_dir / "xp_scenario"
        ]

    def prepare_seed_case_study(self):

        self.model_dir = self.round_dir / self.test_model
        os.mkdir(self.model_dir)

        scenario_dir = self.round_dir / self.test_model / "scenario"
        os.mkdir(scenario_dir)

        log_dir = self.round_dir / self.test_model / "logs"
        os.mkdir(log_dir)

        self.scenario = Path(shutil.copy(self.sample_seed, scenario_dir))
        self.scenario_list = [
            scenario_dir / "scenario.json",
        ]
        self.log_dir_list = [
            log_dir
        ]

    def all_complex(self):
        from Utils.ComplexScenario import ComplexScenario
        is_complex = list()
        for scenario_path in self.scenario_list:
            if not scenario_path.is_file():
                is_complex.append(False)
                break
            scenario = ComplexScenario(scenario_path)
            is_complex.append(scenario.is_complex)
        return all(is_complex)

    def _is_complex(self):
        from Utils.ComplexScenario import ComplexScenario
        is_complex = list()
        for scenario_path in self.scenario_list:
            if not scenario_path.is_file():
                is_complex.append(False)
                break
            scenario = ComplexScenario(scenario_path)
            is_complex.append(scenario.is_complex)
        return all(is_complex)

    def save_evaluation(self, violation):
        evaluation_path = self.round_dir / "evaluation.json"
        with evaluation_path.open("w") as f:
            json.dump(violation.get_violation(), f)


def get_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-o", "--out-dir", default="out-artifact", type=str,
                            help="Directory to save fuzzing logs")
    arg_parser.add_argument("-s", "--seed-dir", default="InputGeneration/Seed", type=str,
                            help="Seed directory")
    arg_parser.add_argument("-t", "--town", default="Town10HD", type=str,
                            help="Town name")
    arg_parser.add_argument("-c", "--max-cycles", default=1000, type=int,
                            help="Maximum number of loops")
    arg_parser.add_argument("-m", "--max-mutations", default=1, type=int,
                            help="Size of the mutated population per cycle")
    arg_parser.add_argument("-v", "--verbose", action="store_true",
                            default=False, help="enable debug mode")
    arg_parser.add_argument("--off-screen", default=1, type=int,
                            help="Run carla without screen.")
    arg_parser.add_argument("-f", "--fuzzing-type", default="case_study", type=str,
                            help="Determine which type of fuzzing. (generation, mutation, case_study, experiment)")
    arg_parser.add_argument("-n", "--npc-type", default="reasonable", type=str,
                            help="Determine method of npc generation. (random, reasonable)")
    arg_parser.add_argument("-p", "--pedestrian-exist", default=0, type=int,
                            help="Whether fuzzer generate pedestrians or not.")
    # If False, environment variable DISPLAY should be set with following command: "export DISPLAY=:1; xhost +".

    return Arguments(arg_parser.parse_args())
