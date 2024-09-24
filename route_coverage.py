import os
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
    "00": "NORMAL",
    "01": "HIGH",
}

LABEL = [
    "Route Key",

    "Predecessor-Curvature",
    "Predecessor-Elevation",
    "Predecessor-SpeedLimit",
    "Predecessor-LaneNum",

    "Junction-Curvature",
    "Junction-ConnectedRoad",

    "Successor-Curvature",
    "Successor-Elevation",
    "Successor-SpeedLimit",
    "Successor-LaneNum"
    
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
                 ]

    str_list += [CURVATURE_STR[next_lane[:2]],
                 ELEVATION_STR[next_lane[2:4]],
                 SPEED_LIMIT[next_lane[4:5]],
                 next_lane[5:]]


if __name__ == '__main__':
    seed_path = Path("/home/dk-kling/Documents/Fuzz4AV/InputGeneration/Seed")
    town_list = os.listdir(seed_path)
    town_list.remove(".gitkeep")
    for town in town_list:
        print(f"{'=' * 10}{town}")
        town_path = seed_path / town
        route_dict = os.listdir(town_path)
        for route_key in route_dict:
            r_key_bin = "{0:b}".format(int(route_key, base=16)).zfill(24)
            col = [route_key] + to_str(r_key_bin) + [len(os.listdir(town_path / route_key))]

            print(f"{route_key}|{to_str(r_key_bin)}|{len(os.listdir(town_path / route_key))}")
            print()
