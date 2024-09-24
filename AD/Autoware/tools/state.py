from __future__ import annotations
import json
from pathlib import Path
import time
from typing import Any, Dict, List

from AD.Autoware.tools.constants import PATH_SIMULATION_LOG

import carla


class State:

    def __init__(self, path_scenario: Path) -> None:
        # Start time of the simulation
        self.time_start: float = time.time()
        # Path to save
        self.log_dir: Path = path_scenario
        # Passed points during the simulation
        self.point: List[Dict[str, float]] = []
        # Speed during the simulation
        self.speed: List[float] = []
        # Speed limit during the simulation
        self.speed_limit: List[float] = []
        # Throttle during the simulation
        self.throttle: List[float] = []
        # Steer during the simulation
        self.steer: List[float] = []
        # Brake during the simulation
        self.brake: List[float] = []
        # Hand brake during the simulation
        self.hand_brake: List[bool] = []
        # Reverse during the simulation
        self.reverse: List[bool] = []
        # Manual gear shift during the simulation
        self.manual_gear_shift: List[bool] = []
        # Gear during the simulation
        self.gear: List[float] = []
        # Violation informations
        self.result: Dict[str, Any] = {
            'collision': False,
            'collision_with': None,
            'stalling': False,
            'speeding': False,
            'spawn_timeout': False,
            'start_timeout': False,
            'normal': False,
            'timeout': False
        }
        # End time of the simulation
        self.time_end: float = 0.0

    def __str__(self) -> str:
        return str(self.__dict__)

    def update(self, state_t: Dict[str, Any]) -> None:
        for k, v in state_t.items():
            attr = getattr(self, k)
            if isinstance(attr, list):
                if not isinstance(v, carla.Transform):
                    attr.append(v)
                else:
                    loc = v.location
                    rot = v.rotation
                    attr.append({
                        'x': loc.x,
                        'y': loc.y,
                        'z': loc.z,
                        'roll': rot.roll,
                        'pitch': rot.pitch,
                        'yaw': rot.yaw
                    })
            elif isinstance(attr, dict):
                _t = dict()
                for _k, _v in attr.items():
                    _t[_k] = _v
                setattr(self, k, _t)

    def any_violation(self) -> bool:
        return self.result['collision'] or self.result['collision_with'] or self.result['stalling']

    def dump(self) -> None:
        self.time_end = time.time()
        with (self.log_dir / 'state.json').open('w') as f:
            del self.log_dir
            json.dump(self.__dict__, f)

    @classmethod
    def get_simulation_result(cls) -> State:
        with (PATH_SIMULATION_LOG / 'state.json').open() as f:
            state = json.load(f)
        s = State(PATH_SIMULATION_LOG)
        s.time_start = state['time_start']
        s.point = state['point']
        s.speed = state['speed']
        s.speed_limit = state['speed_limit']
        s.throttle = state['throttle']
        s.steer = state['steer']
        s.brake = state['brake']
        s.hand_brake = state['hand_brake']
        s.reverse = state['reverse']
        s.manual_gear_shift = state['manual_gear_shift']
        s.gear = state['gear']
        s.result = state['result']
        s.time_end = state['time_end']
        s.invaded_lanes = state['invaded_lanes']
        s.loc_npcs = state['loc_npcs']
        s.bounding_box_ego = state['bounding_box_ego']
        return s
