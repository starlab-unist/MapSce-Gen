import os.path

import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw


class DtwEvaluator:
    """
    Calculate DTW using fastdtw
    XXXX
    """
    def __init__(self, csv_path_list):
        self.np_data_dict = dict()
        for csv_path in csv_path_list:
            loc_list = list()
            measurements = pd.read_csv(csv_path / "logs" / "measurements.csv")
            for frame in measurements.itertuples():
                if (frame.x == "NONE" or frame.x is None) or (frame.y == "NONE" or frame.y is None):
                    continue
                loc_list.append([frame.x, frame.y])
            self.np_data_dict[os.path.basename(csv_path)] = (np.array(loc_list))

    def print_difference(self):
        for model in list(self.np_data_dict.keys()):
            criteria = self.np_data_dict.pop(model)

            for t_model in list(self.np_data_dict.keys()):
                target = self.np_data_dict[t_model]
                distance, path = fastdtw(criteria, target, dist=euclidean)
                length = str(abs(len(target) - len(criteria)))

                print(f"[Criteria Model] {model}")
                print(f"[Target Model] {t_model}")
                print(f"DTW Distance: {distance}")
                print(f"Length Difference: {length}\n")
