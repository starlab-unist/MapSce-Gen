class FuzzState:
    def __init__(self):

        # Scenario_file
        self.scenario_file = None

        # Route path
        self.route_path = None

        # Max values
        self.MAX_CYCLES = 0
        self.MAX_MUTATIONS = 0

        # States of fuzzing
        self.parent_scenario_id = 0
        self.child_scenario_id = 0
        self.ego_model_id = 0

    def set_scenario_route(self, scenario_file, route_path):
        self.scenario_file = scenario_file
        self.route_path = route_path

    def set_max_value(self, max_cycles, max_mutations):
        self.MAX_CYCLES = max_cycles
        self.MAX_MUTATIONS = max_mutations

    def next_cycle(self):
        self.parent_scenario_id += 1
        print(f"\n{'=' * 10} Start Fuzzing Cycle #{self.parent_scenario_id} {'=' * 10}")
        self._init_mutation()
        if self.parent_scenario_id < self.MAX_CYCLES:
            return True
        else:
            return False

    def get_cycle(self):
        return self.parent_scenario_id

    def next_mutation(self):
        self.child_scenario_id += 1
        if self.child_scenario_id < self.MAX_MUTATIONS:
            return True
        else:
            return False

    def _init_mutation(self):
        self.child_scenario_id = 0

    def get_mutation(self):
        return self.child_scenario_id

    def set_ego_model_id(self, ego_model_id):
        self.ego_model_id = ego_model_id
