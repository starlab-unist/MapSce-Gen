import carla
from typing import Any, Dict


class Pedestrian:
    def __init__(self, bp: str, sp: carla.Transform, dp: carla.Transform, speed, trigger_distance, ex, ey, legal=0) -> None:
        self.__pedestrian_info: Dict[str, Any] = {
            "actor": None,
            "bp": bp,
            "start": {
                "x": sp.location.x,
                "y": sp.location.y,
                "z": sp.location.z,
                "pitch": sp.rotation.pitch,
                "yaw": sp.rotation.yaw,
                "roll": sp.rotation.roll
            },
            "dest": {
                "x": dp.location.x,
                "y": dp.location.y,
                "z": dp.location.z,
                "pitch": dp.rotation.pitch,
                "yaw": dp.rotation.yaw,
                "roll": dp.rotation.roll
            },
            "start_time": 100,
            "active": False,
            "speed": speed,
            "trigger_distance": trigger_distance,
            "extent_x": ex,
            "extent_y": ey,
            "legal": legal
        }

    @property
    def json(self) -> Dict[str, Any]:
        return self.__pedestrian_info

    @property
    def actor(self) -> Any:
        return self.__pedestrian_info["actor"]

    @actor.setter
    def actor(self, _actor) -> None:
        self.__pedestrian_info["actor"] = _actor

    @property
    def bp(self) -> str:
        return self.__pedestrian_info["bp"]

    @property
    def sp(self) -> carla.Transform:
        s = self.__pedestrian_info["start"]
        loc = carla.Location(s["x"], s["y"], s["z"])
        rot = carla.Rotation(s["pitch"], s["yaw"], s["roll"])
        return carla.Transform(loc, rot)

    @property
    def dp(self) -> carla.Transform:
        d = self.__pedestrian_info["dest"]
        loc = carla.Location(d["x"], d["y"], d["z"])
        rot = carla.Rotation(d["pitch"], d["yaw"], d["roll"])
        return carla.Transform(loc, rot)

    @property
    def start_time(self) -> int:
        return self.__pedestrian_info["start_time"]

    @property
    def active(self) -> bool:
        return self.__pedestrian_info["active"]

    @active.setter
    def active(self, _active) -> None:
        self.__pedestrian_info["active"] = _active

    @property
    def speed(self) -> float:
        return self.__pedestrian_info["speed"]

    @property
    def trigger_distance(self) -> float:
        return self.__pedestrian_info["trigger_distance"]
