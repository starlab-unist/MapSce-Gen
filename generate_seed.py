import os

from Utils.tools import set_environ
set_environ()


if __name__ == '__main__':
    from Utils import executor
    from pathlib import Path
    from Execution.sub_arguments import IGArguments

    from InputGeneration.RouteDictionary import RouteDictionary
    from InputGeneration.RoadGraph import RoadGraph

    from AD.Autoware.tools.constants import CARLA_VERSION
    from AD.Autoware.tools.utils import run_carla_with_docker

    args = IGArguments()
    run_carla_with_docker(version=CARLA_VERSION, offscreen=False)
    client, tm, world = executor.connect(args, 0)
    town_map_list = ["Town01", "Town02", "Town03", "Town04", "Town05", "Town10HD"]

    route_dir = Path(os.getcwd()) / "InputGeneration/Seed"

    for hd_map_name in town_map_list:
        print("=" * 15 + hd_map_name)
        road_graph = RoadGraph(client, hd_map_name)
        print(hd_map_name, "is parsed successfully!")
        route_dictionary = RouteDictionary(road_graph, route_dir)
        print(f"RouteDictionary of {hd_map_name} is generated successfully!")
