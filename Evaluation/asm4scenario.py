import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import json
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from typing import Tuple, List
from shapely.geometry import Polygon, LineString
from shapely.ops import nearest_points
from pathlib import Path
from log_util import get_logger

MODELS = [
    "vehicle.lincoln.mkz2020",  # "Standard"
    "vehicle.audi.a2",  # "Compact"
    "vehicle.audi.etron",  # "SUV"
    "vehicle.volkswagen.t2",  # "Van"
    "vehicle.carlamotors.carlacola"  # "Truck"
]

START = 0
END = -1
CONTINUE = 100

LANE_FOLLOW = 10

LANE_CHANGE = 20
LANE_CHANGE_LEFT = 21
LANE_CHANGE_RIGHT = 22

JUNCTION_CROSS = 30
JUNCTION_CROSS_LEFT = 31
JUNCTION_CROSS_RIGHT = 32

SLOW_DOWN = 40
SLOW_DOWN_BY_PEDESTRIAN = 41
SLOW_DOWN_BY_VEHICLE = 42
SLOW_DOWN_BY_TRAFFIC_SIGN = 43

STOPPED = 50
STOPPED_BY_PEDESTRIAN = 51
STOPPED_BY_VEHICLE = 52
STOPPED_BY_TRAFFIC_SIGN = 53

COLLIDE_WITH_VEHICLE = 61
COLLIDE_WITH_PEDESTRIAN = 62

PERCEPTION_AREA_LENGTH = 3
PERCEPTION_AREA_WIDTH = 5
JUNCTION_CHECK_LENGTH = 10

SEQUENCE_STR = {
    START: "START",
    END: "END",

    LANE_FOLLOW: "FOLLOWING_LANE",

    LANE_CHANGE: "LANE_CHANGE",
    LANE_CHANGE_LEFT: "LANE_CHANGE_LEFT",
    LANE_CHANGE_RIGHT: "LANE_CHANGE_RIGHT",

    JUNCTION_CROSS: "CROSS_JUNCTION",
    JUNCTION_CROSS_LEFT: "CROSS_JUNCTION_LEFT",
    JUNCTION_CROSS_RIGHT: "CROSS_JUNCTION_RIGHT",

    SLOW_DOWN: "SLOW_DOWN",
    SLOW_DOWN_BY_PEDESTRIAN: "SLOW_DOWN_BY_PEDESTRIAN",
    SLOW_DOWN_BY_VEHICLE: "SLOW_DOWN_BY_VEHICLE",
    SLOW_DOWN_BY_TRAFFIC_SIGN: "SLOW_DOWN_BY_TRAFFIC_SIGN",

    STOPPED: "STOPPED",
    STOPPED_BY_PEDESTRIAN: "STOPPED_BY_PEDESTRIAN",
    STOPPED_BY_VEHICLE: "STOPPED_BY_VEHICLE",
    STOPPED_BY_TRAFFIC_SIGN: "STOPPED_BY_TRAFFIC_SIGN",

    COLLIDE_WITH_VEHICLE: "COLLIDE_WITH_VEHICLE",
    COLLIDE_WITH_PEDESTRIAN: "COLLIDE_WITH_PEDESTRIAN",
}

default_obstacle_analysis_element = {
            "perception pedestrian": False,
            "perception vehicle": False,
            "collision pedestrian": False,
            "collision vehicle": False,
            "is going to paint": list()
}


# Convert Euler angle to directional vector (z-axis)
# Get the exact coordinate of point of the boundary box.
def get_bb(x:float, y:float, yaw:float, extent_x:float, extent_y:float) -> Polygon:
    """
    Convert Euler angle to directional vector (z-axis) and get the exact
    coordinate of point of the boundary box.

    Args:
        x (float): The x coordinate of middle point of ego car.
        y (float): The y coordinate of middle point of ego car.
        yaw (float): How much does the ego car turn in z-axis?
        extent_x (float): Width of ego car.
        extent_y (float): Length of ego car.

    Returns:
        Polygon: Return the coordinates of four points of ego-vehicle boundary box.
    """
    yaw = math.radians(yaw)

    bb = Polygon([
        (x + extent_x * math.cos(yaw) - extent_y * math.sin(yaw),
         y + extent_x * math.sin(yaw) + extent_y * math.cos(yaw)),
        (x - extent_x * math.cos(yaw) - extent_y * math.sin(yaw),
         y - extent_x * math.sin(yaw) + extent_y * math.cos(yaw)),
        (x - extent_x * math.cos(yaw) + extent_y * math.sin(yaw),
         y - extent_x * math.sin(yaw) - extent_y * math.cos(yaw)),
        (x + extent_x * math.cos(yaw) + extent_y * math.sin(yaw),
         y + extent_x * math.sin(yaw) - extent_y * math.cos(yaw))
        ])
    return bb

def get_ego_bb(x:float, y:float, yaw:float, extent_x:float, extent_y:float) -> Tuple[Polygon, Polygon, Polygon]:
    """
    Get the area of collision (if any obstacles get in this area, then it would be considered as 'collision') and
    the area of perception (ego car would be acknowledged obstacles that is in this certain size of area).

    Args:
        x (float): The x coordinate of middle point of ego car.
        y (float): The y coordinate of middle point of ego car.
        yaw (float): How much does the ego car turn in z-axis?
        extent_x (float): Width of ego car.
        extent_y (float): Length of ego car.

    Returns:
        tuple of (Polygon, Polygon, Polygon): Return all the boundary box coordinates for each section.
                                              Ego car box itself, range for collision, range for perception.
    """
    raw_yaw = yaw
    yaw = math.radians(float(yaw))

    cb_x = x + (extent_x - 1) * math.cos(yaw)
    cb_y = y + (extent_x - 1) * math.sin(yaw)
    pb_x = x + (extent_x + PERCEPTION_AREA_WIDTH) * math.cos(yaw)
    pb_y = y + (extent_x + PERCEPTION_AREA_WIDTH) * math.sin(yaw)

    ego_bb = get_bb(x, y, raw_yaw, extent_x, extent_y)

    collision_bb = Polygon([
        (cb_x + 1.2 * math.cos(yaw) - (extent_y + 0.2) * math.sin(yaw),
         cb_y + 1.2 * math.sin(yaw) + (extent_y + 0.2) * math.cos(yaw)),
        (cb_x - 1.2 * math.cos(yaw) - (extent_y + 0.2) * math.sin(yaw),
         cb_y - 1.2 * math.sin(yaw) + (extent_y + 0.2) * math.cos(yaw)),
        (cb_x - 1.2 * math.cos(yaw) + (extent_y + 0.2) * math.sin(yaw),
         cb_y - 1.2 * math.sin(yaw) - (extent_y + 0.2) * math.cos(yaw)),
        (cb_x + 1.2 * math.cos(yaw) + (extent_y + 0.2) * math.sin(yaw),
         cb_y + 1.2 * math.sin(yaw) - (extent_y + 0.2) * math.cos(yaw))
    ])

    perception_bb = Polygon([
        (pb_x + PERCEPTION_AREA_WIDTH * math.cos(yaw) - (extent_y + PERCEPTION_AREA_LENGTH) * math.sin(yaw),
         pb_y + PERCEPTION_AREA_WIDTH * math.sin(yaw) + (extent_y + PERCEPTION_AREA_LENGTH) * math.cos(yaw)),
        (pb_x - PERCEPTION_AREA_WIDTH * math.cos(yaw) - (extent_y + PERCEPTION_AREA_LENGTH) * math.sin(yaw),
         pb_y - PERCEPTION_AREA_WIDTH * math.sin(yaw) + (extent_y + PERCEPTION_AREA_LENGTH) * math.cos(yaw)),
        (pb_x - PERCEPTION_AREA_WIDTH * math.cos(yaw) + (extent_y + PERCEPTION_AREA_LENGTH) * math.sin(yaw),
         pb_y - PERCEPTION_AREA_WIDTH * math.sin(yaw) - (extent_y + PERCEPTION_AREA_LENGTH) * math.cos(yaw)),
        (pb_x + PERCEPTION_AREA_WIDTH * math.cos(yaw) + (extent_y + PERCEPTION_AREA_LENGTH) * math.sin(yaw),
         pb_y + PERCEPTION_AREA_WIDTH * math.sin(yaw) - (extent_y + PERCEPTION_AREA_LENGTH) * math.cos(yaw))
    ])

    return ego_bb, collision_bb, perception_bb


def get_shortest_length_between(a:Polygon, b:Polygon) -> float:
    return LineString(nearest_points(a, b)).length


class ASM4Scenario:
    def __init__(self, _log_path, **kwargs):

        _scenario_path = _log_path / "scenario.json"
        _csv_path = _log_path / "measurements.csv"

        from Utils.ComplexScenario import ComplexScenario
        self.scenario = ComplexScenario(_scenario_path)
        self.vehicles = self.scenario.npc['vehicles']
        self.pedestrians = self.scenario.npc['pedestrians']

        # Ego-vehicle model
        self.ego_vehicle_model = kwargs.get("ego_vehicle_model", "vehicle.tesla.model3")

        self.obstacle_analysis_result = list()

        self.b_seq = list()
        self.frames = list()
        self.driving_state = self.DrivingState()

        self.measurements = pd.read_csv(_csv_path)
        #self.measurements = pd.DataFrame()
        
        self.save_path = kwargs.get("save_path", ".")

        self.reasonable_vehicles = set()
        self.reasonable_pedestrians = set()

        self._load_csv(_csv_path)
        self.x_max = self.measurements["x"].max()
        self.x_min = self.measurements["x"].min()
        self.y_max = self.measurements["y"].max()
        self.y_min = self.measurements["y"].min()

    def get_str_sequence(self):
        str_seq = list()
        for e in self.b_seq:
            str_seq.append(SEQUENCE_STR[e])
        return str_seq

    def analyze(self):
        self.analyze_obstacles() # Check collison/perception of eco vehicle.
        # get_logger("Analyzer").info("Analysis starts.")
        count = 0
        for frame in self.measurements.itertuples():

            ############################################################
            # Initialize
            ############################################################

            if count < 3:
                count += 1
                # get_logger("Analyzer").debug(f"{frame[0]} : {count} is not same or bigger than 3.")
                continue

            elif self.driving_state.current == START:
                # get_logger("Analyzer").debug(f"{frame[0]} : " + str(self.driving_state))
                # get_logger("Analyzer").info(f"{frame[0]} : START state checked.")
                """
                START State
                
                +++ STORE START
                + road_id, lane_id
                -> LANE_FOLLOW
                """
                self.b_seq.append(START)
                self.frames.append(frame.frame) # frame number
                # if self.om.road_graph.
                self.driving_state.current = LANE_FOLLOW
                self.driving_state.road_id = frame.road_id
                self.driving_state.lane_id = frame.lane_id
                
                # get_logger("Analyzer").info(f"{frame[0]} : START -> LANE_FOLLOW")

            ############################################################
            # Collision Checking
            ############################################################
            if self.obstacle_analysis_result[frame.frame]["collision vehicle"]: # Are there any collisions?
                if not self.driving_state.collision and int(self.b_seq[-1] / 10) != 6: # 60th code(collision)
                    # get_logger("Analyzer").info(f"{frame[0]} : COLLIDE WITH VEHICLE checked.")
                    self.b_seq.append(COLLIDE_WITH_VEHICLE)
                    self.driving_state.collision = True
                    self.frames.append(frame.frame)
            elif self.obstacle_analysis_result[frame.frame]["collision pedestrian"]:
                if not self.driving_state.collision and int(self.b_seq[-1] / 10) != 6:
                    # get_logger("Analyzer").info(f"{frame[0]} : COLLIDE WITH PEDESTRIAN checked.")
                    self.b_seq.append(COLLIDE_WITH_PEDESTRIAN)
                    self.driving_state.collision = True
                    self.frames.append(frame.frame)
            else:
                self.driving_state.collision = False
            ############################################################
            # Area Checking
            ############################################################

            if (type(frame.is_junction) is bool and frame.is_junction) or \
                    (type(frame.is_junction) is str and (frame.is_junction == "True" or frame.is_junction == "NONE")):
                self.driving_state.junction_steers.append(frame.steer)
                if not self.driving_state.is_junction:
                    """
                    Check junction
                    
                    + road_id, lane_id, is_junction
                    -> CROSS_JUNCTION
                    """
                    # get_logger("Analyzer").info(f"{frame[0]} : JUNCTION CROSS checked.")
                    self.driving_state.current = JUNCTION_CROSS
                    self.driving_state.road_id = frame.road_id
                    self.driving_state.lane_id = frame.lane_id
                    self.driving_state.is_junction = True

            elif frame.road_id != self.driving_state.road_id:
                """
                Check Road
                    
                + is_junction
                + road_id, lane_id, is_junction
                -> FOLLOWING_LANE
                """
                self.driving_state.current = LANE_FOLLOW
                self.driving_state.road_id = frame.road_id
                self.driving_state.lane_id = frame.lane_id
                if self.driving_state.is_junction:
                    self.driving_state.is_junction = False

            elif frame.lane_id != self.driving_state.lane_id:
                """
                Check lane
                
                + road_id, lane_id
                -> LANE_CHANGE
                
                LANE_CHANGE State
                
                Analyze lane
                    > LEFT or RIGHT
                +++ STORE LANE_CHANGE
                """
                try:
                    if abs(frame.lane_id) > abs(self.driving_state.lane_id):
                        self.b_seq.append(LANE_CHANGE_RIGHT)
                    else:
                        self.b_seq.append(LANE_CHANGE_LEFT)
                except:
                    self.b_seq.append(LANE_CHANGE)
                finally:
                    self.frames.append(frame.frame)

                self.driving_state.current = CONTINUE
                self.driving_state.road_id = frame.road_id
                self.driving_state.lane_id = frame.lane_id

            ############################################################
            # Update State related to Area
            ############################################################

            if self.driving_state.current == JUNCTION_CROSS:
                """
                CROSS_JUNCTION State
                
                +++ STORE CROSS_JUNCTION
                """
                self.b_seq.append(JUNCTION_CROSS)
                self.frames.append(frame.frame)
                self.driving_state.current = CONTINUE

            elif self.driving_state.current == LANE_FOLLOW:
                """
                FOLLOWING_LANE State

                Analyze road type
                    > NARROW or WIDE
                    > NORMAL or LONG or HIGHWAY
                
                if ego passed junction?
                Analyze Control::Steer
                    > STRAIGHT or LEFT or RIGHT
                """
                temp_state = LANE_FOLLOW
                try:
                    road = self.rg.road_dict[str(self.driving_state.road_id)]
                    if len(road.child) < 7:
                        temp_state += 1
                    else:
                        temp_state += 2
                    if road.length > 400:
                        temp_state += 4
                    elif road.length > 150:
                        temp_state += 2
                    self.b_seq.append(temp_state)
                except:
                    self.b_seq.append(LANE_FOLLOW)
                finally:
                    self.frames.append(frame.frame)

                if self.driving_state.junction_steers:
                    steer_mean = np.mean(self.driving_state.junction_steers)
                    if JUNCTION_CROSS in self.b_seq:
                        i = self.b_seq.index(JUNCTION_CROSS)
                        if steer_mean > 0.1:
                            self.b_seq[i] = JUNCTION_CROSS_RIGHT
                        elif steer_mean < -0.1:
                            self.b_seq[i] = JUNCTION_CROSS_LEFT
                        else:
                            self.b_seq[i] = JUNCTION_CROSS

                self.driving_state.current = CONTINUE

            ############################################################
            # Control Checking
            ############################################################

            if frame.brake > 0 and not self.driving_state.decelerate:
                """
                Check decelerate
                
                + decelerate, velocity
                -> SLOW_DOWN
                """
                self.driving_state.decelerate = True
                self.driving_state.velocity = frame.velocity
                p_dist = None
                v_dist = None
                if self.obstacle_analysis_result[frame.frame]["perception pedestrian"]:
                    p_dist = self.obstacle_analysis_result[frame.frame]["perception pedestrian"][0]
                if self.obstacle_analysis_result[frame.frame]["perception vehicle"]:
                    v_dist = self.obstacle_analysis_result[frame.frame]["perception vehicle"][0]
                if p_dist is None:
                    if v_dist is None:
                        self.b_seq.append(SLOW_DOWN)
                    else:
                        self.b_seq.append(SLOW_DOWN_BY_VEHICLE)
                else:
                    if v_dist is None:
                        self.b_seq.append(SLOW_DOWN_BY_PEDESTRIAN)
                    else:
                        if p_dist < v_dist:
                            self.b_seq.append(SLOW_DOWN_BY_PEDESTRIAN)
                        else:
                            self.b_seq.append(SLOW_DOWN_BY_VEHICLE)

                self.frames.append(frame.frame)
                self.driving_state.current = CONTINUE

            if self.driving_state.decelerate:
                if frame.velocity < 0.2 and int(self.b_seq[-1] / 10) != 5:
                    """
                    -> STOPPED State
                    """
                    self.driving_state.current = STOPPED

                elif frame.velocity < self.driving_state.velocity - 5:
                    """
                    + Store velocity
                    """
                    self.driving_state.velocity = frame.velocity
                    # TEMP
                    self.b_seq.append(SLOW_DOWN)
                    self.frames.append(frame.frame)

                elif frame.velocity > self.driving_state.velocity + 5:
                    """
                    + Store velocity
                    -> FOLLOWING_LANE State
                    """
                    self.driving_state.velocity = frame.velocity
                    self.driving_state.decelerate = False
                    # TEMP
                    self.driving_state.current = LANE_FOLLOW

            ############################################################
            # Update State related to Control
            ############################################################

            if self.driving_state.current == STOPPED:
                """
                STOPPED State
                
                Analyze reason
                    > PEDESTRIAN or VEHICLE or TRAFFIC_SIGN
                """
                p_dist = None
                v_dist = None
                if self.obstacle_analysis_result[frame.frame]["perception pedestrian"]:
                    p_dist = self.obstacle_analysis_result[frame.frame]["perception pedestrian"][0]
                if self.obstacle_analysis_result[frame.frame]["perception vehicle"]:
                    v_dist = self.obstacle_analysis_result[frame.frame]["perception vehicle"][0]
                if p_dist is None:
                    if v_dist is None:
                        self.b_seq.append(STOPPED)
                    else:
                        self.b_seq.append(STOPPED_BY_VEHICLE)
                else:
                    if v_dist is None:
                        self.b_seq.append(STOPPED_BY_PEDESTRIAN)
                    else:
                        if p_dist < v_dist:
                            self.b_seq.append(STOPPED_BY_PEDESTRIAN)
                        else:
                            self.b_seq.append(STOPPED_BY_VEHICLE)

                self.frames.append(frame.frame)
                self.driving_state.current = CONTINUE

            count += 1
        if JUNCTION_CROSS in self.b_seq:
            self.handle_cross_junction()

        self.b_seq.append(END)
        self.frames.append(frame.frame)
        print(self.get_str_sequence())
        self._save_scenario_str()
        self.draw_box_sequence()

    def handle_cross_junction(self):
        steer_mean = np.mean(self.driving_state.junction_steers)
        i = self.b_seq.index(JUNCTION_CROSS)
        if steer_mean > 0.1:
            self.b_seq[i] = JUNCTION_CROSS_RIGHT
        elif steer_mean < -0.1:
            self.b_seq[i] = JUNCTION_CROSS_LEFT
        else:
            self.b_seq[i] = JUNCTION_CROSS

    def save_reasonable_p(self, _path):
        print(f"The Number of Reasonable Pedestrian: {self.reasonable_pedestrians}")
        with (_path / 'oba.json').open('w') as f:
            json.dump(list(self.reasonable_pedestrians), f)
        return len(list(self.reasonable_pedestrians))

    def get_npcs(self):
        iterator = 12
        for i in range(len(self.measurements.columns) - 11):
            print(self.measurements.columns[iterator])
            iterator += 1

    def analyze_obstacles(self):
        scenario_area = self.get_scenario_area()

        for frame in self.measurements.itertuples(name=None):
            element = {
                "perception pedestrian": list(),
                "perception vehicle": list(),
                "collision pedestrian": False,
                "collision vehicle": False,
                "is going to paint": list()
            }
            element["is going to paint"].append((scenario_area, "black"))
            tesla_x = 2.3958897590637207
            tesla_y = 1.081725001335144
            ego_bb, collision_bb, perception_bb = get_ego_bb(frame[2], frame[3], frame[4], tesla_x, tesla_y)
            element["is going to paint"].append((ego_bb, "#478FFF"))
            element["is going to paint"].append((collision_bb, "#CC1818"))
            element["is going to paint"].append((perception_bb, "#ECA414"))

            vehicle_bbs, pedestrian_bbs = self.get_npc_bbs(frame)
            
            # get_logger().info(f"{len(vehicle_bbs)} of vehicle polygones and {len(pedestrian_bbs)} of pedestrian polygones are generated.")

            idx = 0
            for v_bb in vehicle_bbs: # Check violation for each vehicle.
                if v_bb is None:
                    continue

                if not v_bb.disjoint(collision_bb): # Did ego car collide with NPC vehicle?
                    element["is going to paint"].append((v_bb, "#236D3A"))
                    if not element["collision vehicle"]:
                        element["collision vehicle"] = True
                        self.reasonable_vehicles.add(idx)

                elif not v_bb.disjoint(perception_bb): # Did ego car recognize NPC vehicle?
                    element["is going to paint"].append((v_bb, "#236D3A"))
                    dist = get_shortest_length_between(v_bb, perception_bb)
                    # Then, store the distance between them.
                    if not element["perception vehicle"]:
                        element["perception vehicle"].append(dist)
                    elif element["perception vehicle"][0] < dist:
                        element["perception vehicle"][0] = dist
                    self.reasonable_vehicles.add(idx)

                elif not v_bb.disjoint(scenario_area): # Did ego car get out of the map area?
                    element["is going to paint"].append((v_bb, "#236D3A"))

                idx += 1

            idx = 0
            for p_bb in pedestrian_bbs:
                if p_bb is None:
                    continue

                if not p_bb.disjoint(collision_bb): # Did ego car collide with NPC pedestrian?
                    element["is going to paint"].append((p_bb, "#9900BF"))
                    if not element["collision pedestrian"]:
                        element["collision pedestrian"] = True
                        self.reasonable_pedestrians.add(idx)

                elif not p_bb.disjoint(perception_bb): # Did ego car recognize NPC pedestrian?
                    element["is going to paint"].append((p_bb, "#9900BF"))
                    dist = get_shortest_length_between(p_bb, perception_bb)
                    if not element["perception pedestrian"]:
                        element["perception pedestrian"].append(dist)
                    elif element["perception pedestrian"][0] < dist:
                        element["perception pedestrian"][0] = dist
                    self.reasonable_pedestrians.add(idx)

                elif not p_bb.disjoint(scenario_area):
                    element["is going to paint"].append((p_bb, "#9900BF"))

                idx += 1

            self.obstacle_analysis_result.append(element)

    def draw_box_sequence(self):
        # Picture Size
        X = np.array([self.x_min - 20, self.x_max + 20])
        Y = np.array([self.y_min - 20, self.y_max + 20])
        idx = 0
        frame_stack = 0

        for frame in self.measurements.itertuples(name=None):
            if frame[1] in self.frames or frame_stack > 50:
                frame_stack = 0
                fig, ax = plt.subplots()
                plt.plot(X, Y, color="None")
                plt.gca().invert_yaxis()

                polys = self.obstacle_analysis_result[idx]["is going to paint"]
                for poly in polys:
                    x, y = poly[0].exterior.xy
                    ax.plot(x, y, color=poly[1])
                plt.axis('scaled')
                plt.savefig(self.save_path + "/picture" + str(frame[1]) + ".png")

            idx += 1
            frame_stack += 1

    def get_npc_bbs(self, frame):
        vehicle_bbs = list()
        pedestrian_bbs = list()
        index = 13
        for i in range(len(self.vehicles)):
            try:
                bb:Polygon = get_bb(frame[index], frame[index + 1], frame[index + 2],
                            self.vehicles[i]["extent_x"], self.vehicles[i]["extent_y"])
                vehicle_bbs.append(bb)
            except:
                vehicle_bbs.append(None)
            finally:
                index += 3

        for i in range(len(self.pedestrians)):
            try:
                bb:Polygon = get_bb(frame[index], frame[index + 1], frame[index + 2],
                            self.pedestrians[i]["extent_x"], self.pedestrians[i]["extent_y"])
                pedestrian_bbs.append(bb)
            except:
                pedestrian_bbs.append(None)
            finally:
                index += 3
        return vehicle_bbs, pedestrian_bbs

    def get_scenario_area(self):
        pic_map = Polygon([
            (self.x_min - 10, self.y_min - 10),
            (self.x_min - 10, self.y_max + 10),
            (self.x_max + 10, self.y_max + 10),
            (self.x_max + 10, self.y_min - 10),
        ])

        return pic_map

    class DrivingState:
        def __init__(self):
            self.current = START
            self.road_id = None
            self.lane_id = None
            self.is_junction = False
            self.decelerate = False
            self.velocity = None
            self.junction_steers = list()
            self.lane_diff = 0
            self.collision = False
            
        def __str__(self):
            return f"{SEQUENCE_STR[self.current]}====\n\t\t\t\t\t\t\t(rid: {self.road_id}, lid: {self.lane_id}, juc: {self.is_junction})(dec: {self.decelerate}, speed: {self.velocity})\n\t\t\t\t\t\t\tCOLLISION? : {self.collision}"

    def _load_csv(self, _csv_path):
        measurements = pd.read_csv(_csv_path)
        self.measurements = measurements

    def _save_scenario_str(self):
        data = list()
        idx = 0
        # print(self.frames)
        # print(self.b_seq)
        for i in self.frames:
            data.append((i, SEQUENCE_STR[self.b_seq[idx]]))
            idx += 1
        with open(self.save_path + "/abstract_scenario.json", 'a') as f_out:
            json.dump(data, f_out)


if __name__ == '__main__':
    # get_logger("ASM_MAIN").info("Initialize")
    from Utils.tools import set_environ
    set_environ()
    
    # get_logger("ASM_MAIN").debug("Set Evironment")

    path_list = list()
    base_path = Path("/home/dk-kling/Documents/Fuzz4AV/out-artifact/PTEST_Town10HD")
    asm_path = Path(base_path / "ASM")
    max_cycle_num = 18
    r_gp = 0
    r_lp = 0
    r_xp = 0
    for cycle_num in range(max_cycle_num):
        print(f"{'=' * 10} Cycle {cycle_num + 1}")
        re_path = asm_path / f"cycle_{cycle_num + 1}"
        if not re_path.exists():
            os.mkdir(re_path)

        re_path = re_path / "gp_scenario"
        os.mkdir(re_path)
        log_path = base_path / f"cycle_{cycle_num + 1}" / "round_1" / "vehicle.tesla.model3" / "logs" / "gp_scenario"
        asm4s = ASM4Scenario(log_path,
                             save_path=str(re_path),
                             ego_vehicle_model="vehicle.tesla.model3")
        state = json.load((log_path / "state.json").open())
        asm4s.analyze()
        r_gp += asm4s.save_reasonable_p(re_path)
        if state["result"]["collision_with"]:
            print("COLLISION")

        re_path = asm_path / f"cycle_{cycle_num + 1}"
        re_path = re_path / "lp_scenario"
        os.mkdir(re_path)
        log_path = base_path / f"cycle_{cycle_num + 1}" / "round_1" / "vehicle.tesla.model3" / "logs" / "lp_scenario"
        asm4s = ASM4Scenario(log_path,
                             save_path=str(re_path),
                             ego_vehicle_model="vehicle.tesla.model3")
        state = json.load((log_path / "state.json").open())
        asm4s.analyze()
        r_lp += asm4s.save_reasonable_p(re_path)
        if state["result"]["collision_with"]:
            print("COLLISION")

        re_path = asm_path / f"cycle_{cycle_num + 1}"
        re_path = re_path / "xp_scenario"
        os.mkdir(re_path)
        log_path = base_path / f"cycle_{cycle_num + 1}" / "round_1" / "vehicle.tesla.model3" / "logs" / "xp_scenario"
        asm4s = ASM4Scenario(log_path,
                             save_path=str(re_path),
                             ego_vehicle_model="vehicle.tesla.model3")
        state = json.load((log_path / "state.json").open())
        asm4s.analyze()
        r_xp += asm4s.save_reasonable_p(re_path)
        if state["result"]["collision_with"]:
            print("COLLISION")
        print()

    print("reasonable gp:", r_gp)
    print("reasonable lp:", r_lp)
    print("reasonable xp:", r_xp)
