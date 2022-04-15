import time
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

from d2r_mem.d2r_mem_api import D2rMemApi
from pathing import Pather
from monsters import sort_and_filter_monsters, CHAMPS_UNIQUES
from monsters import MonsterRule, MonsterType
from obs import ObsRecorder

class BlizzSorc(Sorceress):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: D2rMemApi, obs_recorder: ObsRecorder, old_pather: OldPather, pather: Pather):
        Logger.info("Setting up Blizz Sorc")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder, pather, old_pather)
        self._old_pather = old_pather
        self._pather = pather

    def get_cast_frames(self):
        fcr = self.get_fcr()
        Logger.debug(f"Detected player FCR: {fcr}")
        if fcr >= 200: return 7
        if fcr >= 105: return 8
        if fcr >= 63: return 9
        if fcr >= 37: return 10
        if fcr >= 20: return 11
        if fcr >= 9: return 12
        return 13

    def _ice_blast(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), dist: int = 0):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["ice_blast"]:
            keyboard.send(self._skill_hotkeys["ice_blast"])
        for _ in range(5):
            self._pather.move_mouse_to_abs_pos(cast_pos_abs, dist)
            mouse.press(button="left")
            wait(delay[0], delay[1])
            mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _blizzard(self, cast_pos_abs: tuple[float, float], dist: int = 0):
        if not self._skill_hotkeys["blizzard"]:
            raise ValueError("You did not set a hotkey for blizzard!")
        keyboard.send(self._skill_hotkeys["blizzard"])
        self._pather.move_mouse_to_abs_pos(cast_pos_abs, dist)
        click_tries = random.randint(2, 4)
        for _ in range(click_tries):
            mouse.press(button="right")
            wait(0.09, 0.12)
            mouse.release(button="right")

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
                  static: int = 0,
                ) -> bool:
        min_distance = 10
        max_distance = 30
        kite_dist = 5
        start = time.time()
        last_move = start
        elapsed = 0
        casted_static = static
        monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
        if len(monsters) == 0: return True
        Logger.debug(f"Beginning combat against {len(monsters)} monsters...")
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
                            while monster and monster["dist"] > max_distance and time.time() - monster_start < 5.0:
                                Logger.debug(f"    Monster {monster['id']} distance is too far ({round(monster['dist'], 2)}), moving closer...")
                                self._pather.move_to_monster(self,monster)
                                last_move = time.time()
                                monster = self._api.find_monster(monster["id"])
                            if monster and monster["dist"] <= max_distance and monster["dist"] > min_distance:
                                Logger.debug(f"    Monster {monster['id']} distance just right ({round(monster['dist'], 2)}), attacking...")
                                # if not casted_static: 
                                #     self._cast_static(3.0)
                                #     casted_static=1
                                self._blizzard(cast_pos_abs=monster['position_abs'], dist=monster['dist'])
                                self._ice_blast(cast_pos_abs=monster['position_abs'], dist=monster['dist'])
                                wait(0.05, 0.07)
                            elif monster and monster["dist"] <= min_distance:
                                Logger.debug(f"    Monster {monster['id']} distance is too close ({round(monster['dist'], 2)}), moving farther...")
                                rot_deg = random.randint(-180,180)
                                tele_pos_abs = unit_vector(rotate_vec(monster['position_area'], rot_deg)) * 320 * kite_dist
                                tele_pos_abs = self._pather._adjust_abs_range_to_screen([tele_pos_abs[0],tele_pos_abs[1]])
                                pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                                self.pre_move()
                                self.move(pos_m)
            wait(0.1)
            monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
            elapsed = time.time() - start
        self.post_attack()
        Logger.debug(f"    Finished killing mobs, combat took {elapsed} sec")
        return True

    def kill_pindleskin(self) -> bool:
        return self._kill_super_unique("Pindleskin")

    def kill_mephisto(self) -> bool:
        return self._kill_super_unique("Mephisto", radius=25)

    def kill_andariel(self) -> bool:
        return self._kill_super_unique("Andariel", radius=25)

    def kill_summoner(self) -> bool:
        return self._kill_super_unique("Summoner", radius=15)

    def kill_eldritch(self) -> bool:
        return self._kill_super_unique("Eldritch", radius=20)