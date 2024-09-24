# MapSce-Gen
Generating Driving Scenario for Autonomous Vehicle

## Installation

- nvidia-driver-535
- [ROS noetic](XXXX)
- [Anaconda 23.7.2](XXXX)
- Python 3.8.5 
- [cuda 11.3](XXXX)
- Zenoh Bridge (Autoware-Carla ROS Bridge)

## Conda Settings

```shell
conda env create -f environment.yml --name f4a
conda activate f4a
```

## Set Zenoh Bridge Path

In line #9 of `Utils/tools.py`, change the path of `ZENOH_ROOT`.

```python
os.environ["ZENOH_ROOT"] = ## Set Your Zenoh Bridge Path! 
    # (ex: Carla-Autoware/carla-autoware-launch/external/zenoh_carla_bridge/)
```

## Add High-Definition Map

Please add your high-definition map to path, `InputGeneration/csv/`.

## Execution

1. Input Generation

```shell
python3 generate_seed.py
```

2. Run ScenaVRo
 
```shell
python3 fuzz.py
```

## Simulation Results

After running the scenario, we can check the results in the artifact directory, `out-artifact/`.

## Customize / Experiment

If you want to set other option of NPC, please edit `Concretization/Complicator.py`.
