import os
from pathlib import Path
from typing import Union

PROJECT_ROOT: Path = Path(__file__).parent.parent.resolve()
NAME_USER: Union[None, str] = os.getenv("USER")
DISPLAY: Union[None, str] = os.getenv("DISPLAY")
ZENOH_ROOT: Path = Path(os.getenv("ZENOH_ROOT"))
CARLA_VERSION: str = '0.9.13'

# PATH_SIMULATION_LOG: Path = PROJECT_ROOT / 'carla-autoware-launch/external/zenoh_carla_bridge/carla_agent/logs'
PATH_SIMULATION_LOG: Path = ZENOH_ROOT / 'carla_agent/logs'
PATH_LOCK: Path = PATH_SIMULATION_LOG / 'lock'

NEAR_POINT_MUTATION_THRESHOLD: int = 50

POLLING_INTERVAL: int = 2
LOAD_TIMEOUT: int = 120

# Simulation Results
SUCC: int = 0
NEXT_SEED: int = 1
TRY_AGAIN: int = 2
EXIT: int = 3

NEAREST_VOXEL_TRANSFORMATION_LIKELIHOOD: float = 2.300000