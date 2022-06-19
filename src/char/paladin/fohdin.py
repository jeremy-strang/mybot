from ast import Tuple
from sre_parse import State
from d2r.d2r import TOWNS
import keyboard
from char.skill import Skill
from utils.coordinates import world_to_abs
from utils.custom_mouse import mouse
from char.paladin import Paladin
from template_finder import TemplateFinder
from ui import UiManager
from pathing import OldPather
from logger import Logger
from screen import Screen
from utils.misc import rotate_vec, unit_vector, wait, is_in_roi, point_str
from monsters import sort_and_filter_monsters, get_unlooted_monsters, CHAMPS_UNIQUES
from constants import Roi
import time
from pathing import OldPather, Location
import math
import threading
import numpy as np
import random

from d2r.d2r_api import D2rApi
from pathing import Pather
from monsters import MonsterRule, MonsterType
from obs import ObsRecorder

class FoHdin(Paladin):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: D2rApi, obs_recorder: ObsRecorder, old_pather: OldPather, pather: Pather):
        Logger.info("Setting up FoHdin")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder, pather, old_pather)
        self._old_pather = old_pather
        self._pather = pather
        self._do_pre_move = True
        if not self._skill_hotkeys["teleport"]:
            self._do_pre_move = False

    def _cast_foh(self, cast_pos_abs: tuple[float, float], aura: str = "conviction"):
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
        if self._skill_hotkeys["foh"]:
            keyboard.send(self._skill_hotkeys["foh"])
            wait(0.05)
            m = self._screen.convert_abs_to_monitor(cast_pos_abs)
            mouse.move(*m, delay_factor=[0.2, 0.4])
            keyboard.send(self._char_config["stand_still"], do_release=False)
            wait(0.06, 0.08)
            mouse.press(button="left")
            wait(0.1, 0.2)
            mouse.release(button="left")
            keyboard.send(self._char_config["stand_still"], do_press=False)

    def _cast_holy_bolt(self, cast_pos_abs: tuple[float, float], aura: str = "redemption"):
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
        if self._skill_hotkeys["holy_bolt"]:
            keyboard.send(self._skill_hotkeys["holy_bolt"])
            wait(0.05)
            m = self._screen.convert_abs_to_monitor(cast_pos_abs)
            mouse.move(*m, delay_factor=[0.2, 0.4])
            keyboard.send(self._char_config["stand_still"], do_release=False)
            wait(0.06, 0.08)
            mouse.press(button="left")
            wait(0.1, 0.2)
            mouse.release(button="left")
            keyboard.send(self._char_config["stand_still"], do_press=False)

    def _kill_super_unique(self, name: str = None, radius: int = 20, min_attack_time: float = 0):
        center_pos = None
        boss = self._api.find_monster_by_name(name) if name is not None else None
        if not boss:
            bosses = self._api.find_monsters_by_type(MonsterType.SUPER_UNIQUE)
            if len(bosses) > 0:
                boss = bosses[0]
        if boss:
            center_pos = boss["position_area"]
            Logger.info(f"Killing super unique '{boss['name']}', id: {boss['id']}, position: {point_str(boss['position_area'])}")
        elif self._api.data:
            center_pos = self._api.data["player_pos_area"]
        boundary = [center_pos[0] - radius, center_pos[1] - radius, radius * 2, radius * 2] if center_pos is not None else None
        rules = [
            MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE]),
            MonsterRule(monster_types = [MonsterType.UNIQUE]),
        ]
        if name is not None:
            rules.append(MonsterRule(names = name))

        return self._kill_mobs(rules, time_out=25, boundary=boundary, min_attack_time=min_attack_time)

    def _kill_mobs(self,
                  prioritize: list[MonsterRule],
                  ignore: list[MonsterRule] = None,
                  time_out: float = 40.0,
                  boundary: tuple[float, float, float, float] = None,
                  reposition_pos: tuple[float, float] = None,
                  reposition_time: float = 7.0,
                  min_attack_time: float = 0,
                ) -> bool:
        start = time.time()
        last_move = start
        elapsed = 0
        monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
        if len(monsters) == 0: return True
        Logger.debug(f"Beginning combat against {len(monsters)} monsters...")
        while elapsed < time_out and len(monsters) > 0:
            data = self._api.get_data()
            if data:
                for monster in monsters:
                    monster = self._api.find_monster(monster["id"])
                    if monster:
                        self._cast_foh(cast_pos_abs=monster['position_abs'])
                        # self._cast_holy_bolt(cast_pos_abs=monster['position_abs'])
            wait(0.1)
            monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
            elapsed = time.time() - start
        self.post_attack()
        Logger.debug(f"    Finished killing mobs, combat took {elapsed} sec")
        return True

    def kill_pindleskin(self) -> bool:
        radius = 20
        name = "Pindleskin"
        center_pos = None
        boss = self._api.find_monster_by_name(name) if name is not None else None
        if not boss:
            bosses = self._api.find_monsters_by_type(MonsterType.SUPER_UNIQUE)
            if len(bosses) > 0:
                boss = bosses[0]
        if boss:
            center_pos = boss["position_area"]
            Logger.info(f"Killing super unique '{boss['name']}', id: {boss['id']}, position: {point_str(boss['position_area'])}")
        elif self._api.data:
            center_pos = self._api.data["player_pos_area"]
        boundary = [center_pos[0] - radius, center_pos[1] - radius, radius * 2, radius * 2] if center_pos is not None else None
        rules = [
            MonsterRule(names = "DefiledWarrior"),
            MonsterRule(names = name),
        ]

        return self._kill_mobs(rules, time_out=25, boundary=boundary)

