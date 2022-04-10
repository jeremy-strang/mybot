from operator import is_
import pprint
from typing import Tuple
import keyboard
from utils.coordinates import world_to_abs
from utils.custom_mouse import mouse
from char import IChar
from char.barbarian.barbarian import Barbarian
from template_finder import TemplateFinder
from ui import UiManager
from pathing import OldPather
from logger import Logger
from screen import Screen
from utils.misc import rotate_vec, unit_vector, wait, is_in_roi, cut_roi
import time
from pathing import OldPather, Location
import math
import threading
import numpy as np
import random
import cv2

from api.mapassist import MapAssistApi
from pathing import Pather
from state_monitor import StateMonitor
from monsters import MonsterRule, MonsterType
from obs import ObsRecorder
from monsters import CHAMPS_UNIQUES, sort_and_filter_monsters

class ZerkerBarb(Barbarian):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: MapAssistApi, obs_recorder: ObsRecorder, old_pather: OldPather, pather: Pather):
        Logger.info("Setting up Berserk Barbarian")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder, old_pather, pather)
        self._old_pather = old_pather
        self._pather = pather
        self._do_pre_move = True

    def post_attack(self):
        mouse.release(button="left")
        wait(0.02, 0.03)
        keyboard.release(self._char_config["force_move"])
        wait(0.03, 0.04)
        keyboard.release(self._char_config["stand_still"])
        wait(0.03, 0.04)

    def _kill_mobs(self,
                  prioritize: list[MonsterRule],
                  ignore: list[MonsterRule] = None,
                  time_out: float = 40.0,
                  boundary: Tuple[int, int, int, int] = None,
                  reposition_pos = None,
                  reposition_time: float = 6.0,
                  do_howl: bool=False
                ) -> bool:
        start = time.time()
        last_move = start
        elapsed = 0
        monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
        if len(monsters) == 0: return True
        Logger.debug(f"Beginning combat against {len(monsters)}...")
        while elapsed < time_out and len(monsters) > 0:
            data = self._api.get_data()
            if data:
                for monster in monsters:
                    monster = self._api.find_monster(monster["id"])
                    if monster:
                        monster_start = time.time()
                        if time.time() - last_move > reposition_time and reposition_pos is not None:
                            Logger.debug("    Stood in one place too long, repositioning")
                            self._pather.traverse(reposition_pos, self, time_out = 3.0)
                            last_move = time.time()
                        else:
                            while monster and monster["dist"] > 3.0 and time.time() - monster_start < 5.0:
                                Logger.debug(f"    Monster {monster['id']} distance is too far ({round(monster['dist'], 2)}), moving closer...")
                                self._pather.move_to_monster(self, monster)
                                last_move = time.time()
                                monster = self._api.find_monster(monster["id"])
                                if do_howl and monster and monster["dist"] <= 3.0:
                                    self.cast_howl()
                            if monster and monster["dist"] <= 3.0 and not self.tele_stomp_monster("berserk", 3.0, monster, max_distance=3):
                                wait(0.1)
            wait(0.1)
            monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
            elapsed = time.time() - start
        self.post_attack()
        Logger.debug(f"    Finished killing mobs, combat took {elapsed} sec")
        return True

    def _kill_superunique(self, name: str = None) -> bool:
        rules = [MonsterRule(names=[name])]
        if type(name) is str:
            rules.append(MonsterRule(names=[name]))
        self._kill_mobs(rules, time_out=20, do_howl=True)
        return True
    
    def kill_uniques(self, pickit=None, time_out: float=15.0, looted_uniques: set=set(), boundary=None) -> bool:
        Logger.debug(f"Beginning combat")
        rules = [
            MonsterRule(auras = ["CONVICTION"]),
            MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE]),
            MonsterRule(monster_types = [MonsterType.UNIQUE]),
            MonsterRule(monster_types = [MonsterType.CHAMPION, MonsterType.GHOSTLY, MonsterType.POSSESSED]),
        ]
        start = time.time()
        game_state = StateMonitor(rules, self._api, False, -1, True, False, None)
        last_move = start
        elapsed = 0
        picked_up_items = 0
        data = game_state._data
        initial_pos = None
        while elapsed < time_out and game_state._dead == 0 and game_state._target is not None:
            if not game_state._ready:
                wait(0.1, 0.12)
            else:
                target_pos = game_state._target_pos
                target_pos = [target_pos[0]-9.5, target_pos[1]-39.5]
                if target_pos is not None and initial_pos is None:
                    initial_pos = np.array(game_state._area_pos) if game_state._area_pos is not None else None
                
                if time.time() - last_move > 6.0:
                    Logger.debug("Stood in one place too long, repositioning")
                    self.reposition(target_pos)
                    last_move = time.time()
                elif game_state._dist > 4:
                    move_pos_screen = self._old_pather._adjust_abs_range_to_screen([target_pos[0], target_pos[1]])
                    move_pos_m = self._screen.convert_abs_to_monitor(move_pos_screen)
                    self.pre_move()
                    self.move(move_pos_m, force_tp=True, force_move=True)
                    last_move = time.time()
                else:
                    self.cast_aoe("howl")
                    self.verify_active_weapon_tab()
                    if not self.tele_stomp_monster("berserk", 2.5, game_state._target): wait(0.1)
            elapsed = time.time() - start
        self.cast_aoe("howl")
        self.do_hork(None, time_out=9, unique_only=True)
        self.post_attack()
        picked_up_items += self.loot_uniques(pickit, time_out, looted_uniques, boundary)
        Logger.debug(f"Finished killing mobs, combat took {elapsed} sec")
        game_state.stop()
        return picked_up_items

    def kill_andariel(self) -> bool:
        rules = [MonsterRule(names=["Andariel"])]
        self._kill_mobs(rules, time_out=40, do_howl=True)
        return True

    def kill_mephisto(self) -> bool:
        rules = [
            MonsterRule(names=["Mephisto"]),
            MonsterRule(monster_types=[MonsterType.SUPER_UNIQUE]),
        ]
        self._kill_mobs(rules, time_out=40)
        return True

    def kill_council(self) -> bool:
        sequence = [
            (10, [MonsterRule(auras = ["CONVICTION"])]),
            (10, [MonsterRule(auras = ["HOLYFREEZE", "HOLY_FREEZE"])]),
            (20, [MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE])]),
            (25, [MonsterRule(names = ["CouncilMember"]), MonsterRule(monster_types = [MonsterType.UNIQUE])]),
        ]
        for time, rules in sequence:
            self._kill_mobs(rules, time_out=time, reposition_pos=(156, 113), boundary=(122, 80, 50, 50))
        return True

    def kill_summoner(self) -> bool:
        return self._kill_superunique("Summoner")

    def kill_pindle(self) -> bool:
        return self._kill_superunique("Pindleskin")

    def kill_nihlathak(self) -> bool:
        return self._kill_superunique("Nihlathak")

    def kill_countess(self) -> bool:
        return self._kill_superunique("Countess")