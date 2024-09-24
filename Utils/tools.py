import os
import socket
import subprocess
import time


def set_environ():
    os.environ["EXECUTOR_ROOT"] = os.getcwd()
    os.environ["AUTOWARE_ROOT"] = os.environ["EXECUTOR_ROOT"] + "/AD/Autoware"
    os.environ["ZENOH_ROOT"] = "/home/dk-kling/Documents/Carla-Autoware/carla-autoware-launch/external/zenoh_carla_bridge/"
    os.environ["PYTHONPATH"] = os.environ["AUTOWARE_ROOT"]


def exit_handler(ports):
    for port in ports:
        while is_port_in_use(port):
            try:
                subprocess.run("kill -9 $(lsof -t -i :" + str(port) + ")", shell=True)
                time.sleep(1)
            except:
                continue


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", int(port))) == 0


def get_proj_root():
    config_path = os.path.abspath(__file__)
    src_dir = os.path.dirname(config_path)
    proj_root = os.path.dirname(src_dir)

    return proj_root


# def set_carla_api_path():
#     proj_root = get_proj_root()
#
#     dist_path = os.path.join(proj_root, "carla/PythonAPI/carla/dist")
#     glob_path = os.path.join(dist_path, "carla-*%d.%d-%s.egg" % (
#         sys.version_info.major,
#         sys.version_info.minor,
#         "win-amd64" if os.name == "nt" else "linux-x86_64"
#     ))
#
#     try:
#         api_path = glob.glob(glob_path)[0]
#     except IndexError:
#         print("Couldn't set Carla API path.")
#         exit(-1)
#
#     if api_path not in sys.path:
#         sys.path.append(api_path)
#         print(f"API: {api_path}")