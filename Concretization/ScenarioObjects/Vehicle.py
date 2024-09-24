import carla
from typing import Any, Dict


class Vehicle:
    def __init__(self, bp: str, sp: carla.Transform, ex, ey) -> None:
        self.__vehicle_info: Dict[str, Any] = {
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
            "start_time": 100,
            "active": False,
            "agent": None,
            "sensors": [],
            "extent_x": ex,
            "extent_y": ey,
            "ignore_traffic": False
        }

    @property
    def json(self) -> Dict[str, Any]:
        return self.__vehicle_info

    @property
    def actor(self) -> Any:
        return self.__vehicle_info["actor"]

    @actor.setter
    def actor(self, _actor) -> None:
        self.__vehicle_info["actor"] = _actor

    @property
    def bp(self) -> str:
        return self.__vehicle_info["bp"]

    @property
    def sp(self) -> carla.Transform:
        s = self.__vehicle_info["start"]
        loc = carla.Location(s["x"], s["y"], s["z"])
        rot = carla.Rotation(s["pitch"], s["yaw"], s["roll"])
        return carla.Transform(loc, rot)

    @property
    def dp(self) -> carla.Transform:
        d = self.__vehicle_info["dest"]
        loc = carla.Location(d["x"], d["y"], d["z"])
        rot = carla.Rotation(d["pitch"], d["yaw"], d["roll"])
        return carla.Transform(loc, rot)

    @property
    def path(self) -> (carla.Transform, carla.Transform):
        return self.sp, self.dp

    @property
    def start_time(self) -> int:
        return self.__vehicle_info["start_time"]

    @property
    def agent(self) -> Any:
        return self.__vehicle_info["agent"]

    @agent.setter
    def agent(self, _agent) -> None:
        self.__vehicle_info["agent"] = _agent

    @property
    def active(self) -> bool:
        return self.__vehicle_info["active"]

    @active.setter
    def active(self, _active) -> None:
        self.__vehicle_info["active"] = _active

    @property
    def sensors(self) -> Any:
        return self.__vehicle_info["sensors"]

    def add_sensor(self, sensor) -> None:
        self.__vehicle_info["sensors"].append(sensor)

    @property
    def ignore_traffic(self) -> bool:
        return self.__vehicle_info["ignore_traffic"]

    @ignore_traffic.setter
    def ignore_traffic(self, _ignore_traffic) -> Any:
        self.__vehicle_info["ignore_traffic"] = _ignore_traffic
