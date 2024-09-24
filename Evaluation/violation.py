import os.path
import json


class ViolationChecker:
    def __init__(self, json_path_list):
        self.result_dict = dict()
        for json_path in json_path_list:
            state = json.load((json_path / "state.json").open())
            self.result_dict[os.path.basename(json_path)] = state["result"]

        self.ads_collision_bug = False
        self.com_collision_bug = False

        self.ads_collision_npc_bug = False
        self.com_collision_npc_bug = False

        self.ads_speeding_bug = False
        self.com_speeding_bug = False

        self.ads_stalling_bug = False
        self.com_stalling_bug = False

        self.collision_bug_models = list()
        self.collision_npc_bug_models = list()
        self.speeding_bug_models = list()
        self.stalling_bug_models = list()

    def calc_violation(self):
        collision_bug_list = list()
        collision_npc_bug_list = list()
        speeding_bug_list = list()
        stalling_bug_list = list()

        for result in list(self.result_dict.keys()):
            pivot = self.result_dict.pop(result)

            if pivot["collision"]:
                collision_bug_list.append(True)
                self.collision_bug_models.append(result)
            else:
                collision_bug_list.append(False)

            if pivot["collision_with"] is not None:
                collision_npc_bug_list.append(True)
                self.collision_npc_bug_models.append(result)
            else:
                collision_npc_bug_list.append(False)

            if pivot["speeding"]:
                speeding_bug_list.append(True)
                self.speeding_bug_models.append(result)
            else:
                speeding_bug_list.append(False)

            if pivot["stalling"]:
                stalling_bug_list.append(True)
                self.stalling_bug_models.append(result)
            else:
                stalling_bug_list.append(False)

        self.ads_collision_bug = all(collision_bug_list)
        if not self.ads_collision_bug:
            self.com_collision_bug = any(collision_bug_list)

        self.ads_collision_npc_bug = all(collision_npc_bug_list)
        if not self.ads_collision_npc_bug:
            self.com_collision_npc_bug = any(collision_npc_bug_list)

        self.ads_speeding_bug = all(speeding_bug_list)
        if not self.ads_speeding_bug:
            self.com_speeding_bug = any(speeding_bug_list)

        self.ads_stalling_bug = all(stalling_bug_list)
        if not self.ads_stalling_bug:
            self.com_stalling_bug = any(stalling_bug_list)

    def print_violation(self):
        if self.ads_collision_bug:
            print("ADS Bug: Collision")
        if self.ads_collision_npc_bug:
            print("ADS Bug: NPC Collision")
        if self.ads_speeding_bug:
            print("ADS Bug: Speeding")
        if self.ads_stalling_bug:
            print("ADS Bug: Stalling")

        if self.com_collision_bug:
            print("Compatibility Bug: Collision")
        if self.com_collision_npc_bug:
            print("Compatibility Bug: NPC Collision")
        if self.com_speeding_bug:
            print("Compatibility Bug: Speeding")
        if self.com_stalling_bug:
            print("Compatibility Bug: Stalling")
        print()

    def get_violation(self):
        return {
            "ads_collision_bug": self.ads_collision_bug,
            "ads_collision_npc_bug": self.ads_collision_npc_bug,
            "ads_speeding_bug": self.ads_speeding_bug,
            "ads_stalling_bug": self.ads_stalling_bug,

            "com_collision_bug": self.com_collision_bug,
            "com_collision_npc_bug": self.com_collision_npc_bug,
            "com_speeding_bug": self.com_speeding_bug,
            "com_stalling_bug": self.com_stalling_bug,

            "collision_bug_models": self.collision_bug_models,
            "collision_npc_bug_models": self.collision_npc_bug_models,
            "speeding_bug_models": self.speeding_bug_models,
            "stalling_bug_models": self.stalling_bug_models
        }

    def violated(self):
        return any([
            self.ads_collision_bug,
            self.com_collision_bug,

            self.ads_collision_npc_bug,
            self.com_collision_npc_bug,

            self.ads_speeding_bug,
            self.com_speeding_bug,

            self.ads_stalling_bug,
            self.com_stalling_bug
        ])
