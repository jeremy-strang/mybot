
import keyboard
from utils.custom_mouse import mouse
from char.sorceress import Sorceress
from template_finder import TemplateFinder
from ui import UiManager
from pathing import OldPather
from logger import Logger
from screen import Screen
from utils.misc import wait, point_str
from monsters import sort_and_filter_monsters
import time
from pathing import OldPather

from d2r.d2r_api import D2rApi
from pathing import Pather
from monsters import MonsterRule, MonsterType
from obs import ObsRecorder

class NovaSorc(Sorceress):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: D2rApi, obs_recorder: ObsRecorder, old_pather: OldPather, pather: Pather):
        Logger.info("Setting up Nova Sorc")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder, pather, old_pather)
        self._old_pather = old_pather
        self._pather = pather

    def get_cast_frames(self):
        fcr = self.get_fcr()
        frames = 15
        if fcr >= 125: frames = 9
        if fcr >= 75: frames = 10
        elif fcr >= 48: frames = 11
        elif fcr >= 30: frames = 12
        elif fcr >= 18: frames = 13
        elif fcr >= 9: frames = 14
        Logger.debug(f"FCR recalculated to be FCR: {fcr} ({frames} frames)")
        return frames

    def _nova(self, time_in_s: float):
        if not self._skill_hotkeys["nova"]:
            raise ValueError("You did not set nova hotkey!")
        keyboard.send(self._skill_hotkeys["nova"])
        wait(0.05, 0.1)
        start = time.time()
        while (time.time() - start) < time_in_s:
            wait(0.03, 0.04)
            mouse.press(button="right")
            wait(0.12, 0.2)
            mouse.release(button="right")

    def kill_pindleskin(self) -> bool:
        return self._kill_super_unique("Pindleskin", self._cast_duration * 7)

    def kill_eldritch(self) -> bool:
        return self._kill_super_unique("Eldritch", self._cast_duration * 7)

    def kill_shenk(self):
        return self._kill_super_unique("Shenk", self._cast_duration * 7)

    def kill_mephisto(self) -> bool:
        return self._kill_super_unique("Mephisto", radius=25)

    def kill_andariel(self) -> bool:
        return self._kill_super_unique("Andariel", radius=25)

    def kill_summoner(self) -> bool:
        return self._kill_super_unique("Summoner", radius=15)

    def kill_nihlathak(self) -> bool:
        return self._kill_super_unique("Nihlathak", radius=20)

    def kill_countess(self) -> bool:
        return self._kill_super_unique("Countess", radius=20)

    def kill_council(self) -> bool:
        if not self._do_pre_move:
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.05, 0.10)
        sequence = [
            (10, [MonsterRule(auras = ["CONVICTION"])]),
            (10, [MonsterRule(auras = ["HOLYFREEZE", "HOLY_FREEZE"])]),
            (20, [MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE])]),
            (25, [MonsterRule(names = ["CouncilMember"]), MonsterRule(monster_types = [MonsterType.UNIQUE])]),
        ]
        for time, rules in sequence:
            self._kill_mobs(rules, time_out=time, reposition_pos=(156, 113), boundary=(122, 80, 50, 50))
        wait(0.05, 0.08)
        return True

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
        # for m in monsters:
        #     if "conviction" in m["type"] or "cursed" in m["type"]:
        #         self._api.write_data_to_file(file_prefix="monster_type_check")
        #         break
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
                            while monster and monster["dist"] > 3 and time.time() - monster_start < 5.0:
                                Logger.debug(f"    Monster {monster['id']} distance is too far ({round(monster['dist'], 2)}), moving closer...")
                                self._pather.move_to_monster(self, monster)
                                last_move = time.time()
                                monster = self._api.find_monster(monster["id"])
                            if monster and monster["dist"] <= 3:
                                wait(0.05, 0.07)
                                if not self.tele_stomp_monster("nova", 4.0, monster, mouse_button="right", max_distance=5, min_attack_time=min_attack_time):
                                    wait(0.1)
            wait(0.1)
            monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
            elapsed = time.time() - start
        self.post_attack()
        Logger.debug(f"    Finished killing mobs, combat took {elapsed} sec")
        return True
