from distutils.log import Log
import math
import time
from turtle import pos
import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import rotate_vec, unit_vector, wait, point_str
import random
from pathing import Location
import numpy as np
from logger import Logger
from config import Config
from screen import Screen
from template_finder import TemplateFinder
from ui import UiManager
from pathing import OldPather, Location

from d2r.d2r_api import D2rApi
from pathing import Pather
from monsters import sort_and_filter_monsters, CHAMPS_UNIQUES
from monsters import MonsterRule, MonsterType
from obs import ObsRecorder

class HydraSorc(Sorceress):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: D2rApi, obs_recorder: ObsRecorder, old_pather: OldPather, pather: Pather):
        Logger.info("Setting up HydraSorc")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder, pather, old_pather)
        self._old_pather = old_pather
        self._pather = pather

    def _fire_ball(self, cast_pos_abs: tuple[float, float], dist: int = 0):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["fire_ball"]:
            keyboard.send(self._skill_hotkeys["fire_ball"])
        for _ in range(2):
            self._pather.move_mouse_to_abs_pos(cast_pos_abs, dist)
            mouse.press(button="left")
            wait(0.16, 0.23)
            mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _hyrda(self, cast_pos_abs: tuple[float, float], dist: int = 0):
        if not self._skill_hotkeys["hydra"]:
            raise ValueError("You did not set a hotkey for hydra!")
        keyboard.send(self._skill_hotkeys["hydra"])
        self._pather.move_mouse_to_abs_pos(cast_pos_abs, dist)
        Logger.debug(f"Hail Hydra!!!")
        mouse.press(button="right")
        wait(2,3)
        mouse.release(button="right")

    def _kill_super_unique(self, name: str = None, radius: int = 20, reposition_pos: list[tuple[float, float]] = None, min_distance: int = 10):
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

        return self._kill_mobs(rules, time_out=25, reposition_pos=reposition_pos, boundary=boundary, min_distance=min_distance)

    def _kill_mobs(self,
                  prioritize: list[MonsterRule],
                  ignore: list[MonsterRule] = None,
                  time_out: float = 40.0,
                  boundary: tuple[float, float, float, float] = None,
                  reposition_pos: list[tuple[float, float]] = None,
                  min_distance: int = 10,
                ) -> bool:
        
        start = time.time()
        elapsed = 0
        pos_idx = 0
        hydra_time = None
        Logger.debug(f"boundary {boundary}...")
        monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
        if len(monsters) == 0: return True
        Logger.debug(f"Beginning combat against {len(monsters)} monsters...")
        while elapsed < time_out and len(monsters) > 0:
            data = self._api.get_data()
            if data:
                for monster in monsters:
                    data = self._api.get_data()
                    monster = self._api.find_monster(monster["id"])
                    if monster and monster["mode"] != 12:
                        if monster and monster["dist"] <= min_distance and reposition_pos is not None:
                            Logger.debug(f"    Monster {monster['id']} distance is too close ({round(monster['dist'], 2)}), moving pos[{pos_idx}]={reposition_pos[pos_idx]}...")
                            self._pather.traverse(reposition_pos[pos_idx], self, time_out = 3.0)
                            pos_idx += 1
                            if pos_idx >= len(reposition_pos): 
                                pos_idx = 0
                        else:
                            Logger.debug(f"    Monster {monster['id']} distance just right ({round(monster['dist'], 2)}), attacking...")
                            Logger.debug(f"======================================================================")
                            Logger.debug(f"{hydra_time is None}")
                            if hydra_time is not None: Logger.debug(f"{time.time() - hydra_time} > 10 = {time.time() - hydra_time > 10}")
                            if hydra_time is None or time.time() - hydra_time > 10:
                                self._hyrda(cast_pos_abs=monster['position_abs'], dist=monster['dist'])
                                hydra_time = time.time()
                            self._fire_ball(cast_pos_abs=monster['position_abs'], dist=monster['dist'])
                            wait(0.05, 0.07)
                            Logger.debug(f"======================================================================")
                        

            wait(0.1)
            monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
            elapsed = time.time() - start
            Logger.debug(f"    Continuing combat against {len(monsters)} monsters...")
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

        return self._kill_mobs(rules, time_out=25, boundary=boundary, min_distance=0)
        
    def kill_eldritch(self) -> bool:
        self._kill_super_unique("Eldritch", reposition_pos=[[278,733],[296,739]] )
        
    def kill_mephisto(self) -> bool:
        return self._kill_mobs([MonsterRule(names = "Mephisto")], reposition_pos=[[69,82],[69,54]])
        