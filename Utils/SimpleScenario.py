import json
import carla

from pathlib import Path
from typing import Any, Dict, List


class SimpleScenario:
    def __init__(self, _path: Path):
        self._path = _path
        self._scenario: Dict[str, Any] = json.load(_path.open())

    @property
    def map(self) -> str:
        return self._scenario['map']

    @map.setter
    def map(self, _map: str) -> None:
        self._scenario['map'] = _map

    @property
    def mutation(self) -> int:
        return self._scenario['mutation']

    @mutation.setter
    def mutation(self, _mutation: int) -> None:
        self._scenario['mutation'] = _mutation

    @property
    def mission(self) -> Dict[str, Dict[str, float]]:
        return self._scenario['mission']

    @mission.setter
    def mission(self, _mission: Dict[str, Dict[str, float]]) -> None:
        self._scenario['mission'] = _mission

    @property
    def sp_loc(self):
        return carla.Location(
            self._scenario['mission']["start"]["x"],
            self._scenario['mission']["start"]["y"],
            self._scenario['mission']["start"]["z"]
        )

    @property
    def sp_rot(self):
        return carla.Rotation(
            self._scenario['mission']["start"]["pitch"],
            self._scenario['mission']["start"]["yaw"],
            self._scenario['mission']["start"]["roll"]
        )

    @property
    def dp_loc(self):
        return carla.Location(
            self._scenario['mission']["dest"]["x"],
            self._scenario['mission']["dest"]["y"],
            self._scenario['mission']["dest"]["z"]
        )

    @property
    def dp_rot(self):
        return carla.Rotation(
            self._scenario['mission']["dest"]["pitch"],
            self._scenario['mission']["dest"]["yaw"],
            self._scenario['mission']["dest"]["roll"]
        )

    @property
    def sp_transform(self):
        return carla.Transform(
            self.sp_loc,
            self.sp_rot
        )

    @property
    def dp_transform(self):
        return carla.Transform(
            self.dp_loc,
            self.dp_rot
        )

    @property
    def route(self) -> List:
        return self._scenario['mission']['route']

    @route.setter
    def route(self, _route: List) -> None:
        self._scenario['mission']['route'] = _route

    @property
    def target(self) -> str:
        return self._scenario['target']

    @target.setter
    def target(self, _target: str) -> None:
        self._scenario['target'] = _target

    @property
    def npc(self) -> Dict[str, List[Dict[str, float]]]:
        return self._scenario['npc']

    @npc.setter
    def npc(self, _npc: Dict[str, Any]):
        self._scenario['npc'] = _npc

    @property
    def weather(self) -> Dict[str, int]:
        return self._scenario['weather']

    @weather.setter
    def weather(self, _weather: Dict[str, int]) -> None:
        self._scenario['weather'] = _weather

    @property
    def puddles(self) -> List[Dict[str, float]]:
        return self._scenario['puddles']

    @puddles.setter
    def puddles(self, _puddles: List[Dict[str, float]]) -> None:
        self._scenario['puddles'] = _puddles

    def __str__(self) -> str:
        return json.dumps(self._scenario)

    def save(self, p: Path) -> None:
        with p.open("w") as f:
            json.dump(self._scenario, f)

    def change_path(self, s_path):
        self._path = s_path
