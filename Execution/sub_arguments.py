import argparse
from pathlib import Path


class IGArguments:
    def __init__(self):
        self.sim_host = "127.0.0.1"
        self.sim_port = [2000]
        self.debug = False
        self.sim_tm_port = [8000]


class CPArguments:
    def __init__(self, round_dir, seed_path, npc_type, pedestrian_exist, fuzzing_type):
        self.sim_host = "127.0.0.1"
        self.sim_port = [2000]
        self.debug = False
        self.sim_tm_port = [8000]
        self.round_dir = Path(round_dir)
        self.seed_path = Path(seed_path)
        self.npc_type = npc_type
        self.pedestrian_exist = False if pedestrian_exist == 0 else True
        self.fuzzing_type = fuzzing_type


class ExeArguments:
    def __init__(self, args):
        self.port = args.port
        self.scenario_file = Path(args.scenario_file)
        self.out_dir = Path(args.out_dir)
        self.off_screen = args.off_screen
        self.cycle = args.cycle


def get_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-p", "--port", default=2000, type=int,
                            help="Port number of carla simulator.")
    arg_parser.add_argument("-s", "--scenario-file", type=str,
                            help="Path of scenario file.")
    arg_parser.add_argument("-o", "--out-dir", type=str,
                            help="Path of output directory.")
    arg_parser.add_argument("--off-screen", default=True, type=bool,
                            help="Run carla without screen.")
    arg_parser.add_argument("-c", "--cycle", default=0, type=int,
                            help="The number of cycle.")
    # If False, environment variable DISPLAY should be set with following command: "export DISPLAY=:1; xhost +".

    return ExeArguments(arg_parser.parse_args())


def complicate_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-d", "--round-dir", type=Path,
                            help="Path of round directory.")
    arg_parser.add_argument("-s", "--seed-path", type=Path,
                            help="Path of seed file.")
    arg_parser.add_argument("-f", "--fuzzing-type", default="case_study", type=str,
                            help="Determine which type of fuzzing. (generation, mutation, case_study, experiment)")
    arg_parser.add_argument("-n", "--npc-type", default="rea", type=str,
                            help="Determine method of npc generation. (random, reasonable)")
    arg_parser.add_argument("-p", "--pedestrian-exist", default=1, type=int,
                            help="Whether fuzzer generate pedestrians or not.")
    _a = arg_parser.parse_args()
    return CPArguments(_a.round_dir, _a.seed_path, _a.npc_type, _a.pedestrian_exist, _a.fuzzing_type)
