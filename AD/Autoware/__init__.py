import math
import os
import subprocess
import time
import getpass
from typing import Dict, Union

from AD.Autoware.tools.constants import PATH_LOCK, POLLING_INTERVAL, PATH_SIMULATION_LOG, NEAREST_VOXEL_TRANSFORMATION_LIKELIHOOD
from AD.Autoware.tools.exceptions import RunAgain, Exit, RoutingFailure
from AD.Autoware.tools.state import State
from AD.Autoware.tools.utils import exec_docker_container, get_logger, quaternion_from_euler
from Utils.ComplexScenario import ComplexScenario


def __spawn_ego_vehicle(scenario: ComplexScenario) -> None:
    # get_logger().info("Run Carla-Autoware bridge")
    s = str(scenario).replace(' ', '').replace('"', '\\"')
    cmd = 'bash -c' + ' "' + \
          ' && '.join([
              'source ~/.bashrc',
              'export ROS_LOCALHOST_ONLY=1',
              'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp',
              'cd autoware_carla_launch',
              'source env.sh',
              'source /opt/ros/galactic/setup.bash',
              'source /autoware/install/setup.bash',
              f'export CARLA_MAP_NAME={scenario.map}',
              f'export CARLA_MAP_PATH=/home/{getpass.getuser()}/autoware_carla_launch/carla_map/{scenario.map}',
              f"./script/fuzz.sh '{s}' &"
          ]) + '"'
    exec_docker_container(name_container='bridge', cmd=cmd)


def __call_ros2(cmd: str, matching_str: str, timeout: int = 120, timeout_cmd: int = 30, wait_for_output: bool = True,
                return_output: bool = False) -> Union[str, bool]:
    t = time.time()
    while True:
        if timeout_cmd > 0:
            command = f'bash -c "source /autoware/install/setup.bash && export ROS_LOCALHOST_ONLY=1 && export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp && timeout {timeout_cmd} {cmd}"'
        else:
            command = f'bash -c "source /autoware/install/setup.bash && export ROS_LOCALHOST_ONLY=1 && export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp && {cmd}"'
        output = exec_docker_container(
            name_container='autoware',
            cmd=command
        )
        if return_output:
            return output
        if 'rclpy.executors.ExternalShutdownException' in output:
            return False
        if matching_str in output:
            return True
        if not wait_for_output:
            return False
        if time.time() - t > timeout:
            return False
        time.sleep(2)


def __wait_to_be_connected(timeout: int) -> bool:
    # Run bridge
    cmd = 'bash -c' + ' "' + \
          ' && '.join([
              'source ~/.bashrc',
              'export ROS_LOCALHOST_ONLY=1',
              'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp',
              'cd autoware_carla_launch',
              'source env.sh',
              'source /opt/ros/galactic/setup.bash',
              'source /autoware/install/setup.bash',
              f"RUST_LOG=z=info /home/{getpass.getuser()}/autoware_carla_launch/external/zenoh_carla_bridge/target/release/zenoh_carla_bridge &"
          ]) + '"'
    exec_docker_container(
        name_container='bridge',
        cmd=cmd
    )
    # get_logger().info("Waiting for the Autoware to be connected with Carla.")
    cmd = " ".join([
        'ros2',
        'topic',
        'echo',
        '--once',
        '/system/component_state_monitor/component/autonomous/localization'
    ])
    res = __call_ros2(cmd=cmd, matching_str='available: true', timeout=timeout)
    if res:
        # get_logger().info("Successfully connected Carla and Autoware")
        return True
    else:
        return False


def __send_routing_request(dest: Dict[str, float], timeout=3) -> bool:
    q = quaternion_from_euler(0.0, 0.0, math.radians(-dest['yaw']))
    ps = [dest['x'], -dest['y'], dest['z'], q[0], q[1], q[2], q[3]]
    cmd = " ".join([
        'ros2',
        'topic',
        'pub',
        '--once',
        "/planning/mission_planning/goal",
        "geometry_msgs/msg/PoseStamped",
        f"'{{ header: {{ stamp: now, frame_id: 'map'}}, pose: {{ position: {{x: {ps[0]}, y: {ps[1]}, z: {ps[2]} }}, orientation: {{x: {ps[3]}, y: {ps[4]}, z: {ps[5]}, w: {ps[6]} }} }} }}'",
    ])
    _ = __call_ros2(cmd=cmd, matching_str='', wait_for_output=False)
    return __is_routing_valid(timeout)


def __is_routing_valid(timeout) -> bool:
    cmd_check = " ".join([
        'ros2',
        'topic',
        'echo',
        '--once',
        '/api/operation_mode/state'
    ])
    time.sleep(3)
    out = __call_ros2(cmd=cmd_check, matching_str='is_autonomous_mode_available: true', wait_for_output=False)
    if out:
        # get_logger().info(f'Routing request done!')
        return True
    else:
        # get_logger().info(f'Cannot find proper routing path')
        return False


def __wait_to_be_loaded(timeout: int) -> bool:
    cmd = " ".join([
        'ros2',
        'topic',
        'echo',
        '--once',
        '/rosout'
    ])
    'msg: waiting for initial pose...'
    'msg: waiting for self pose'
    res = __call_ros2(cmd=cmd, matching_str='msg: waiting for self pose', timeout=timeout)
    if res:
        # get_logger().info("Successfully loaded Autoware.")
        return True
    else:
        return False


def __load_autoware(scenario: ComplexScenario, timeout: int) -> bool:
    # get_logger().info("Loading Autoware")
    #  > /dev/null 2>&1
    cmd = 'bash -c' + ' "' + \
          ' && '.join([
              'source ~/.bashrc',
              'cd autoware_carla_launch',
              'source env.sh',
              'source /autoware/install/setup.bash',
              'source /opt/ros/humble/setup.bash',
              f'export CARLA_MAP_NAME={scenario.map}',
              f'export CARLA_MAP_PATH=/home/{getpass.getuser()}/autoware_carla_launch/carla_map/{scenario.map}',
              'export ROS_LOCALHOST_ONLY=1',
              'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp',
              f'./script/run-autoware.sh &'
          ]) + '"'
    exec_docker_container(name_container='autoware', cmd=cmd)
    return __wait_to_be_loaded(timeout)


def __start_driving() -> None:
    cmd = " ".join([
        'ros2',
        'topic',
        'pub',
        '--once',
        "/autoware/engage",
        "autoware_auto_vehicle_msgs/msg/Engage",
        "'{engage: True}'",
        "-1"
    ])
    __call_ros2(cmd=cmd, matching_str='')
    # Unlock the pygame UI
    PATH_LOCK.unlink()


def __start_recording() -> None:
    # For recording ros messages
    cmd = " ".join([
        'ros2',
        'bag',
        'record',
        '-o',
        "autoware_carla_launch/external/zenoh_carla_bridge/carla_agent/logs/bag",
        "-a",
        '--compression-mode',
        'file',
        '--compression-format',
        'zstd',
        "&"
    ])
    __call_ros2(cmd=cmd, timeout_cmd=-1, matching_str='')


def __finish_recording() -> None:
    # Post-process ros bag file
    cmd = " ".join([
        'ros2',
        'bag',
        'reindex',
        'autoware_carla_launch/external/zenoh_carla_bridge/carla_agent/logs/bag'
    ])
    __call_ros2(cmd=cmd, timeout_cmd=-1, matching_str='')


def __wait_until_driving_done(no_record: bool, interval: int = POLLING_INTERVAL) -> None:
    if not no_record:
        __start_recording()
    # Wait until the driving done
    while not (PATH_SIMULATION_LOG / 'end').is_file():
        time.sleep(interval)
    # get_logger().info("Driving Done.")
    if not no_record:
        __finish_recording()
    __restart_autoware()


def __check_pose_initialization() -> bool:
    cmd = " ".join([
        'ros2',
        'topic',
        'echo',
        '--once',
        '--field',
        'data',
        '/localization/pose_estimator/nearest_voxel_transformation_likelihood'
    ])
    output = str(__call_ros2(cmd=cmd, matching_str='', return_output=True))
    try:
        value = float(output.split('\n')[0])
        # get_logger().info(f"Nearest voxel transformation likelihood: {value}")
        return value >= NEAREST_VOXEL_TRANSFORMATION_LIKELIHOOD
    except Exception as _:
        return False


def __restart_autoware() -> None:
    os.system("docker kill autoware > /dev/null 2>&1")
    os.system("docker restart autoware > /dev/null 2>&1")


def __restart_bridge(interval: int = POLLING_INTERVAL, force: bool = True) -> None:
    if not force:
        # get_logger().info("Logging the simulation")
        while True:
            output = subprocess.check_output(['docker', 'top', 'bridge']).decode('utf-8')
            if not 'main.py' in output:
                break
            time.sleep(interval)
    os.system("docker restart bridge > /dev/null 2>&1")


def clean_up():
    __restart_autoware()
    __restart_bridge()


def run(scenario: ComplexScenario, no_record: bool = False, dry_run: bool = False) -> State:
    chances_run_again = 3
    while True:
        if chances_run_again <= 0:
            # get_logger().info("No more try for the same seed. Try next seed.")
            raise RunAgain
        chances_run_again -= 1
        try:
            # Spawn ego vehicle
            __spawn_ego_vehicle(scenario)
            # Load Autoware
            if not __load_autoware(scenario, timeout=120):
                # get_logger().error("Failed to load Autoware.")
                # If the loading fails, try again not changing the scenario.
                raise RunAgain
            # Connect Carla and Autoware via Bridge
            if not __wait_to_be_connected(timeout=120):
                # get_logger().error("Failed to connect Carla and Autoware.")
                # If the loading fails, try again not changing the scenario.
                raise RunAgain
            if not __check_pose_initialization():
                # get_logger().error("Initialization error. Run the same scenario again.")
                # Do not decrease the chance.
                chances_run_again += 1
                raise RunAgain
            # Send routing request
            # get_logger().info("Send routing request to the Autoware.")

            __send_routing_request(scenario.mission['dest'])
            scenario.dump(PATH_SIMULATION_LOG)

            # Start driving
            __start_driving()
            # Check if driving is done
            __wait_until_driving_done(no_record)
            # Simulation done
            __restart_bridge(force=False)
            return State.get_simulation_result()
        except RunAgain as _:
            # get_logger().info("Run the simulation again with the same scenario.")
            continue
        except KeyboardInterrupt as _:
            raise Exit
        finally:
            clean_up()
