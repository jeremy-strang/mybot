import keyboard
from mas import world_to_abs
from utils.custom_mouse import mouse
from char import IChar, CharacterCapabilities
from char.barbarian.barbarian import Barbarian
from template_finder import TemplateFinder
from ui import UiManager
from pathing import OldPather
from logger import Logger
from screen import Screen
from utils.misc import wait, cut_roi, is_in_roi
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
from obs import ObsRecorder

class SingerBarb(Barbarian):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, obs_recorder: ObsRecorder, old_pather: OldPather, pather: Pather, api: MapAssistApi):
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder, pather, old_pather)
        self._old_pather = old_pather
        self._pather = pather
        Logger.info("Setting up Singer Barbarian")

    def _cast_war_cry(self, time_in_s: float):
        cry_frequency = min(0.2, self._skill_hotkeys["cry_frequency"])
        keyboard.send(self._char_config["stand_still"], do_release=False)
        wait(0.05, 0.1)
        if self._skill_hotkeys["war_cry"]:
            keyboard.send(self._skill_hotkeys["war_cry"])
        wait(0.05, 0.1)
        start = time.time()
        while (time.time() - start) < time_in_s:
            wait(0.06, 0.08)
            mouse.click(button="right")
            wait(cry_frequency, cry_frequency + 0.2)
            mouse.click(button="right")
        wait(0.01, 0.05)
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _cast_war_cry(self, time_in_s: float):
        cry_frequency = min(0.2, self._skill_hotkeys["cry_frequency"])
        keyboard.send(self._char_config["stand_still"], do_release=False)
        wait(0.05, 0.1)
        if self._skill_hotkeys["war_cry"]:
            keyboard.send(self._skill_hotkeys["war_cry"])
        wait(0.05, 0.1)
        start = time.time()
        while (time.time() - start) < time_in_s:
            wait(0.06, 0.08)
            mouse.click(button="right")
            wait(cry_frequency, cry_frequency + 0.2)
            mouse.click(button="right")
        wait(0.01, 0.05)
        keyboard.send(self._char_config["stand_still"], do_press=False)
    
    def on_capabilities_discovered(self, capabilities: CharacterCapabilities):
        if capabilities.can_teleport_natively:
            self._old_pather.offset_node(149, [120, 70])
            
    def _do_hork(self, hork_time: float):
         if self._skill_hotkeys["find_item"]:
            self.switch_weapon()
            keyboard.send(self._skill_hotkeys["find_item"])
            wait(0.5, 0.15)
            mouse.move(*self._screen.convert_abs_to_monitor(abs_screen_pos), randomize=80, delay_factor=[0.2, 0.4])
            mouse.press(button="right")
            wait(hork_time)
            mouse.release(button="right")
            keyboard.send(self._char_config["weapon_switch"])
         else:
            Logger.warning("Find Item unbound or missing. Skipping hork")	

    def pre_buff(self, switch_back=True):
        keyboard.send(self._char_config["battle_command"])
        wait(0.08, 0.19)
        mouse.click(button="right")
        wait(self._cast_duration + 0.08, self._cast_duration + 0.1)
        keyboard.send(self._char_config["battle_orders"])
        wait(0.08, 0.19)
        mouse.click(button="right")
        wait(self._cast_duration + 0.08, self._cast_duration + 0.1)
        keyboard.send(self._skill_hotkeys["shout"])
        wait(0.08, 0.19)
        mouse.click(button="right")
        wait(self._cast_duration + 0.08, self._cast_duration + 0.1)

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use leap if set
        should_cast_leap = self._skill_hotkeys["leap"] and not self._ui_manager.is_left_skill_selected(["LEAP"])
        can_teleport = self.capabilities.can_teleport_natively and self._ui_manager.is_right_skill_active()
        if  should_cast_leap and not can_teleport:
            keyboard.send(self._skill_hotkeys["leap"])
            wait(0.15, 0.25)
            
    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = self._screen.convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_war_cry(atk_len)

    def kill_pindle(self) -> bool:
        wait(0.1, 0.15)
        if self.capabilities.can_teleport_natively:
            self._old_pather.traverse_nodes_fixed("pindle_end", self)
        else:
            if not self._do_pre_move:
                self._old_pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        self._old_pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, time_out=0.1)
        self._cast_war_cry(self._char_config["atk_len_pindle"])
        wait(0.1, 0.15)
        self._do_hork(4)
        return True

    def kill_eldritch(self) -> bool:
        if self.capabilities.can_teleport_natively:
            self._old_pather.traverse_nodes_fixed("eldritch_end", self)
        else:
            self._old_pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_war_cry(self._char_config["atk_len_eldritch"])
        wait(0.1, 0.15)
        self._do_hork(4)
        return True

    def kill_shenk(self):
        self._old_pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_war_cry(self._char_config["atk_len_shenk"])
        wait(0.1, 0.15)
        self._do_hork(4.5)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Move close to nihlathak
        self._old_pather.traverse_nodes(end_nodes, self, time_out=0.8, do_pre_move=False)
        # move mouse to center (leftover from hammerdin)
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_war_cry(self._char_config["atk_len_nihlathak"] * 0.4)
        self._cast_war_cry(0.8)
        self._move_and_attack((30, 15), self._char_config["atk_len_nihlathak"] * 0.3)
        self._cast_war_cry(0.8)
        self._move_and_attack((-30, -15), self._char_config["atk_len_nihlathak"] * 0.4)
        wait(0.1, 0.15)
        self._cast_war_cry(1.2)
        self._do_hork(5)
        return True

    def kill_baal(self) -> bool:
        return self._kill_mobs(["BaalCrab"], ignore_names=["BaalCrabClone"])

    def kill_meph(self) -> bool:
        return self._kill_mobs(["Mephisto"])

    def kill_andy(self) -> bool:
        return self._kill_mobs(["Andariel"])

    def _get_updated_monster(self, monster):
        fresh_data = self._api.get_data()
        fresh_m = next(filter(lambda x: x["id"] == monster and x["mode"] != 12, fresh_data["monsters"]), monster)
        return fresh_m

    def kill_council(self, game_state: StateMonitor) -> bool:
        atk_len = self._char_config["atk_len_trav"]
        self._kill_mobs(game_state, atk_len)
        return True

    def _kill_mobs(self, game_state: StateMonitor, atk_len: float = 2) -> bool:
        Logger.debug(f"Beginning combat")
        start = time.time()
        last_move = start
        elapsed = 0
        while elapsed < 50 and game_state._dead == 0:
            if game_state._ready:
                target_pos = game_state._target_pos
                target_pos = [target_pos[0]-9.5,target_pos[1]-39.5]
                # If we've been standing in one spot for too long, reposition
                if time.time() - last_move > 6.0:
                    Logger.debug("Stood in one place too long, repositioning")
                    self._pather.traverse((156, 113), self)
                    last_move = time.time()
                elif game_state._dist > 6:
                    move_pos_screen = self._old_pather._adjust_abs_range_to_screen([target_pos[0], target_pos[1]])
                    move_pos_m = self._screen.convert_abs_to_monitor(move_pos_screen)
                    self.pre_move()
                    self.move(move_pos_m, force_tp=True)
                    last_move = time.time()
                else:
                    self._cast_war_cry(atk_len/5)
            elapsed = time.time() - start
        Logger.debug(f"Finished killing mobs, combat took {elapsed} sec")
        return True

    def _kill_mobs_adv(self, names: list[str], game_state:StateMonitor) -> bool:
        #loop till our boss death
        while game_state._dead == 0:
            if game_state._ready is True:
                area_pos = game_state._area_pos
                dist = game_state._dist
                self._pather.traverse(area_pos, self, randomize=10)
                if dist < 8:
                    self._cast_war_cry(2.0)
