from sre_parse import State
import keyboard
from utils.coordinates import world_to_abs
from utils.custom_mouse import mouse
from char import IChar, CharacterCapabilities
from template_finder import TemplateFinder
from ui import UiManager
from pathing import OldPather
from logger import Logger
from screen import Screen
from utils.misc import rotate_vec, unit_vector, wait, is_in_roi
from utils.monsters import get_unlooted_monsters, CHAMPS_UNIQUES
import time
from pathing import OldPather, Location
import math
import threading
import numpy as np
import random

from api.mapassist import MapAssistApi
from pathing import Pather
from state_monitor import StateMonitor
from monsters import MonsterRule, MonsterType
from obs import ObsRecorder

class Hammerdin(IChar):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: MapAssistApi, obs_recorder: ObsRecorder, old_pather: OldPather, pather: Pather):
        Logger.info("Setting up Hammerdin")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder, pather, old_pather)
        self._old_pather = old_pather
        self._pather = pather
        self._do_pre_move = True
        # In case we have a running pala, we want to switch to concentration when moving to the boss
        # ass most likely we will click on some mobs and already cast hammers
        if not self._skill_hotkeys["teleport"]:
            self._do_pre_move = False
        else:
            # we want to change positions of shenk and eld a bit to be more center for teleport
            self._old_pather.offset_node(149, (70, 10))
    
    def get_cast_frames(self):
        fcr = self.get_fcr()
        frames = 15
        if fcr >= 125: frames = 9
        if fcr >= 75: frames = 10
        elif fcr >= 48: frames = 11
        elif fcr >= 30: frames = 12
        elif fcr >= 18: frames = 13
        elif fcr >= 9: frames = 14
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

    def on_capabilities_discovered(self, capabilities: CharacterCapabilities):
        # In case we have a running pala, we want to switch to concentration when moving to the boss
        # ass most likely we will click on some mobs and already cast hammers
        if capabilities.can_teleport_natively:
            self._do_pre_move = False
        else:
            # we want to change positions of shenk and eld a bit to be more center for teleport
            self._old_pather.offset_node(149, (70, 10))

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use vigor if set
        should_cast_vigor = self._skill_hotkeys["vigor"] and not self._ui_manager.is_right_skill_selected(["VIGOR"])
        can_teleport = self.capabilities.can_teleport_natively and self._ui_manager.is_right_skill_active()
        if should_cast_vigor and not can_teleport:
            keyboard.send(self._skill_hotkeys["vigor"])
            wait(0.15, 0.25)

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = self._screen.convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_hammers(atk_len)

    def kill_pindle(self) -> bool:
        wait(0.1, 0.15)
        if self.capabilities.can_teleport_natively:
            self._old_pather.traverse_nodes_fixed("pindle_end", self)
        else:
            if not self._do_pre_move:
                keyboard.send(self._skill_hotkeys["concentration"])
                wait(0.05, 0.15)
            self._old_pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        self._cast_hammers(self._char_config["atk_len_pindle"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_eldritch(self) -> bool:
        if self.capabilities.can_teleport_natively:
            # Custom eld position for teleport that brings us closer to eld
            self._old_pather.traverse_nodes_fixed([(675, 30)], self)
        else:
            if not self._do_pre_move:
                keyboard.send(self._skill_hotkeys["concentration"])
                wait(0.05, 0.15)
            self._old_pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_hammers(self._char_config["atk_len_eldritch"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_shenk(self):
        if not self._do_pre_move:
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.05, 0.15)
        self._old_pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_hammers(self._char_config["atk_len_shenk"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_council(self, game_state: StateMonitor) -> bool:
        if not self._do_pre_move:
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.05, 0.10)
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        atk_len = self._char_config["atk_len_trav"]
        # Here we have two different attack sequences depending if tele is available or not
        if self.capabilities.can_teleport_natively:
            self._kill_council(game_state)
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.05, 0.10)
        else:
            # Start hammers near the entrance
            self._cast_hammers(atk_len)
            # Go left of center stairs a bit
            self._old_pather.traverse_nodes([226, 227], self, time_out=1, force_move=True, do_pre_move=self._do_pre_move, force_time_out=True)
            self._cast_hammers(atk_len)
            # Move a bit to the top and more hammer
            self._move_and_attack((20, 10), atk_len)
            # Go inside and hammer a bit
            if not self._old_pather.traverse_nodes([228, 229], self, time_out=1, force_move=True, do_pre_move=self._do_pre_move, force_time_out=True):
                self._move_and_attack((-5, 5), atk_len / 2)
            self._cast_hammers(atk_len)
            # Stay inside and cast hammers again moving forward
            self._move_and_attack((40, 10), atk_len)
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
        return self._kill_mobs(["Diablo"], time_out=90)

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
            elpased = time.time() - start_time
            if elpased > 5.5:
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
                                self._pather.traverse(area_pos, self, randomize=12)
                                if dist < 8:
                                    self._cast_hammers(1.4)
                                    screen_space = world_to_abs(m['position'], self._api._player_pos)
                                    screen_space = [screen_space[0]-9.5,screen_space[1]-39.5]
                                    self._cast_holy_bolt(1.2, screen_space)
                                aura_after_battle = "cleansing"
                                num_repositions = 0
                            elif not focus_mummies:
                                self._pather.traverse(area_pos, self, randomize=12)
                                if dist < 8:
                                    self._cast_hammers(1)
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
        return self._kill_mobs(["BaalCrab"], ignore_names=["BaalCrabClone"], time_out=90)

    def kill_mephisto(self) -> bool:
        return self._kill_mobs(["Mephisto"])

    def kill_andariel(self) -> bool:
        return self._kill_mobs(["Andariel"])

    def kill_summoner(self) -> bool:
        return self._kill_mobs(["Summoner"])

    def kill_nihlathak(self) -> bool:
        return self._kill_mobs(["Nihlathak"])

    def _get_updated_monster(self, monster):
        fresh_data = self._api.get_data()
        fresh_m = next(filter(lambda x: x["id"] == monster and x["mode"] != 12, fresh_data["monsters"]), monster)
        return fresh_m

    def _kill_council(self, game_state: StateMonitor):
        Logger.debug(f"Beginning combat...")
        start = time.time()
        last_move = start
        elapsed = 0
        while elapsed < 50 and game_state._dead == 0:
            if game_state._ready:
                target_pos = game_state._target_pos
                target_pos = [target_pos[0] - 9.5, target_pos[1] - 39.5]
                # If we've been standing in one spot for too long, reposition
                if time.time() - last_move > 5.0:
                    Logger.debug("Stood in one place too long, repositioning")
                    self._pather.traverse((156, 113), self, time_out = 3.0)
                    last_move = time.time()
                elif game_state._dist > 8:
                    move_pos_screen = self._old_pather._adjust_abs_range_to_screen([target_pos[0], target_pos[1]])
                    move_pos_m = self._screen.convert_abs_to_monitor(move_pos_screen)
                    self.pre_move()
                    self.move(move_pos_m, force_tp=True)
                    last_move = time.time()
                keyboard.send(self._skill_hotkeys["concentration"])
                wait(0.03, 0.05)
                if not self.tele_stomp_monster("blessed_hammer", self._cast_duration * 3, game_state._target, stop_when_dead=False, max_distance=5): wait(0.1)
                self.post_attack()
            elapsed = time.time() - start
        Logger.debug(f"Finished killing council, combat took {round(elapsed, 2)} sec")
        return True

    def _kill_mobs(self, names: list[str] = None, ignore_names: list[str] = None, boundary: list[int] = None, time_out = 60) -> bool:
        start = time.time()
        success = False
        check_ignored = ignore_names is not None and len(ignore_names) > 0
        while time.time() - start < time_out:
            data = self._api.get_data()
            is_alive = False
            if data is not None:
                for m in data["monsters"]:
                    if m['mode'] != 12:
                        m = self._get_updated_monster(m)
                        area_pos = m["position"] - data["area_origin"]
                        proceed = any(m["name"].startswith(startstr) for startstr in names)
                        if check_ignored:
                            proceed = proceed and not any(m["name"].startswith(startstr) for startstr in ignore_names)
                        if proceed and (boundary is None or is_in_roi(boundary, area_pos)):
                            dist = math.dist(area_pos, data["player_pos_area"])
                            # self._pather.traverse(area_pos, self, time_out=1.0)
                            self._pather.move_to_monster(self, m)
                            if dist < 8:
                                self._cast_hammers(self._cast_duration * 3)
                            wait(0.1)
                            is_alive = True
                            success = True
            if not is_alive:
                return success
        Logger.debug(f"Finished killing council, combat took {round(time.time() - start, 2)} sec")
        return False

    def move_to_monster(self, monster, offset) -> bool:
        self.pre_move()
        self._pather.traverse([offset[0]+monster['position'][0]- self._api.data["area_origin"][0], offset[1]+monster["position"][1]- self._api.data["area_origin"][1]], self)
        wait(0.02, 0.4)
        return True
    
    def prepare_attack(self, aura: str) -> bool:
        keyboard.send(self._skill_hotkeys[aura])
        wait(0.03, 0.05)
        keyboard.send(self._char_config["stand_still"], do_release=False)
        wait(0.03, 0.05)
        if self._skill_hotkeys["blessed_hammer"]:
            keyboard.send(self._skill_hotkeys["blessed_hammer"])
            wait(0.03, 0.05)
        mouse.press(button="left")
        wait(0.03, 0.05)
        return True

    def post_attack(self) -> bool:
        mouse.release(button="left")
        wait(0.02, 0.4)
        keyboard.release(self._char_config["stand_still"]) 
        wait(0.02, 0.4)
        return True

    def kill_uniques(self, pickit=None, time_out: float=15.0, looted_uniques: set=set(), boundary=None):
        Logger.debug(f"Beginning combat")
        rules = [
            MonsterRule(auras = ["CONVICTION"]),
            MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE]),
            MonsterRule(monster_types = [MonsterType.UNIQUE]),
            MonsterRule(monster_types = [MonsterType.CHAMPION, MonsterType.GHOSTLY, MonsterType.POSSESSED]),
            # MonsterRule(monster_types = [MonsterType.MINION]),
        ]
        start = time.time()
        game_state = StateMonitor(rules, self._api, False, -1, True, False, None)
        last_move = start
        elapsed = 0
        picked_up_items = 0
        data = game_state._data
        while elapsed < time_out and game_state._dead == 0 and game_state._target is not None:
            if not game_state._ready:
                wait(0.1)
            else:
                target_pos = game_state._target_pos
                target_pos = [target_pos[0]-9.5, target_pos[1]-39.5]
                if time.time() - last_move > 6.0:
                    Logger.debug("Stood in one place too long, repositioning")
                    self.reposition(target_pos)
                    last_move = time.time()
                elif game_state._dist > 7:
                    move_pos_screen = self._old_pather._adjust_abs_range_to_screen([target_pos[0], target_pos[1]])
                    move_pos_m = self._screen.convert_abs_to_monitor(move_pos_screen)
                    self.pre_move()
                    self.move(move_pos_m, force_tp=True, force_move=True)
                    last_move = time.time()
                else:
                    keyboard.send(self._skill_hotkeys["concentration"])
                    wait(0.03, 0.05)
                    if not self.tele_stomp_monster("blessed_hammer", self._cast_duration * 3, game_state._target, stop_when_dead=False, max_distance=5): wait(0.1)
                    self.post_attack()
            elapsed = time.time() - start
        
        picked_up_items += self.loot_uniques(pickit, time_out, looted_uniques, boundary)

        # This is a hack to prevent Teleport from being used during pickit
        keyboard.send(self._skill_hotkeys["concentration"])
        wait(0.03, 0.05)
        self.post_attack()
        Logger.debug(f"Finished killing uniques, combat took {round(elapsed, 2)} sec")
        game_state.stop()
        return picked_up_items

    def _kill_mobs_adv(self, names: list[str], game_state:StateMonitor) -> bool:
        #loop till our boss death
        while game_state._dead == 0:
            if game_state._ready is True:
                area_pos = game_state._area_pos
                dist = game_state._dist
                self._pather.traverse(area_pos, self, randomize=10)
                if dist < 8:
                    self._cast_hammers(1.0)

    def kill_countess(self, pickit=None) -> bool:
        self.kill_uniques(pickit, 20)
        return True
