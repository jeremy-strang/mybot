from ast import Tuple
from sre_parse import State
import keyboard
from char.skill import Skill
from utils.coordinates import world_to_abs
from utils.custom_mouse import mouse
from char import IChar
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

from d2r_mem.d2r_mem_api import D2rMemApi
from pathing import Pather
from monsters import MonsterRule, MonsterType
from obs import ObsRecorder

class Hammerdin(IChar):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: D2rMemApi, obs_recorder: ObsRecorder, old_pather: OldPather, pather: Pather):
        Logger.info("Setting up Hammerdin")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder, pather, old_pather)
        self._old_pather = old_pather
        self._pather = pather
        self._do_pre_move = True
        if not self._skill_hotkeys["teleport"]:
            self._do_pre_move = False

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

    def _cast_hammers(self, time_in_s: float, aura: str = "concentration"):
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
            wait(0.05, 0.1)
            keyboard.send(self._char_config["stand_still"], do_release=False)
            wait(0.05, 0.1)
            if self._skill_hotkeys["blessed_hammer"]:
                keyboard.send(self._skill_hotkeys["blessed_hammer"])
            wait(0.05, 0.1)
            start = time.time()
            while (time.time() - start) < time_in_s:
                wait(0.06, 0.08)
                mouse.press(button="left")
                wait(0.1, 0.2)
                mouse.release(button="left")
            wait(0.01, 0.05)
            keyboard.send(self._char_config["stand_still"], do_press=False)

    def _cast_holy_bolt(self, time_in_s: float, abs_screen_pos: tuple[float, float]):
        if self._skill_hotkeys["holy_bolt"]:
            keyboard.send(self._skill_hotkeys["concentration"])
            keyboard.send(self._skill_hotkeys["holy_bolt"])
            wait(0.05)
            m = self._screen.convert_abs_to_monitor(abs_screen_pos)
            mouse.move(*m, delay_factor=[0.2, 0.4])
            keyboard.send(self._char_config["stand_still"], do_release=False)
            start = time.time()
            while (time.time() - start) < time_in_s:
                wait(0.06, 0.08)
                mouse.press(button="left")
                wait(0.1, 0.2)
                mouse.release(button="left")
            keyboard.send(self._char_config["stand_still"], do_press=False)

    def pre_buff(self, switch_back=True):
        if self._char_config["cta_available"]:
            self._pre_buff_cta()
        keyboard.send(self._skill_hotkeys["holy_shield"])
        wait(0.04, 0.1)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.06)

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use vigor if set
        should_cast_vigor = self._skill_hotkeys["vigor"] and not self._ui_manager.is_right_skill_selected(Skill.Vigor)
        can_teleport = self.can_tp and self._ui_manager.is_right_skill_active()
        if should_cast_vigor and not can_teleport:
            keyboard.send(self._skill_hotkeys["vigor"])
            wait(0.15, 0.25)

    def post_attack(self) -> bool:
        mouse.release(button="left")
        wait(0.02, 0.4)
        keyboard.release(self._char_config["stand_still"]) 
        wait(0.02, 0.4)
        return True

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = self._screen.convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_hammers(atk_len)

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
        if self.can_tp:
            return self._kill_mobs(rules, time_out=25, boundary=boundary, min_attack_time=min_attack_time)
        else:
            return self._kill_mobs_walking(rules, time_out=25, boundary=boundary, min_attack_time=min_attack_time)

    def kill_pindleskin(self) -> bool:
        return self._kill_super_unique("Pindleskin", self._cast_duration * 7)

    def kill_eldritch(self) -> bool:
        return self._kill_super_unique("Eldritch", self._cast_duration * 7)

    def kill_shenk(self):
        return self._kill_super_unique("Shenk", self._cast_duration * 7)

    def kill_council(self) -> bool:
        if not self._do_pre_move:
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.05, 0.10)
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        atk_len = self._char_config["atk_len_trav"]
        # Here we have two different attack sequences depending if tele is available or not
        if self.can_tp:
            self._kill_council_with_tp()
        else:
            self._kill_council_walking()
        keyboard.send(self._skill_hotkeys["concentration"])
        wait(0.05, 0.08)
        return True

    # Chaos Sanctuary, Seal Bosses (a = Vizier, b = De Seis, c = Infector) & Diablo
    def kill_cs_trash(self) -> bool:
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_cs_trashmobs"] * 0.4)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.3)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.4)
        wait(0.1, 0.15)
        self._cast_hammers(2, "redemption")
        #self._cast_hammers(1.2, "cleansing") # would make sense to add cleansing to CS, due to the tons of curses (that also interfere with the seal logic)
        return True
        
    def kill_cs_trash_pentagram(self) -> bool:
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_cs_trashmobs"] * 0.2)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.2)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.1)
        wait(0.1, 0.15)
        self._cast_hammers(2, "redemption")
        #self._cast_hammers(1.2, "cleansing") # would make sense to add cleansing to CS, due to the tons of curses (that also interfere with the seal logic)
        return True
    
    def kill_vizier(self, nodes1: list[int], nodes2: list[int]) -> bool:
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.4)
        self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"] * 0.4)
        self._cast_hammers(1, "redemption")
        self._old_pather.traverse_nodes(nodes1, self)
        self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.4)
        self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"] * 0.4)
        self._cast_hammers(1, "redemption")
        self._old_pather.traverse_nodes(nodes2, self)
        self._move_and_attack((0, 0), self._char_config["atk_len_diablo_vizier"])
        wait(0.1, 0.15)
        self._cast_hammers(2, "redemption")
        return True

    def kill_deseis(self, nodes1: list[int], nodes2: list[int], nodes3: list[int]) -> bool:
        """ WIZ VERSION - NOT STABLE FOR CTHU
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._move_and_attack((30, 30), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._move_and_attack((-60, -0), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._cast_hammers(1, "redemption")
        self._old_pather.traverse_nodes(nodes1, self)
        self._move_and_attack((0, -60), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._move_and_attack((60, 0), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._cast_hammers(1, "redemption")
        self._old_pather.traverse_nodes(nodes2, self)
        self._move_and_attack((-30, -30), self._char_config["atk_len_diablo_deseis"] * 0.5)
        self._cast_hammers(1, "redemption")
        self._old_pather.traverse_nodes(nodes3, self)
        self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"])
        wait(0.1, 0.15)
        self._cast_hammers(2, "redemption") 
        return True
        """
        #CTHU VERSION
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._move_and_attack((30, 15), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._cast_hammers(1, "redemption")
        self._old_pather.traverse_nodes(nodes1, self)
        self._move_and_attack((30, 15), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._cast_hammers(1, "redemption")
        self._old_pather.traverse_nodes(nodes2, self)
        self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"] * 0.5)
        self._cast_hammers(1, "redemption")
        self._old_pather.traverse_nodes(nodes3, self)
        self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"])
        wait(0.1, 0.15)
        self._cast_hammers(2, "redemption") 
        return True

    def kill_infector(self) -> bool:
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_diablo_infector"] * 0.4)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), self._char_config["atk_len_diablo_infector"] * 0.3)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, -15), self._char_config["atk_len_diablo_infector"] * 0.4)
        wait(0.1, 0.15)
        self._cast_hammers(1.2, "redemption") 
        return True

    def kill_diablo(self) -> bool:
        rules = [
            MonsterRule(names = ["Diablo"]),
            MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE]),
        ]
        self._kill_mobs(rules, time_out=30)
        return True

    def baal_idle(self, monster_filter: list[str], start_time: float) -> tuple[bool, list[str]]:
        found_monsters = []
        stop_hammers = False
        def pre_cast_hammers():
            while not stop_hammers:
                self._cast_hammers(1.5)
        hammer_thread = threading.Thread(target=pre_cast_hammers)
        hammer_thread.name = 'mybot_subthread_hdin_baal_idle_pre_cast_hammers'
        hammer_thread.daemon = True

        throne_area = [70, 0, 50, 95]
        if not self._pather.traverse((93, 26), self):
            return False, found_monsters
        aura = "redemption"
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
        start = time.time()
        while time.time() - start < 50:
            data = self._api.get_data()
            if data is not None:
                 for m in data["monsters"]:
                    if m['mode'] != 12:
                        area_pos = m["position"] - data["area_origin"]
                        proceed = True
                        if monster_filter is not None:
                            proceed = any(m["name"].startswith(startstr) for startstr in monster_filter)
                        if is_in_roi(throne_area, area_pos) and proceed:
                            found_monsters.append(m["name"])
                            Logger.info("Found wave, attack")
                            stop_hammers = True
                            if hammer_thread.is_alive():
                                hammer_thread.join()
                            return True, found_monsters
            elapsed = time.time() - start_time
            if elapsed > 5.5:
                if not hammer_thread.is_alive():
                    hammer_thread.start()
            time.sleep(0.1)
        return False, found_monsters

    def clear_throne(self, full = False, monster_filter = None, baal_wave = 0) -> bool:
        throne_area = [70, 0, 50, 95 if full else 65]

        def _should_focus_mummies(monsters):
            return baal_wave == 2 and any(x["name"].startswith("BaalSubjectMummy") and x["mode"] != 12 for x in monsters)

        aura_after_battle = "redemption"
        success = False
        start = time.time()
        prev_position = None
        prev_pos_counter = time.time()
        num_repositions = 0
        time_out = 100 if baal_wave == 2 else 80
        while time.time() - start < time_out:
            data = self._api.get_data()
            found_a_monster = False
            if data is not None: 
                monsters = data["monsters"]
                focus_mummies = _should_focus_mummies(monsters)
                for i in range(len(monsters)):
                    m = monsters[i]
                    if m['mode'] != 12:
                        if i > 0:
                            fresh_data = self._api.get_data()
                            fresh_m = next(filter(lambda x: x["id"] == m["id"], fresh_data["monsters"]), m)
                            if fresh_m is not None:
                                m = fresh_m
                                focus_mummies = _should_focus_mummies(fresh_data["monsters"])
                        area_pos = m["position"] - data["area_origin"]
                        proceed = True
                        if monster_filter is not None:
                            proceed = any(m["name"].startswith(startstr) for startstr in monster_filter)
                        if is_in_roi(throne_area, area_pos) and proceed:
                            m_is_mummy = m["name"].startswith("BaalSubjectMummy")
                            dist = math.dist(area_pos, data["player_pos_area"])
                            if m_is_mummy:
                                Logger.debug("Fighting mummy: {0}, id: {1}, distance: {2}".format(m["name"], m["id"], dist))
                                if dist >= 5:
                                    self._pather.traverse(area_pos, self, randomize=12)
                                    dist = math.dist(area_pos, data["player_pos_area"])
                                if dist < 5:
                                    self.tele_stomp_monster("holy_bolt", self._cast_duration * 5, m)
                                aura_after_battle = "cleansing"
                                num_repositions = 0
                            elif not focus_mummies:
                                if dist >= 5:
                                    self._pather.traverse(area_pos, self, randomize=12)
                                    dist = math.dist(area_pos, data["player_pos_area"])
                                if dist < 5:
                                    self.tele_stomp_monster("blessed_hammer", self._cast_duration * 5, m)
                                num_repositions = 0
                            found_a_monster = True
                            break
                if prev_position is None or not np.array_equal(prev_position, data["player_pos_area"]):
                    prev_pos_counter = time.time()
                if time.time() - prev_pos_counter > (3.8 if baal_wave != 2 else 6):
                    Logger.debug("Reposition for next attack (" + str(num_repositions) + ")")
                    if baal_wave == 2 and num_repositions == 2:
                        self._pather.traverse((95, 55), self)
                    elif baal_wave == 2 and num_repositions == 3:
                        self._pather.traverse((101, 3), self)
                    elif baal_wave == 2 and num_repositions == 4:
                        self._pather.traverse((86, 3), self)
                    else:
                        m_pos = self._screen.convert_abs_to_monitor((random.randint(-100, 100), random.randint(-100, 100)))
                        self.pre_move()
                        self.move(m_pos)
                    num_repositions += 1
                prev_position = data["player_pos_area"]
            if not found_a_monster:
                success = True
                break
        if aura_after_battle in self._skill_hotkeys and self._skill_hotkeys[aura_after_battle]:
            keyboard.send(self._skill_hotkeys[aura_after_battle])
        return success

    def kill_baal(self) -> bool:
        rules = [
            MonsterRule(names = ["BaalCrab"]),
            MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE]),
        ]
        ignore = [
            MonsterRule(names = ["BaalCrabClone"]),
        ]
        self._kill_mobs(rules, ignore, time_out=90)
        return True

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

    def _kill_council_with_tp(self):
        sequence = [
            (10, [MonsterRule(auras = ["CONVICTION"])]),
            (10, [MonsterRule(auras = ["HOLYFREEZE", "HOLY_FREEZE"])]),
            (20, [MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE])]),
            (25, [MonsterRule(names = ["CouncilMember"]), MonsterRule(monster_types = [MonsterType.UNIQUE])]),
        ]
        for time, rules in sequence:
            self._kill_mobs(rules, time_out=time, reposition_pos=(156, 113), boundary=(122, 80, 50, 50))
        return True

    def _kill_council_walking(self):
        Logger.debug(f"Beginning combat with Council Members (walking)...")
        rules = [
            MonsterRule(auras = ["CONVICTION"]),
            MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE, MonsterType.UNIQUE]),
            MonsterRule(names = ["CouncilMember"]),
        ]
        roi_tups = [
            ((157, 113), Roi.TRAV_STAIRS), 
            ((141, 115), Roi.TRAV_PATIO), 
            ((124, 109), Roi.TRAV_CORNER),
            ((142,  92), Roi.TRAV_FULL)
        ]
        for pos_area, roi in roi_tups:
            monsters = sort_and_filter_monsters(self._api.data, rules, None, roi, ignore_dead=True)
            if len(monsters) > 0:
                self._pather.walk_to_position(pos_area, time_out=4)
                self._cast_hammers((self._cast_duration - 0.01) * 4)
                self._kill_mobs_walking(rules, time_out=10, boundary=roi)
                self.post_attack()
        self._pather.walk_to_position((157, 98), 3.0)
        return True

    def kill_blocking_mobs(self) -> bool:
        Logger.info(f"    Monsters were found blocking the click target, killing them...")
        boundary = None
        if self._api.data:
            player_pos = self._api.data["player_pos_area"]
            boundary = [player_pos[0] - 10, player_pos[1] - 10, 20, 20]
        return self._kill_mobs(None, None, 10, boundary=boundary, min_attack_time=2.5)

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
                                keyboard.send(self._skill_hotkeys["concentration"])
                                wait(0.05, 0.07)
                                if not self.tele_stomp_monster("blessed_hammer", 3.0, monster, max_distance=5, min_attack_time=min_attack_time):
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
                  boundary: Tuple = None,
                  reposition_pos = None,
                  reposition_time: float = 7.0,
                  min_attack_time: float = 0,
                ) -> bool:
        start = time.time()
        last_move = start
        elapsed = 0
        monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
        if len(monsters) == 0: return True
        Logger.debug(f"Beginning combat (walking) against {len(monsters)} monsters...")
        while elapsed < time_out and len(monsters) > 0:
            for monster in monsters:
                monster = self._api.find_monster(monster["id"])
                if monster:
                    monster_start = time.time()
                    if time.time() - last_move > reposition_time and reposition_pos is not None:
                        Logger.debug("    Stood in one place too long, repositioning")
                        self._pather.walk_to_position(reposition_pos, time_out = 2)
                        last_move = time.time()
                    else:
                        while monster and monster["dist"] > 6 and time.time() - monster_start < 5.0:
                            Logger.debug(f"    Monster {monster['id']} distance is too far ({round(monster['dist'], 2)}), moving closer...")
                            self._pather.move_to_monster(self, monster)
                            last_move = time.time()
                            wait(0.1, 0.15)
                            monster = self._api.find_monster(monster["id"])
                        if monster is not None and monster["mode"] != 12:
                            keyboard.send(self._skill_hotkeys["concentration"])
                            wait(0.04, 0.05)
                            self._cast_hammers(max(self._cast_duration * 4, min_attack_time))
            wait(0.1)
            monsters = sort_and_filter_monsters(self._api.data, prioritize, ignore, boundary, ignore_dead=True)
            elapsed = time.time() - start
        self.post_attack()
        Logger.debug(f"    Finished killing mobs, combat took {elapsed} sec")
        return True

    def kill_uniques(self, pickit=None, time_out: float=15.0, looted_uniques: set=set(), boundary=None, min_attack_time: float = 1.5):
        start = time.time()
        rules = [
            MonsterRule(auras = ["CONVICTION"]),
            MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE]),
            MonsterRule(monster_types = [MonsterType.UNIQUE]),
            MonsterRule(monster_types = [MonsterType.CHAMPION, MonsterType.GHOSTLY, MonsterType.POSSESSED]),
        ]
        last_move = start
        elapsed = 0
        picked_up_items = 0
        monsters = sort_and_filter_monsters(self._api.data, rules, None, boundary, ignore_dead=True)
        Logger.debug(f"Beginning combat (tele stomping) against {len(monsters)} monsters...")
        while elapsed < time_out and len(monsters) > 0:
            if self._api.data:
                for monster in monsters:
                    monster = self._api.find_monster(monster["id"])
                    if monster:
                        monster_start = time.time()
                        if time.time() - last_move > 6.0:
                            Logger.debug("    Stood in one place too long, repositioning")
                            self.reposition()
                            last_move = time.time()
                        else:
                            while monster and monster["dist"] > 3 and time.time() - monster_start < 5.0:
                                Logger.debug(f"    Monster {monster['id']} distance is too far ({round(monster['dist'], 2)}), moving closer...")
                                self._pather.move_to_monster(self, monster)
                                last_move = time.time()
                                monster = self._api.find_monster(monster["id"])
                            if monster and monster["dist"] <= 3:
                                keyboard.send(self._skill_hotkeys["concentration"])
                                wait(0.07, 0.09)
                                nearby = len(list(filter(lambda m: m["dist"] < 15, self._api.data["monsters"])))
                                if self.tele_stomp_monster("blessed_hammer", self._cast_duration * 8, monster, max_distance=5, stop_when_dead=nearby < 5, min_attack_time=min_attack_time):
                                    picked_up_items += self.loot_uniques(pickit, time_out, looted_uniques, boundary)
                                wait(0.1)
                                last_move = time.time()
            wait(0.1)
            monsters = sort_and_filter_monsters(self._api.data, rules, None, boundary, ignore_dead=True)
            elapsed = time.time() - start
        self.post_attack()
        picked_up_items += self.loot_uniques(pickit, time_out, looted_uniques, boundary)
        Logger.debug(f"Finished killing uniques, combat took {round(elapsed, 2)} sec")
        return picked_up_items
