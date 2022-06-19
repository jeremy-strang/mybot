from operator import is_
import pprint
from typing import Tuple
from constants.roi import Roi
import keyboard
from monsters.monsters import get_closest_monster
from utils.coordinates import world_to_abs
from utils.custom_mouse import mouse
from char import IChar
from char.barbarian.barbarian import Barbarian
from template_finder import TemplateFinder
from ui import UiManager
from pathing import OldPather
from logger import Logger
from screen import Screen
from utils.misc import normalize_text, rotate_vec, unit_vector, wait, is_in_roi, cut_roi, roi_center
import time
from pathing import OldPather, Location
import math
import threading
import numpy as np
import random
import cv2

from d2r.d2r_api import D2rApi
from pathing import Pather
from state_monitor import StateMonitor
from monsters import MonsterRule, MonsterType
from obs import ObsRecorder
from monsters import CHAMPS_UNIQUES, sort_and_filter_monsters

class ZerkerBarb(Barbarian):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: D2rApi, obs_recorder: ObsRecorder, old_pather: OldPather, pather: Pather):
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
        Logger.debug(f"Focusing {len(monsters)} mobs...")
        while elapsed < time_out and len(monsters) > 0:
            data = self._api.data
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
                                self._pather.move_to_monster(self, monster)
                                last_move = time.time()
                                monster = self._api.find_monster(monster["id"])
                                if do_howl and monster and monster["dist"] <= 3.0:
                                    self.cast_howl()
                            if monster and monster["dist"] <= 3.0: # and not self.attack_melee_range("berserk", 3.0, monster, max_distance=3):
                                self.attack_melee_range("berserk", 3.0, monster, max_distance=3)
                                wait(0.1)
            wait(0.1)
            monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
            elapsed = time.time() - start
        self.post_attack()
        Logger.debug(f"    Finished killing mobs, combat took {elapsed} sec")
        return True

    def _kill_mobs_walking(self,
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
        Logger.debug(f"Focusing {len(monsters)} mobs...")
        while elapsed < time_out and len(monsters) > 0:
            data = self._api.data
            if data:
                for monster in sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True):
                    monster = self._api.find_monster(monster["id"])
                    if monster:
                        monster_start = time.time()
                        if time.time() - last_move > reposition_time and reposition_pos is not None:
                            Logger.debug("    Stood in one place too long, repositioning")
                            self._pather.traverse(reposition_pos, self, time_out = 3.0)
                            last_move = time.time()
                        else:
                            while monster and monster["dist"] > 3.0 and time.time() - monster_start < 8.0:
                                self._pather.move_to_monster(self, monster)
                                last_move = time.time()
                                monster = self._api.find_monster(monster["id"])
                                if do_howl and monster and monster["dist"] <= 3.5:
                                    self.cast_howl()
                            data = self._api.data
                            if data and monster and monster["dist"] <= 3.0: # and not self.attack_melee_range("berserk", 3.0, monster, max_distance=3):
                                Logger.debug(f"    Next melee target in ROI {boundary} located at {monster['position_area']}, player location: {data['player_pos_area']}")
                                self.attack_melee_range("berserk", 2.5, monster, max_distance=3)
                                wait(0.1)
                            elif self._api.data is not None and self._api.data["monsters"] is not None:
                                # Try to deal with blocking monsters
                                Logger.debug(f"    Next melee target in ROI {boundary} (due to blockage) located at {monster['position_area']}, player location: {data['player_pos_area']}")
                                closest_monster = get_closest_monster(self._api.data, [MonsterRule(boundary=boundary)])
                                if closest_monster:
                                    self.attack_melee_range("berserk", 2.5, closest_monster, max_distance=8)
                                    wait(0.1)
                            
            wait(0.1)
            monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
            elapsed = time.time() - start
        self.post_attack()
        Logger.debug(f"    Finished killing mobs walking, combat took {elapsed} sec")
        return True

    def _kill_superunique(self, name: str = None) -> bool:
        rules = [MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE])]
        if type(name) is str:
            rules.append(MonsterRule(names=[name]))
        self._kill_mobs(rules, time_out=20, do_howl=True)
        return True
    
    def kill_uniques(self, pickit=None, time_out: float=15.0, looted_uniques: set=set(), boundary=None, min_attack_time: float = 1.5) -> bool:
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
                    if not self.attack_melee_range("berserk", 2.5, game_state._target): wait(0.1)
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
        if self.can_tp:
            return self._kill_council_teleporting()
        return self._kill_council_walking()
    
    def _avoid_durance(self):
        # Hack in case we end up in Durance by accidentally clicking the stairs
        data = self._api.get_data()
        if data is not None and data["current_area"] == "DuranceOfHateLevel1":
            if not self._pather.go_to_area("Travincal", "Travincal", True, time_out=5.0):
                self._pather.go_to_area("Travincal", "Travincal", True, time_out=5.0)
                wait(0.15, 0.20)
                self._pather.walk_to_position((157, 100), time_out=8, step_size=5)

    def _kill_council_teleporting(self) -> bool:
        sequence = [
            (15, "conviction", [MonsterRule(auras = ["CONVICTION"])]),
            (15, "holy freeze", [MonsterRule(auras = ["HOLYFREEZE", "HOLY_FREEZE"])]),
            (25, "super unique", [MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE])]),
            (40, "council members/unique", [MonsterRule(names = ["CouncilMember"]), MonsterRule(monster_types = [MonsterType.UNIQUE])]),
        ]
        for time, rule_desc, rules in sequence:
            self._kill_mobs(rules, time_out=time, reposition_pos=(156, 113), boundary=(122, 80, 50, 50))
        # Hork hork hork
        horkable_ids = set()
        if self._api.data:
            for m in self._api.data["monsters"]:
                if "councilmember" in normalize_text(m["name"]) and m["is_targetable_corpse"]:
                    horkable_ids.add(m["id"])
        Logger.debug(f"Number of horkable Council Member corpses: {len(horkable_ids)}")
        self.do_hork(names=["CouncilMember"], boundary=[122, 80, 50, 50])
        return True
    
    def _kill_council_walking(self) -> bool:
        Logger.debug(f"Beginning combat with Council Members (walking)...")
        sequence = [
            (10, "conviction", [MonsterRule(auras = ["CONVICTION"])]),
            (10, "holy freeze", [MonsterRule(auras = ["HOLYFREEZE", "HOLY_FREEZE"])]),
            (15, "super unique", [MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE])]),
            (20, "council members/unique", [MonsterRule(names = ["CouncilMember"]), MonsterRule(monster_types = [MonsterType.UNIQUE])]),
        ]
        roi_tups = [
            ((157, 100), "stairs", Roi.TRAV_STAIRS),
            ((144, 113), "patio-left", Roi.TRAV_PATIO_LEFT),
            ((157, 100), "inner-mid", Roi.TRAV_INNER_MID), 
            ((144,  94), "inner-left", Roi.TRAV_INNER_LEFT),
            ((157, 100), "full", Roi.TRAV_FULL),
        ]
        Logger.debug("Killing Council...")
        for pos_area, section_desc, roi in roi_tups:
            wait(0.15)
            for time_out, rule_desc, rules in sequence:
                monsters = sort_and_filter_monsters(self._api.data, rules, None, roi, ignore_dead=True)
                if len(monsters) > 0:
                    Logger.debug(f"    Focusing {len(monsters)} in the {section_desc} section of Trav, prioritizing {rule_desc} mobs")
                    data = self._api.data
                    if data and not is_in_roi(roi, data["player_pos_area"]):
                        if not self._pather.walk_to_position((157, 100), time_out=8, step_size=5):
                            self._avoid_durance()
                    if not self._pather.walk_to_position(pos_area, time_out=3, step_size=5):
                        self._avoid_durance()
                    self._kill_mobs_walking(rules, time_out=time_out, boundary=roi, reposition_time=8, reposition_pos=(157, 100))
                    self.post_attack()
                    self._avoid_durance()
        # Hork hork hork
        hork_roi_tups = [
            ((157, 100), Roi.TRAV_INNER_MID, "inner-mid"),
            ((144, 94), Roi.TRAV_INNER_LEFT, "inner-left"), 
            ((157, 100), Roi.TRAV_STAIRS, "stairs"),
            ((144, 113), Roi.TRAV_PATIO_LEFT, "patio-left"),
        ]
        Logger.debug("Horking Trav...")
        horkable_ids = set()
        for pos_area, roi, section in hork_roi_tups:
            Logger.debug(f"    Horking the {section} section of Trav")
            wait(0.15)
            data = self._api.data
            monsters_in_roi = sort_and_filter_monsters(data, [MonsterRule(names = ["CouncilMember"])], None, roi, ignore_dead=False)
            roi_corpses = 0
            for m in monsters_in_roi:
                if m["is_targetable_corpse"]:
                    roi_corpses += 1
                    horkable_ids.add(m["id"])
            if roi_corpses == 0:
                continue
            if data and not is_in_roi(roi, data["player_pos_area"]):
                self._pather.walk_to_position((157, 100), time_out=5, step_size=5)
            self._pather.walk_to_position(pos_area, 5.0, step_size=5)
            self.do_hork(names=["CouncilMember"], boundary=roi)
        Logger.debug(f"Number of horkable Council Member corpses: {len(horkable_ids)}")
        self._pather.walk_to_position((157, 101), 5.0, step_size=5)
        return True

    def kill_summoner(self) -> bool:
        return self._kill_superunique("Summoner")

    def kill_nihlathak(self) -> bool:
        return self._kill_superunique("Nihlathak")

    def kill_countess(self) -> bool:
        return self._kill_superunique("Countess")

    def kill_shenk(self) -> bool:
        return self._kill_superunique("Shenk")

    def kill_eldritch(self) -> bool:
        return self._kill_superunique("Eldritch")

    def kill_pindleskinskin(self) -> bool:
        return self._kill_superunique("Pindleskin")
