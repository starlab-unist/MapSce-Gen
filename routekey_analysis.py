import os
import csv
import json
from pathlib import Path


CURVATURE_STR = {
    "00": "STRAIGHT",
    "01": "LEFT_CURVATURE",
    "10": "RIGHT_CURVATURE",
    "11": "COMPLEX_CURVATURE",
}

ELEVATION_STR = {
    "00": "FLAT",
    "01": "DOWNHILL",
    "10": "UPHILL",
    "11": "COMPLEX_HILL",
}

SPEED_LIMIT = {
    "0": "NORMAL",
    "1": "HIGH",
}

LABEL = [
    "Route-Key",
    "Predecessor-Curvature",
    "Predecessor-Elevation",
    "Predecessor-SpeedLimit",
    "Predecessor-LaneNum",

    "Junction-Curvature",
    "Junction-ConnectedRoad",

    "Successor-Curvature",
    "Successor-Elevation",
    "Successor-SpeedLimit",
    "Successor-LaneNum",

    "NumberOfLanes"
]


def to_str(route_key_bin):
    str_list = list()
    prev_lane = route_key_bin[:8]
    junction_lane = route_key_bin[8:16]
    next_lane = route_key_bin[16:]
    str_list += [CURVATURE_STR[prev_lane[:2]],
                 ELEVATION_STR[prev_lane[2:4]],
                 SPEED_LIMIT[prev_lane[4:5]],
                 prev_lane[5:]]
    str_list += [CURVATURE_STR[junction_lane[2:4]],
                 junction_lane[5:]
                 ]
    str_list += [CURVATURE_STR[next_lane[:2]],
                 ELEVATION_STR[next_lane[2:4]],
                 SPEED_LIMIT[next_lane[4:5]],
                 next_lane[5:]]

    return str_list


if __name__ == '__main__':
    seed_path = Path("/home/dk-kling/Documents/Fuzz4AV/InputGeneration/RouteDictionary")
    route_dict = os.listdir(seed_path)
    if ".gitkeep" in route_dict:
        route_dict.remove(".gitkeep")
    for route_key in route_dict:
        r_key_bin = "{0:b}".format(int(route_key, base=16)).zfill(24)
        # print(to_str(r_key_bin)[0])
        if to_str(r_key_bin)[0] == "LEFT_CURVATURE":
            print(route_key)

