import logging
import math
import os
import pathlib
from pathlib import Path
import shutil
import time
from typing import Iterator

from AD.Autoware.tools.constants import PATH_SIMULATION_LOG, NAME_USER, DISPLAY
from Utils.ComplexScenario import ComplexScenario

import docker
import numpy as np


logger = logging.getLogger()
logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s]: %(message)s',
    level=logging.INFO,
    datefmt='%Y/%m/%d %I:%M:%S %p'
)


def get_logger() -> logging.Logger:
    global logger
    return logger


def construct_seed(path_seed: Path, reproduce: bool) -> Iterator[pathlib.Path]:

    if reproduce:
        logs = list(path_seed.glob('Town*_*'))
        for seed in logs:
            mb = sorted(seed.glob('*_*'), key=lambda _p: int(str(_p).split('_')[-1]))[-1]
            yield mb / 'scenario.json'
        # for p in sorted()
    else:
        for p in sorted(path_seed.glob('*.json')):
            yield p


def init_log_dir_for_seed(path_log: Path, seed: Path, reproduce: bool=False) -> Path:
    if isinstance(path_log, str):
        path_log = Path(path_log)
    if reproduce:
        p = path_log / seed.parent.parent.stem
        p.mkdir(exist_ok=True)
    else:
        p = path_log / seed.stem
        p.mkdir(exist_ok=True)
        shutil.copy(seed, p / 'seed.json')
    return p


def init_log_dir_for_mutant(p: Path, mutant: ComplexScenario, c: int, r: int) -> None:
    path_mutant = p / f'{c}_{r}'
    path_mutant.mkdir(exist_ok=True)
    mutant.dump(path_mutant)


def record_simulation(p: Path, scenario: ComplexScenario, score: float, violation: bool,
                      only_measure: bool = False) -> None:
    data_list = ['front.mp4', 'top.mp4', 'state.json', 'measurements.csv']
    if only_measure:
        data_list = ['front.mp4', 'top.mp4', 'state.json', 'measurements.csv']
    scenario.dump(p)
    for f in data_list:
        if (PATH_SIMULATION_LOG / f).is_file():
            shutil.copy(PATH_SIMULATION_LOG / f, p / f)
    # if any violation is made, save ros bag file
    # if violation:
    #     if (PATH_SIMULATION_LOG / 'bag').is_dir():
    #         shutil.copytree(PATH_SIMULATION_LOG / 'bag', p / 'bag')
    #         shutil.rmtree(PATH_SIMULATION_LOG / 'bag')
    # Save score
    with (p / 'score.txt').open('w') as f:
        f.write(f'{score}')


def run_docker_container(kill_previous_run: bool=False, **kwargs) -> bool:
    already_running = False
    try:
        name_container = kwargs['name']
        docker_client = docker.from_env()
        # Check if container is already running
        if name_container in [c.name for c in docker_client.containers.list()]:
            already_running = True
            container_carla = docker_client.containers.get(name_container)
            if kill_previous_run:
                # get_logger().info(f"   - Container '{name_container}' is already running. I'll stop it and run another one.")
                container_carla.stop()
                while container_carla.status != 'removing':
                    container_carla.reload()
                    time.sleep(1)
            else:
                # get_logger().info(f"   - Container '{name_container}' is already running")
                return already_running
        # Check if there's any stopped container
        try:
            container_carla = docker_client.containers.get(name_container)
            # get_logger().info(f"   - '{name_container}' is not running(stopped before). I'll start the container")
            container_carla.start()
        except Exception as _:
            # get_logger().info(f"   - Start the container '{name_container}'")
            container_carla = docker_client.containers.run(**kwargs)
        os.system(f'docker update --restart unless-stopped {name_container} > /dev/null 2>&1')
    except Exception as e:
        # get_logger().error(f"Error while starting carla simulator with docker: {e}")
        exit(1)
    return already_running


def exec_docker_container(name_container: str, **kwargs) -> str:
    try:
        # print(kwargs)
        # import subprocess
        # cmd = kwargs['cmd']
        # if need_output:
        #     output = subprocess.check_output(f'docker exec -it {name_container} {cmd}', shell=True)
        #     return output.decode('utf-8')
        # else:
        #     subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        docker_client = docker.from_env()
        container = docker_client.containers.get(name_container)
        return container.exec_run(**kwargs).output.decode('utf-8')
    except Exception as e:
        # get_logger().error(f"Error while execute command in the docker container: {e}")
        exit(1)


def quaternion_from_euler(ai, aj, ak, axes='sxyz'):
    # Copied from
    # https://github.com/davheld/tf/blob/master/src/tf/transformations.py#L1100

    _AXES2TUPLE = {
        'sxyz': (0, 0, 0, 0), 'sxyx': (0, 0, 1, 0), 'sxzy': (0, 1, 0, 0),
        'sxzx': (0, 1, 1, 0), 'syzx': (1, 0, 0, 0), 'syzy': (1, 0, 1, 0),
        'syxz': (1, 1, 0, 0), 'syxy': (1, 1, 1, 0), 'szxy': (2, 0, 0, 0),
        'szxz': (2, 0, 1, 0), 'szyx': (2, 1, 0, 0), 'szyz': (2, 1, 1, 0),
        'rzyx': (0, 0, 0, 1), 'rxyx': (0, 0, 1, 1), 'ryzx': (0, 1, 0, 1),
        'rxzx': (0, 1, 1, 1), 'rxzy': (1, 0, 0, 1), 'ryzy': (1, 0, 1, 1),
        'rzxy': (1, 1, 0, 1), 'ryxy': (1, 1, 1, 1), 'ryxz': (2, 0, 0, 1),
        'rzxz': (2, 0, 1, 1), 'rxyz': (2, 1, 0, 1), 'rzyz': (2, 1, 1, 1)
    }

    _TUPLE2AXES = dict((v, k) for k, v in _AXES2TUPLE.items())

    _NEXT_AXIS = [1, 2, 0, 1]

    try:
        firstaxis, parity, repetition, frame = _AXES2TUPLE[axes.lower()]
    except (AttributeError, KeyError):
        _ = _TUPLE2AXES[axes]
        firstaxis, parity, repetition, frame = axes

    i = firstaxis
    j = _NEXT_AXIS[i+parity]
    k = _NEXT_AXIS[i-parity+1]

    if frame:
        ai, ak = ak, ai
    if parity:
        aj = -aj

    ai /= 2.0
    aj /= 2.0
    ak /= 2.0
    ci = math.cos(ai)
    si = math.sin(ai)
    cj = math.cos(aj)
    sj = math.sin(aj)
    ck = math.cos(ak)
    sk = math.sin(ak)
    cc = ci*ck
    cs = ci*sk
    sc = si*ck
    ss = si*sk

    quaternion = np.empty((4, ), dtype=np.float64)
    if repetition:
        quaternion[i] = cj*(cs + sc)
        quaternion[j] = sj*(cc + ss)
        quaternion[k] = sj*(cs - sc)
        quaternion[3] = cj*(cc - ss)
    else:
        quaternion[i] = cj*sc - sj*cs
        quaternion[j] = cj*ss + sj*cc
        quaternion[k] = cj*cs - sj*sc
        quaternion[3] = cj*cc + sj*ss
    if parity:
        quaternion[j] *= -1

    return quaternion


def run_carla_with_docker(version: str, offscreen: bool, kill_previous_run: bool=False) -> None:
    cmd = '/bin/bash ./CarlaUE4.sh -nosound -quality-level=Epic -fps 20'
    if offscreen:
        # get_logger().info(f"Run carla with docker container without screen.")
        cmd += ' -graphicsadapter=1 -RenderOffScreen -opengl'
    else:
        # get_logger().info(f"1. Run carla with docker container - DISPLAY: {DISPLAY}")
        if DISPLAY is None:
            # get_logger().error("Please set environment variable 'DISPLAY' before running Carla simulator. ex) export DISPLAY=:1; xhost +")
            exit(1)
    already_running = run_docker_container(
        kill_previous_run=kill_previous_run,
        image=f'carlasim/carla:{version}',
        command=cmd,
        auto_remove=True,
        detach=True,
        name=f'carla-{version}-{NAME_USER}',
        privileged=True,
        network_mode='host',
        runtime="nvidia",
        environment={
            "DISPLAY": DISPLAY
        },
        volumes={
            "/tmp/.X11-unix": {
                "bind": "/tmp/.X11-unix",
                "mode": "rw"
            },
            str(Path(__file__).resolve().parent.parent / 'data'): {
                "bind": "/home/carla/Import",
                "mode": "rw"
            }
        }
    )
    if not already_running:
        # get_logger().info("Carla simulator is just started. Waiting 10 seconds for the simulator to be loaded.")
        time.sleep(10)
