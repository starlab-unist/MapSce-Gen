from Utils.tools import set_environ
set_environ()

if __name__ == '__main__':
    from AD.Autoware.tools.constants import CARLA_VERSION
    from AD.Autoware.tools.utils import run_carla_with_docker
    run_carla_with_docker(version=CARLA_VERSION, offscreen=False)
