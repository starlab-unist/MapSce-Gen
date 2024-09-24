import atexit
import warnings
from Utils.tools import set_environ
set_environ()


if __name__ == '__main__':
    from Utils import executor
    from Utils.tools import exit_handler
    from Execution.sub_arguments import complicate_arguments
    from Concretization.Complicator import Complicator

    from AD.Autoware.tools.constants import CARLA_VERSION
    from AD.Autoware.tools.utils import run_carla_with_docker

    cp_args = complicate_arguments()
    warnings.filterwarnings("ignore", category=UserWarning)
    atexit.register(exit_handler, cp_args.sim_port)

    run_carla_with_docker(version=CARLA_VERSION, offscreen=True)
    client, tm, world = executor.connect(cp_args, 0)

    complicator = Complicator(client, cp_args)
    complicator.update_model_z()
    complicator.generate_predefined_weather()
    if complicator.fuzzing_type == "experiment":
        complicator.generate_pedestrian_class()
    if complicator.fuzzing_type == "case_study":
        complicator.generate_dynamic_npc()


