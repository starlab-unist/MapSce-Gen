import os
import time

from multiprocessing import Process

timeout_seconds = 300


class Executor:
    def __init__(self, args):
        self.test_model = args.test_model
        self.scenario_list = args.scenario_list
        self.log_dir_list = args.log_dir_list
        self.sim_port = args.sim_port
        self.num_model = len(self.scenario_list)

    def all_scenario_run(self):
        for i in range(len(self.scenario_list)):
            print(f"[+] Driving Scenario is Prepared!")
            scenario_path = self.scenario_list[i]
            log_dir = self.log_dir_list[i]

            print(f"[*] Executing Driving Scenario...")

            while not os.listdir(log_dir):
                start_time = time.time()
                simulate_p = Process(
                    target=os.system,
                    args=(f"python3 run_sim.py -p {self.sim_port} -s {scenario_path} -o {log_dir}",)
                )

                simulate_p.start()

                while time.time() - start_time < timeout_seconds and simulate_p.is_alive():
                    time.sleep(2)

                if simulate_p.is_alive():
                    from AD.Autoware import clean_up
                    clean_up()
                    simulate_p.terminate()
                    simulate_p.join()
                    time.sleep(2)

            print(f"[+] Driving Scenario is Executed Completely!\n")
