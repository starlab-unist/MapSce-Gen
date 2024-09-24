import carla
import random

from Utils.ComplexScenario import ComplexScenario

WeatherLib = [
        carla.WeatherParameters.ClearNoon,
        carla.WeatherParameters.CloudyNoon,
        carla.WeatherParameters.WetNoon,
        carla.WeatherParameters.WetCloudyNoon,
        carla.WeatherParameters.SoftRainNoon,
        carla.WeatherParameters.MidRainyNoon,
        carla.WeatherParameters.HardRainNoon,
        carla.WeatherParameters.ClearSunset,
        carla.WeatherParameters.CloudySunset,
        carla.WeatherParameters.WetSunset,
        carla.WeatherParameters.WetCloudySunset,
        carla.WeatherParameters.SoftRainSunset,
        carla.WeatherParameters.MidRainSunset,
        carla.WeatherParameters.HardRainSunset
    ]


# class WeatherManager:
#     def __init__(self, scenario: ComplexScenario):
#         self._weather = scenario.weather

    # def random_weather(self):
    #     import random
    #     self.weather = carla.WeatherParameters(
    #             # 구름의 양 [0-100]
    #             cloudiness=random.randrange(0, 100),
    #             # 강수량 [0-100]
    #             precipitation=random.randrange(0, 100),
    #             # 강수 퇴적물 (물 웅덩이) [0-100]
    #             precipitation_deposits=random.randrange(0, 100),
    #             # 바람 세기 (빗방울 방향) [0-100]
    #             wind_intensity=random.randrange(0, 100),
    #             # 태양 방위각 [0-360]
    #             sun_azimuth_angle=random.randrange(0, 360),
    #             # 태양 고도각 [-90-90]
    #             sun_altitude_angle=random.randrange(-90, 90),
    #             # 안개 밀도 [-90-90]
    #             fog_density=random.randrange(-90, 90),
    #             # 안개 거리 [0-infinite]
    #             fog_distance=random.randrange(0, 100),
    #             # 젖음 정도 (RGB 카메라 센서에만 영향을 줌)[0-100]
    #             wetness=random.randrange(0, 100),
    #             # 안개 높이 [0 - 100]
    #             fog_falloff=random.randrange(0, 100),
    #     )

def generate_weather(scenario: ComplexScenario):
    _weather = scenario.weather

    carla_weather = random.choice(WeatherLib)
    _weather["cloud"] = carla_weather.cloudiness
    _weather["rain"] = carla_weather.precipitation
    _weather["puddle"] = carla_weather.precipitation_deposits
    _weather["wind"] = carla_weather.wind_intensity
    _weather["angle"] = carla_weather.sun_azimuth_angle
    _weather["altitude"] = carla_weather.sun_altitude_angle
    _weather["fog"] = carla_weather.fog_density
    _weather["wetness"] = carla_weather.wetness

    scenario.weather = _weather


def mutate_weather(scenario: ComplexScenario):
    _weather = scenario.weather

    _weather["cloud"] += random.random() - 0.5 * 10
    _weather["rain"] += random.random() - 0.5 * 10
    _weather["puddle"] += random.random() - 0.5 * 10
    _weather["wind"] += random.random() - 0.5 * 10
    _weather["angle"] += random.random() - 0.5 * 36
    _weather["altitude"] += random.random() - 0.5 * 18
    _weather["fog"] += random.random() - 0.5 * 18
    _weather["wetness"] += random.random() - 0.5 * 10


def adjust_valid_weather(_weather):
    if _weather["cloud"] < 0:
        _weather["cloud"] = 0
    elif _weather["cloud"] > 100:
        _weather["cloud"] = 100

    if _weather["rain"] < 0:
        _weather["rain"] = 0
    elif _weather["rain"] > 100:
        _weather["rain"] = 100

    if _weather["puddle"] < 0:
        _weather["puddle"] = 0
    elif _weather["puddle"] > 100:
        _weather["puddle"] = 100

    if _weather["wind"] < 0:
        _weather["wind"] = 0
    elif _weather["wind"] > 100:
        _weather["wind"] = 100

    if _weather["angle"] < 0:
        _weather["angle"] = 0
    elif _weather["angle"] > 360:
        _weather["angle"] = 360

    if _weather["altitude"] < -90:
        _weather["altitude"] = -90
    elif _weather["altitude"] > 90:
        _weather["altitude"] = 90

    if _weather["fog"] < -90:
        _weather["fog"] = -90
    elif _weather["fog"] > 90:
        _weather["fog"] = 90

    if _weather["wetness"] < 0:
        _weather["wetness"] = 0
    elif _weather["wetness"] > 100:
        _weather["wetness"] = 100
