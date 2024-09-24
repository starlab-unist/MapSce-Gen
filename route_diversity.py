import os
import random
import numpy as np

from typing import List
from Utils.tools import set_environ
set_environ()


if __name__ == '__main__':
    from Utils import executor
    from Execution.sub_arguments import IGArguments

    from InputGeneration.RouteDictionary import RouteDictionary
    from InputGeneration.RoadGraph import RoadGraph

    from AD.Autoware.tools.constants import CARLA_VERSION
    from AD.Autoware.tools.utils import run_carla_with_docker

    args = IGArguments()
    run_carla_with_docker(version=CARLA_VERSION, offscreen=False)
    client, tm, world = executor.connect(args, 0)
    town_map_list = ["Town01", "Town02", "Town03", "Town04", "Town05", "Town10HD"]
    # town_map_list = ["Town01"]

    baseline_route_class = set()
    scenavro_route_class = set()

    for hd_map_name in town_map_list:
        random10_test_random = list()
        random10_test_baseline = list()
        random10_test_scenavro = list()
        print("=" * 15 + hd_map_name)

        rg_scenavro = RoadGraph(client, hd_map_name)
        rd_scenavro = RouteDictionary(rg_scenavro)
        rd_scenavro.extract_routes()

        all_driving_lane_num = 0
        for wr in list(rg_scenavro.whole_road.values()):
            all_driving_lane_num += wr.num_driving

        r_keys_scenavro = dict()
        l_keys = set()
        j_keys = set()

        scenavro_lane_coverage = 0
        scenavro_length_coverage = 0
        missing_lanes = 0

        for r_key in rd_scenavro.route_keys:
            r_keys_scenavro["{0:b}".format(int(r_key, base=16)).zfill(24)] = rd_scenavro.get_number(r_key)
            for route in rd_scenavro.route_dictionary[r_key]:
                missing_lanes += len(route.route) - 3
                l_keys |= route.covered
                j_keys |= route.j_key

                for lane in route.route:
                    if not rg_scenavro.whole_road[lane.road_id].lane_dict[lane.lane_id].coverage:
                        scenavro_lane_coverage += 1
                        scenavro_length_coverage += float(rg_scenavro.whole_road[lane.road_id].road_length)
                        rg_scenavro.whole_road[lane.road_id].lane_dict[lane.lane_id].coverage = True

        # scenavro_lane_coverage = 0
        # for wr in list(rg_scenavro.whole_road.values()):
        #     for pivot in list(wr.lane_dict.values):
        #         if pivot.lane_type == "driving" and pivot.coverage:
        #             scenavro_lane_coverage += 1

        rg_baseline = RoadGraph(client, hd_map_name)
        rd_baseline = RouteDictionary(rg_baseline)
        rd_baseline.extract_simple_routes()
        baseline_l_keys = set()

        r_keys_baseline = dict()

        baseline_lane_coverage = 0
        baseline_length_coverage = 0

        for r_key in rd_baseline.route_keys:
            r_keys_baseline["{0:b}".format(int(r_key, base=16)).zfill(24)] = rd_baseline.get_number(r_key)
            for route in rd_baseline.route_dictionary[r_key]:
                baseline_l_keys |= route.covered
                for lane in route.route:
                    if not rg_baseline.whole_road[lane.road_id].lane_dict[lane.lane_id].coverage and lane.lane_type == "driving":
                        baseline_lane_coverage += 1
                        baseline_length_coverage += float(rg_baseline.whole_road[lane.road_id].road_length)
                        rg_baseline.whole_road[lane.road_id].lane_dict[lane.lane_id].coverage = True

        rg_random = RoadGraph(client, hd_map_name)
        rd_random = RouteDictionary(rg_random)
        rd_random.extract_simple_routes()

        r_keys_random = dict()

        random_lane_coverage = 0
        random_length_coverage = 0

        for r_key in rd_random.route_keys:
            r_keys_random["{0:b}".format(int(r_key, base=16)).zfill(24)] = rd_random.get_number(r_key)
            for route in rd_random.route_dictionary[r_key]:
                for lane in route.route:
                    if not rg_random.whole_road[lane.road_id].lane_dict[lane.lane_id].coverage and lane.lane_type == "driving":
                        random_lane_coverage += 1
                        random_length_coverage += float(rg_random.whole_road[lane.road_id].road_length)
                        rg_random.whole_road[lane.road_id].lane_dict[lane.lane_id].coverage = True

        rd_random_final = list()
        for i in rd_random.route_dictionary.values():
            rd_random_final += i

        l_test_rnd = set()
        l_test_bsl = set()
        l_test_snv = set()

        j_test_rnd = set()
        j_test_bsl = set()
        j_test_snv = set()

        from pathlib import Path
        with (Path(f"/home/dk-kling/Documents/Fuzz4AV/out-artifact/100test/{hd_map_name}_100test.csv")).open('w') as f:
            f.write(
                "# of Scenario run,"
                
                # "#covered_random,"
                "RANDOM,"
                
                # "#covered_baseline,"
                "CROUTE,"
                
                # "#covered_scenavro,"
                "OURS"
                "\n"
            )

        overall = (len(l_keys) + len(j_keys))

        l_test_rnd = dict()
        l_test_bsl = dict()
        l_test_snv = dict()

        j_test_rnd = dict()
        j_test_bsl = dict()
        j_test_snv = dict()

        for i in range(100):

            l_test_rnd[i] = dict()
            l_test_bsl[i] = dict()
            l_test_snv[i] = dict()

            j_test_rnd[i] = dict()
            j_test_bsl[i] = dict()
            j_test_snv[i] = dict()

            scenavro_keys = list(rd_scenavro.route_dictionary.keys())
            index_list = list(range(len(scenavro_keys)))
            weights_list = list(np.ones(len(scenavro_keys)))

            for j in range(100):

                _key_baseline = random.choice(list(rd_baseline.route_dictionary.keys()))

                _index = random.choices(index_list, weights=weights_list)[0]
                _key_scenavro = scenavro_keys[_index]

                temp = set()
                temp.add(_key_scenavro[:2])
                temp.add(_key_scenavro[4:6])
                temp2 = _key_scenavro[2:4]

                for k in range(len(weights_list)):
                    if not scenavro_keys[k][:2] in temp and not scenavro_keys[k][4:6] in temp and not scenavro_keys[k][2:4] == temp2:
                        weights_list[k] += 0.2
                # _key_scenavro = random.choice(list(rd_scenavro.route_dictionary.keys()))

                rnd_route = random.choice(rd_random_final)
                bsl_route = random.choice(list(rd_baseline.route_dictionary[_key_baseline]))
                snv_route = random.choice(list(rd_scenavro.route_dictionary[_key_scenavro]))

                if j == 0:
                    l_test_rnd[i][j] = rnd_route.covered
                    l_test_bsl[i][j] = bsl_route.covered
                    l_test_snv[i][j] = snv_route.covered

                    j_test_rnd[i][j] = rnd_route.j_key
                    j_test_bsl[i][j] = bsl_route.j_key
                    j_test_snv[i][j] = snv_route.j_key

                else:
                    l_test_rnd[i][j] = l_test_rnd[i][j - 1] | rnd_route.covered
                    l_test_bsl[i][j] = l_test_bsl[i][j - 1] | bsl_route.covered
                    l_test_snv[i][j] = l_test_snv[i][j - 1] | snv_route.covered

                    j_test_rnd[i][j] = j_test_rnd[i][j - 1] | rnd_route.j_key
                    j_test_bsl[i][j] = j_test_bsl[i][j - 1] | bsl_route.j_key
                    j_test_snv[i][j] = j_test_snv[i][j - 1] | snv_route.j_key

            #     rnd_cover_sum = len(l_test_random) + len(j_test_random)
            #     bsl_cover_sum = len(l_test_baseline) + len(j_test_baseline)
            #     snv_cover_sum = len(l_test_scenavro) + len(j_test_scenavro)
            #
            # rnd_cover_mn = rnd_cover_sum / 100
            # bsl_cover_mn = bsl_cover_sum / 100
            # snv_cover_mn = snv_cover_sum / 100

        for j in range(100):
            rnd_cover_sum = 0
            bsl_cover_sum = 0
            snv_cover_sum = 0

            for i in range(100):
                rnd_cover_sum += len(l_test_rnd[i][j]) + len(j_test_rnd[i][j])
                bsl_cover_sum += len(l_test_bsl[i][j]) + len(j_test_bsl[i][j])
                snv_cover_sum += len(l_test_snv[i][j]) + len(j_test_snv[i][j])

            rnd_cover_mn = rnd_cover_sum / 100
            bsl_cover_mn = bsl_cover_sum / 100
            snv_cover_mn = snv_cover_sum / 100

            with (Path(f"/home/dk-kling/Documents/Fuzz4AV/out-artifact/100test/{hd_map_name}_100test.csv")).open('a') as f:
                f.write(
                    f"{j},"
                    
                    # f"{rnd_cover_mn},"
                    f"{rnd_cover_mn / overall},"
                    
                    # f"{bsl_cover_mn},"
                    f"{bsl_cover_mn / overall},"
                    
                    # f"{snv_cover_mn},"
                    f"{snv_cover_mn / overall}"
                    
                    f"\n"
                )

        # for i in range(100):
        #     test_random = set()
        #     test_baseline = set()
        #     test_scenavro = set()
        #     for j in range(len(l_keys)):
        #         _key_baseline = random.choice(list(rd_baseline.route_dictionary.keys()))
        #         _key_scenavro = random.choice(list(rd_scenavro.route_dictionary.keys()))
        #         test_random = test_random | random.choice(rd_random_final).covered
        #         test_baseline = test_baseline | random.choice(list(rd_baseline.route_dictionary[_key_baseline])).covered
        #         test_scenavro = test_scenavro | random.choice(list(rd_scenavro.route_dictionary[_key_scenavro])).covered
        #         print(f"TRY: {j}")
        #         print(f"Baseline Lane Coverage: {len(test_baseline)} / {len(l_keys)} "
        #               f"({100 * len(test_baseline) / len(l_keys)}%)")
        #         print(f"ScenaVRo Lane Coverage: {len(test_scenavro)} / {len(l_keys)} "
        #               f"({100 * len(test_scenavro) / len(l_keys)}%)\n")

        #     random10_test_random.append(len(test_random))
        #     random10_test_baseline.append(len(test_baseline))
        #     random10_test_scenavro.append(len(test_scenavro))
        # r_re = sum(random10_test_random) / len(random10_test_random)
        # b_re = sum(random10_test_baseline) / len(random10_test_baseline)
        # s_re = sum(random10_test_scenavro) / len(random10_test_scenavro)

        # print(f"{r_re} ({r_re / len(l_keys) * 100}%)")
        # print(f"{b_re} ({b_re / len(l_keys) * 100}%)")
        # print(f"{s_re} ({s_re / len(l_keys) * 100}%)")
        # print()

        # print(l_keys)
        # print(baseline_l_keys)

        # s_lanes = set()
        # j_lanes = set()
        # # for key in list(rd_scenavro.route_dictionary.keys()):
        #     # s_lanes.add(key[:2])
        #     # j_lanes.add(key[2:4])
        #     # s_lanes.add(key[4:])
        #
        # print(s_lanes)
        #
        # s_lanes = set()
        # j_lanes = set()
        # # for key in list(rd_baseline.route_dictionary.keys()):
        #     # s_lanes.add(key[:2])
        #     # j_lanes.add(key[2:4])
        #     # s_lanes.add(key[4:])
        #
        # print(s_lanes)

        # print("Not Covered Lanes in Baseline")
        # for road in list(rg_baseline.whole_road.values()):
        #     for lane in list(road.lane_dict.values()):
        #         if not rg_baseline.whole_road[lane.road_id].lane_dict[lane.lane_id].coverage and lane.lane_type == "driving":
        #             print(f"[\"{lane.road_id}\", \"{lane.lane_id}\"],")
        # print()

        # for i in range(10):
        #     test_random = set()
        #     test_baseline = set()
        #     test_scenavro = set()
        #     for j in range(int(all_driving_lane_num / 5)):
        #         _key_baseline = random.choice(list(rd_baseline.route_dictionary.keys()))
        #         _key_scenavro = random.choice(list(rd_scenavro.route_dictionary.keys()))
        #         test_random = test_random | set(random.choice(rd_random_final).route)
        #         test_baseline = test_baseline | set(random.choice(list(rd_baseline.route_dictionary[_key_baseline])).route)
        #         test_scenavro = test_scenavro | set(random.choice(list(rd_scenavro.route_dictionary[_key_scenavro])).route)
        #
        #     print(f"Baseline Lane Coverage: {len(test_baseline)} / {all_driving_lane_num} "
        #           f"({100 * len(test_baseline) / all_driving_lane_num}%)")
        #     print(f"ScenaVRo Lane Coverage: {len(test_scenavro)} / {all_driving_lane_num} "
        #           f"({100 * len(test_scenavro) / all_driving_lane_num}%)\n")
        #
        #     random10_test_random.append(len(test_random))
        #     random10_test_baseline.append(len(test_baseline))
        #     random10_test_scenavro.append(len(test_scenavro))
        # r_re = sum(random10_test_random) / len(random10_test_random)
        # b_re = sum(random10_test_baseline) / len(random10_test_baseline)
        # s_re = sum(random10_test_scenavro) / len(random10_test_scenavro)
        #
        # print(f"{r_re} ({r_re / all_driving_lane_num * 100}%)")
        # print(f"{b_re} ({b_re / all_driving_lane_num * 100}%)")
        # print(f"{s_re} ({s_re / all_driving_lane_num * 100}%)")
        # print()

    #     print(f"Baseline Lane Coverage: {baseline_lane_coverage} / {all_driving_lane_num} "
    #           f"({100 * baseline_lane_coverage / all_driving_lane_num}%)")
    #     print(f"ScenaVRo Lane Coverage: {scenavro_lane_coverage} / {all_driving_lane_num} "
    #           f"({100 * scenavro_lane_coverage / all_driving_lane_num}%)\n")
    #
    #     print(f"Baseline Length Coverage: {baseline_length_coverage} / {scenavro_length_coverage} "
    #           f"({100 * baseline_length_coverage / scenavro_length_coverage}%)")
    #     print(f"ScenaVRo Length Coverage: {scenavro_length_coverage} / {scenavro_length_coverage} "
    #           f"({100}%)\n")
    #
    #     print(f"Baseline Lost Lane Distance: {scenavro_length_coverage - baseline_length_coverage}m")
    #     print(f"ScenaVRo Lost Lane Distance: {0}m\n")
    #
    #     print(f"Baseline Number of Route Class: {len(rd_baseline.route_dictionary.keys())}")
    #     print(f"ScenaVRo Number of Route Class: {len(rd_scenavro.route_dictionary.keys())}\n")
    #
    #     print(f"Baseline Number of Missing Lane: {missing_lanes}\n")
    #
    #     baseline_route_class = baseline_route_class | rd_baseline.route_dictionary.keys()
    #     scenavro_route_class = scenavro_route_class | rd_scenavro.route_dictionary.keys()
    #     print()
    #
    #
    # print("=" * 15 + "Total")
    # print(f"Baseline Number of Route Class: {len(baseline_route_class)}")
    # print(f"ScenaVRo Number of Route Class: {len(scenavro_route_class)}\n")
    #
