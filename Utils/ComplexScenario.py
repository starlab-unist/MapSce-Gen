import json

from typing import Dict
from pathlib import Path

from Utils.SimpleScenario import SimpleScenario
from Concretization.ScenarioObjects.Pedestrian import Pedestrian
from Concretization.ScenarioObjects.Vehicle import Vehicle
from Concretization.ScenarioObjects.Puddle import Puddle


class ComplexScenario(SimpleScenario):
    def __init__(self, _path):

        super().__init__(_path)

    @property
    def ego_model(self) -> Dict:
        return self._scenario["ego_model"]

    @ego_model.setter
    def ego_model(self, _ego_model: Dict) -> None:
        self._scenario["ego_model"] = _ego_model

    @property
    def is_complex(self) -> bool:
        return bool(self._scenario["npc"]["vehicles"])

    def update_sp(self, sp):
        self._scenario["mission"]["start"]["x"] = sp.location.x
        self._scenario["mission"]["start"]["y"] = sp.location.y
        self._scenario["mission"]["start"]["z"] = sp.location.z
        self._scenario["mission"]["start"]["roll"] = sp.rotation.roll
        self._scenario["mission"]["start"]["pitch"] = sp.rotation.pitch
        self._scenario["mission"]["start"]["yaw"] = sp.rotation.yaw

    def update_dp(self, dp):
        self._scenario["mission"]["dest"]["x"] = dp.location.x
        self._scenario["mission"]["dest"]["y"] = dp.location.y
        self._scenario["mission"]["dest"]["z"] = dp.location.z
        self._scenario["mission"]["dest"]["roll"] = dp.rotation.roll
        self._scenario["mission"]["dest"]["pitch"] = dp.rotation.pitch
        self._scenario["mission"]["dest"]["yaw"] = dp.rotation.yaw

    def update_sz(self, _z):
        self._scenario["mission"]["start"]["z"] = _z

    def update_dz(self, _z):
        self._scenario["mission"]["dest"]["z"] = _z

    def add_vehicle(self, _vehicle: Vehicle) -> None:
        self._scenario["npc"]["vehicles"].append(_vehicle.json)

    def add_pedestrian(self, _pedestrian: Pedestrian) -> None:
        self._scenario["npc"]["pedestrians"].append(_pedestrian.json)

    def add_puddle(self, _puddle: Puddle) -> None:
        self._scenario["puddles"].append(_puddle)

    def save_scenario(self):
        with self._path.open("w") as f:
            json.dump(self._scenario, f)

    def dump(self, p: Path, name_file: str = 'scenario.json') -> None:
        with (p / name_file).open('w') as f:
            json.dump(self._scenario, f)
