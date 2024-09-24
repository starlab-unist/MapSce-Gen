import atexit
import warnings
from Utils.tools import set_environ
set_environ()


if __name__ == '__main__':
    from Utils.tools import exit_handler
    from Execution.sub_arguments import get_arguments

    import AD.Autoware as Autoware
    from AD.Autoware.tools.constants import CARLA_VERSION
    from AD.Autoware.tools.utils import run_carla_with_docker, record_simulation
    from Utils.ComplexScenario import ComplexScenario

    exe_args = get_arguments()
    warnings.filterwarnings("ignore", category=UserWarning)
    atexit.register(exit_handler, [exe_args.port])

    run_carla_with_docker(version=CARLA_VERSION, offscreen=exe_args.off_screen)

    scenario = ComplexScenario(exe_args.scenario_file)
    state_seed = Autoware.run(scenario)
    violation_seed = state_seed.any_violation()
    record_simulation(exe_args.out_dir, scenario, 0.0, violation_seed, only_measure=True)
