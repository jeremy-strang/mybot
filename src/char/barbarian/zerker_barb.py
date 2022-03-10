from operator import is_
import keyboard
from mas import world_to_abs
from utils.custom_mouse import mouse
from char import IChar, CharacterCapabilities
from char.barbarian.barbarian import Barbarian
from template_finder import TemplateFinder
from ui import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait, is_in_roi, cut_roi
import time
from pather import Pather, Location
import math
import threading
import numpy as np
import random
import cv2

from api.mapassist import MapAssistApi
from pather_v2 import PatherV2
from state_monitor import StateMonitor, MonsterPriorityRule, MonsterType
from obs import ObsRecorder

class ZerkerBarb(Barbarian):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: MapAssistApi, obs_recorder: ObsRecorder, pather: Pather, pather_v2: PatherV2):
        Logger.info("Setting up Berserk Barbarian")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder, pather, pather_v2)
        self._pather = pather
        self._pather_v2 = pather_v2
        self._do_pre_move = True

    def kill_b(self, game_state: StateMonitor) -> bool: # TODO
        atk_len = self._char_config["atk_len_trav"]
        self._kill_mobs(game_state, atk_len)
        return True

    def distance(self, monster, offset):
        if type(monster) is dict:
            player_p = self._api.data['player_pos_world']+self._api.data['player_offset']
            dist = math.dist(player_p, monster["position"]) -(offset [0] + offset [1]) 
            return dist
        return 0

    def prepare_attack(self):
        wait(0.05, 0.1)
        keyboard.send(self._skill_hotkeys["howl"])
        wait(0.05)
        mouse.click(button="right")
        wait(0.05)
        if self._skill_hotkeys["berserk"]:
            keyboard.send(self._skill_hotkeys["berserk"])
            wait(0.05)
        mouse.press(button="left")
        wait(0.1, 0.2)
        keyboard.send(self._char_config["stand_still"], do_release=False) 
        wait(0.05, 0.1)

    def post_attack(self):
        mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False) 
        wait(0.1, 0.15)

    def mouse_follow_unit(self, monster, offset):
        player_p = self._api.data['player_pos_world']+self._api.data['player_offset']
        pos_monitor = world_to_abs([monster["position"][0]+offset[0]-2, monster["position"][1]+offset[1]-2],player_p)
        pos_monitor = self._screen.convert_abs_to_monitor(pos_monitor)    
        wait(0.1)
        mouse.move(*pos_monitor)

    def kill_uniques(self, monster, aura: str = "concentration", offset = [-1, -1]) -> bool:
        if not self._pather_v2.move_to_monster(self, monster): return False
        dist = self.distance(monster, offset)
        counter = 0
        while dist > 7 and counter < 5:
            counter += 1
            wait(0.1, 0.2)
            monster = self.kill_around(self._api, density=self._char_config["density"], area=self._char_config["area"], special = True)
            self._pather_v2.move_to_monster(self, monster)
            dist = self.distance(monster, offset)
        
        while type(monster) != bool and dist <= 7:
            self.prepare_attack()
            self.mouse_follow_unit(monster, offset)
            wait(0.8, 1.0)
            monster = self.kill_around(self._api, density=self._char_config["density"], area=self._char_config["area"], special = True)
            self.post_attack()
            if type(monster)==dict:
                dist = self.distance(monster, offset)
            else:
                dist = 10
        self.post_attack()
        self.do_hork(unique_only=True, disable_swap=True)
        return True

    def kill_council(self, game_state: StateMonitor = None) -> bool:
        rules = [
            MonsterPriorityRule(auras = ["CONVICTION"]),
            MonsterPriorityRule(auras = ["HOLYFREEZE", "HOLY_FREEZE"]),
            MonsterPriorityRule(names = ["CouncilMember"], monster_types = [MonsterType.SUPER_UNIQUE]),
            MonsterPriorityRule(names = ["CouncilMember"]),
            MonsterPriorityRule(monster_types = [MonsterType.UNIQUE]),
        ]
        game_state = StateMonitor(rules, self._api, unique_id=-1, many=True)
        self._kill_mobs(game_state, reposition_pos_world=(156, 113))
        game_state.stop()
        return True

    def _kill_mobs(self, game_state: StateMonitor, atk_len: float = 1.5, time_out: float = 30, reposition_pos_world = None) -> bool:
        Logger.debug(f"Beginning combat")
        start = time.time()
        last_move = start
        elapsed = 0
        while elapsed < time_out and game_state._dead == 0:
            if game_state._ready:
                target_pos = game_state._target_pos
                target_pos = [target_pos[0]-9.5,target_pos[1]-39.5]
                # If we've been standing in one spot for too long, reposition
                if time.time() - last_move > 6.0 and reposition_pos_world is not None:
                    Logger.debug("Stood in one place too long, repositioning")
                    self._pather_v2.traverse(reposition_pos_world, self, time_out = 3.0)
                    last_move = time.time()
                elif game_state._dist > 6:
                    move_pos_screen = self._pather._adjust_abs_range_to_screen([target_pos[0], target_pos[1]])
                    move_pos_m = self._screen.convert_abs_to_monitor(move_pos_screen)
                    self.pre_move()
                    self.move(move_pos_m, force_tp=True)
                    wait(0.1)
                    last_move = time.time()
                else:
                    self.cast_melee("berserk", atk_len, target_pos)
            elapsed = time.time() - start
        # This is a hack to prevent Teleport from being used during pickit
        keyboard.send(self._char_config["battle_orders"])
        wait(0.04, 0.08)
        Logger.debug(f"Finished killing mobs, combat took {elapsed} sec")
        return True

    def _kill_mobs_v2(self, priority_rules: list[MonsterPriorityRule] = []):
        pass
