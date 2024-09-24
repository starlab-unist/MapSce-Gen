#!/usr/bin/env python3

# Python packages
import carla
import sys
import time

list_spawn_points = None


def connect(args, idx):

    client = carla.Client(args.sim_host, args.sim_port[idx])
    client.set_timeout(60)
    try:
        client.get_server_version()
    except Exception as e:
        print(f"[-] Error: Check client connection.")
        sys.exit(-1)
    if args.debug:
        print("Connected to Client:", client)
    tm = client.get_trafficmanager(args.sim_tm_port[idx])
    tm.set_synchronous_mode(True)
    if args.debug:
        print("Traffic Manager Server:", tm)

    world = client.get_world()
    world.wait_for_tick()
    if args.debug:
        print("Connected to World:", world)
    time.sleep(1)
    return client, tm, world


def switch_map(conf, town, client, world, seed):
    """
    Switch map in the simulator and retrieve legitimate waypoints (a list of
    carla.Transform objects) in advance.
    """
    # global client
    global list_spawn_points

    assert (client is not None)

    try:
        # world = client.get_world()
        # if world.get_map().name != town: # force load every time
        if conf.user_defined_map is None:
            if conf.debug:
                print("[*] Switching town to {} (slow)".format(town))
            client.set_timeout(60)  # Handle sluggish loading bug
            client.load_world(str(town))  # e.g., "/Game/Carla/Maps/Town01"

            if conf.debug:
                print("[+] Switched")
            client.set_timeout(60)

            town_map = world.get_map()
            list_spawn_points = town_map.get_spawn_points()
        else:
            if conf.debug:
                print("[*] Switching town to {} (slow)".format(town))
            client.set_timeout(60)  # Handle sluggish loading bug
            client.generate_opendrive_world(seed.road_graph.map_str)

    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(-1)
    return world
