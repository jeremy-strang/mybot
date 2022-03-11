from operator import is_
from unittest import skip
import keyboard
from mas import world_to_abs
from utils.custom_mouse import mouse
from char import IChar, CharacterCapabilities
from template_finder import TemplateFinder
from ui import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait, is_in_roi, cut_roi, points_equal
import time
from pather import Pather, Location
import math
import threading
import numpy as np
import random
import cv2

from api.mapassist import MapAssistApi
from pathing.pather_v2 import PatherV2
from state_monitor import StateMonitor
from obs import ObsRecorder

class Barbarian(IChar):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: MapAssistApi, obs_recorder: ObsRecorder, pather: Pather, pather_v2: PatherV2):
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder)
        self._pather = pather
        self._pather_v2 = pather_v2
        self._do_pre_move = True

    def get_cast_frames(self):
        fcr = self.get_fcr()
        frames = 13
        if fcr >= 200: frames = 7
        elif fcr >= 105: frames = 8
        elif fcr >= 63: frames = 9
        elif fcr >= 37: frames = 10
        elif fcr >= 20: frames = 11
        elif fcr >= 9: frames = 12
        return frames
    
    def on_capabilities_discovered(self, capabilities: CharacterCapabilities):
        if capabilities.can_teleport_natively:
            self._pather.offset_node(149, [120, 70])

    def cast_melee(self, skill_key: str, time_in_s: float, abs_screen_pos: tuple[float, float], mouse_button: str = "left"):
        mouse_pos_m = self._screen.convert_abs_to_monitor(abs_screen_pos)
        Logger.debug(f"Casting {skill_key} in the direction of ({round(mouse_pos_m[0], 2)}, {round(mouse_pos_m[0], 2)})")
        if self._skill_hotkeys[skill_key]:
            keyboard.send(self._skill_hotkeys[skill_key])
            wait(0.05)
            mouse.move(*mouse_pos_m, delay_factor=[0.2, 0.4])
            keyboard.send(self._char_config["stand_still"], do_release=False)
            start = time.time()
            while (time.time() - start) < time_in_s:
                wait(0.06, 0.08)
                mouse.press(button=mouse_button)
                wait(0.1, 0.2)
                mouse.release(button=mouse_button)
            keyboard.send(self._char_config["stand_still"], do_press=False)
    
    def cast_melee_to_monster(self, skill_key: str, time_in_s: float, monster: dict, mouse_button: str = "left") -> bool:
        if self._skill_hotkeys[skill_key]:
            if type(monster) is dict:
                Logger.debug(f"Meleeing monster {monster['id']} with {skill_key} ({round(monster['position'][0], 2)}, {round(monster['position'][0], 2)})")
                keyboard.send(self._skill_hotkeys[skill_key])
                wait(0.03, 0.4)
                self._pather_v2.move_mouse_to_monster(monster)
                keyboard.send(self._char_config["stand_still"], do_release=False)
                start = time.time()
                while (time.time() - start) < time_in_s:
                    wait(0.05, 0.07)
                    mouse.press(button=mouse_button)
                    wait(0.1, 0.2)
                    mouse.release(button=mouse_button)
                keyboard.send(self._char_config["stand_still"], do_press=False)
                return True
            else:
                Logger.error(f"Invalid monster {monster}")
        return False

    def get_next_corpse(self, names: list[str] = None, boundary: list[int] = None, skip_ids = set(), unique_only: bool = False):
        data = self._api.get_data()
        if data is None or "monsters" not in data or type(data["monsters"]) is not list: return None
        monsters = sorted(data["monsters"], key = lambda m: (math.dist(data["player_pos_area"], m["position"] - data["area_origin"])))
        for m in monsters:
            if unique_only:
                proceed = m["mode"] == 12 and m["is_targetable_corpse"] and m["id"] not in skip_ids and any (m["type"] in typ for typ in ["SuperUnique", "Unique", "Champion"])
            else:
                proceed = m["mode"] == 12 and m["is_targetable_corpse"] and m["id"] not in skip_ids
            if proceed and names is not None:
                proceed = False
                for name in names:
                    proceed = proceed or m["name"].startswith(name)
            if proceed and boundary is not None:
                proceed = is_in_roi(boundary, m["position"] - data["area_origin"])
            if proceed: return m
        return None

    def cast_hork(self, abs_screen_pos: tuple[float, float], press_len: float = 0.4, stand_still: bool = True):
        mouse_pos_m = self._screen.convert_abs_to_monitor(abs_screen_pos)
        Logger.debug(f"Casting hork in the direction of ({round(mouse_pos_m[0], 2)}, {round(mouse_pos_m[1], 2)})")
        if self._skill_hotkeys["find_item"]:
            keyboard.send(self._skill_hotkeys["find_item"])
            wait(0.03)
            if stand_still:
                keyboard.send(self._char_config["stand_still"], do_release=False)
                wait(0.03)
            mouse.move(*mouse_pos_m, delay_factor=[0.07, 0.1])
            wait(0.03)
            mouse.press(button="right")
            wait(press_len)
            mouse.release(button="right")
            wait(0.03)
            if stand_still:
                keyboard.send(self._char_config["stand_still"], do_press=False)
            wait(0.1, 0.15)

    def do_hork(self, names: list[str] = None, boundary: list[int] = None, time_out: float = 15.0, unique_only: bool = False, disable_swap: bool = False) -> bool:
        Logger.debug("Beginning hork...")
        if self._char_config["barb_pre_hork_weapon_swap"] and not disable_swap:
            self.switch_weapon()
        m = self.get_next_corpse(names, boundary, unique_only = unique_only)
        start = time.time()
        skip_ids = set()
        last_pos = None
        last_monster_id = 0
        while m is not None and time.time() - start < time_out:
            data = self._api.get_data()
            distance = math.dist(data["player_pos_area"], m["position"] - data["area_origin"])
            m_id = m["id"]
            if distance > 3.5:
                move_pos_m = self._screen.convert_player_target_world_to_monitor(m["position"], data["player_pos_world"])
                self.pre_move()
                self.move(move_pos_m, force_tp=True)
                wait(0.1, 0.15)
                data = self._api.get_data()
                # Recalculate distance after moving
                distance = math.dist(data["player_pos_area"], m["position"] - data["area_origin"])
                # If we're in the same spot and targeting the same monster after moving, skip it
                if m_id == last_monster_id:
                    if last_pos is not None and points_equal(last_pos, data["player_pos_world"], 2):
                        Logger.debug(f"Failed to move into hork range of monster {m_id}, skipping it")
                        skip_ids.add(m_id)
            if distance <= 3.5:
                target_pos = world_to_abs(m["position"], data["player_pos_world"])
                self.cast_hork(target_pos, press_len=self._cast_duration * 2 + 0.02)
            else:
                wait(0.10, 0.15)
            last_monster_id = m_id
            last_pos = data["player_pos_world"]
            m = self.get_next_corpse(names, boundary, skip_ids=skip_ids, unique_only=unique_only)
        if self._char_config["barb_pre_hork_weapon_swap"] and not disable_swap:
            self.switch_weapon()
        Logger.debug(f"Finished horking corpses after {round(time.time() - start, 2)} sec")

    def pre_buff_swap(self, switch_back=True):
        # Try to switch weapons and select bo until we find the skill on the right skill slot
        self.switch_weapon()
        keyboard.send(self._char_config["battle_command"])
        wait(0.04, 0.07)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.03)
        keyboard.send(self._char_config["battle_orders"])
        wait(0.04, 0.07)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.03)
        keyboard.send(self._skill_hotkeys["shout"])
        wait(0.04, 0.07)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.03)
        # Make sure the switch back to the original weapon is good
        if switch_back:
            print("switching back...")
            self.switch_weapon()
            self.verify_active_weapon_tab()
        else:
            print("not switching back...")

    def pre_buff(self, switch_back=True):
        if self._char_config["barb_pre_buff_weapon_swap"]:
            self.pre_buff_swap(switch_back)
        else:
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

