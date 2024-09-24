# from copy import deepcopy
# import random
# from typing import Dict, Generator, List, Optional
#
# from AD.Autoware.tools.constants import NEAR_POINT_MUTATION_THRESHOLD
# from AD.Autoware.tools.scenario import Scenario
# from AD.Autoware.tools.utils import get_logger
#
# import carla
#
#
# def __get_spawnable_points(_map: str, point: Optional[carla.Transform], dist: int = -1) -> List[carla.Transform]:
#     client = carla.Client('127.0.0.1', 2000)
#     client.set_timeout(10.0)
#     map_cur = client.get_world().get_map()
#     if not map_cur.name.lower().endswith(_map.lower()):
#         client.load_world(_map)
#         map_cur = client.get_world().get_map()
#     spawnable_points = map_cur.get_spawn_points()
#     if point is not None:
#         if dist != -1:
#             return [p for p in spawnable_points if p.location.distance(point.location) < dist]
#         else:
#             get_logger().warn("Distance threshold is not set for the spawning points. Ignore the threshold.")
#     return spawnable_points
#
#
# def __get_carla_transform(point: Dict[str, float]) -> carla.Transform:
#     return carla.Transform(
#         carla.Location(point['x'], point['y'], point['z']),
#         carla.Rotation(roll=point['roll'], pitch=point['pitch'], yaw=point['yaw'])
#     )
#
#
# def __transform_to_dict(point: carla.Transform) -> Dict[str, float]:
#     l = point.location
#     r = point.rotation
#     return {
#         'x': l.x,
#         'y': l.y,
#         'z': l.z,
#         'roll': r.roll,
#         'pitch': r.pitch,
#         'yaw': r.yaw
#     }
#
#
# def get_mutant(seed: Scenario, policy: str='random') -> Scenario:
#     policy = policy.lower()
#     # Avoid the seed to be mutated
#     mutant = deepcopy(seed)
#     # Mutate mission
#     mutant = mutate_mission(mutant, policy=policy)
#     # Mutate weather
#     mutant = mutate_weather(mutant, policy=policy)
#     # Mutate NPC vehicle and NPC pedestrians
#     mutant = mutate_npcs(mutant, policy=policy)
#     # Mutate puddle
#     mutant = mutate_puddles(mutant, policy=policy, sp=mutant.mission['start'])
#     return mutant
#
# def mutate_mission(scenario: Scenario, policy: str) -> Scenario:
#     if policy == 'dryrun':
#         return scenario
#     elif policy == 'random':
#         scenario.mission['start'] = mutate_start(scenario, policy)
#         scenario.mission['dest'] = mutate_dest(scenario, policy).pop()
#     return scenario
#
# def mutate_weather(scenario: Scenario, policy: str) -> Scenario:
#     if policy == 'dryrun':
#         return scenario
#     elif policy == 'random':
#         scenario.weather = {
#             'cloud': random.randint(0, 100),
#             'rain': random.randint(0, 100),
#             'puddle': random.randint(0, 100),
#             'wind': random.randint(0, 100),
#             'fog': random.randint(0, 100),
#             'wetness': random.randint(0, 100),
#             'angle': random.randint(0, 360),
#             'altitude': random.randint(-90, 90)
#         }
#     return scenario
#
# def mutate_npcs(scenario: Scenario, policy: str) -> Scenario:
#     # TODO
#     if policy == 'dryrun':
#         return scenario
#     elif policy == 'random':
#         pass
#     return scenario
#
# def mutate_puddles(scenario: Scenario, policy: str, sp: Dict[str, float]) -> Scenario:
#     if policy == 'dryrun':
#         return scenario
#     elif policy == 'random':
#         sp = __get_carla_transform(sp)
#         sp = random.sample(__get_spawnable_points(scenario.map, sp, dist=NEAR_POINT_MUTATION_THRESHOLD)[:], k=1).pop()
#         scenario.puddles.append({
#             "level": random.randint(0, 200) / 100,
#             "x": sp.location.x,
#             "y": sp.location.y,
#             "z": sp.location.z,
#             "size_x": 500.0,
#             "size_y": 500.0,
#             "size_z": 1000.0
#         })
#     return scenario
#
# def mutate_start(scenario: Scenario, policy: str='random') -> Dict[str, float]:
#     if policy == 'dryrun':
#         return scenario.mission['start']
#     elif policy == 'random':
#         start = __get_carla_transform(scenario.mission['start'])
#         starts = __get_spawnable_points(scenario.map, start, dist=NEAR_POINT_MUTATION_THRESHOLD)[:]
#         return __transform_to_dict(random.sample(starts, k=1).pop())
#     else:
#         return {}
#
# def mutate_dest(scenario: Scenario, policy: str='random') -> List[Dict[str, float]]:
#     if policy == 'dryrun':
#         return [scenario.mission['dest']]
#     elif policy == 'random':
#         dest = __get_carla_transform(scenario.mission['dest'])
#         dests = __get_spawnable_points(scenario.map, dest, dist=NEAR_POINT_MUTATION_THRESHOLD)[:]
#         random.shuffle(dests)
#         return [__transform_to_dict(d) for d in dests]
#     else:
#         return []
