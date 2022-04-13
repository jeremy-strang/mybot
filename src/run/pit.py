from unittest.mock import seal
import keyboard
import cv2
import time
from char.i_char import IChar
from char.skill import Skill
from config import Config
from logger import Logger
from pathing import Location, OldPather, PathFinder, Pather
from typing import Union
from pickit.pixel_pickit import PixelPickit
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from utils.custom_mouse import mouse
from screen import Screen
import math
from d2r_mem.d2r_mem_api import D2rMemApi
from pathing import Pather
from obs import ObsRecorder


class Pit:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        old_pather: OldPather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PixelPickit,
        api: D2rMemApi,
        pather: Pather,
        obs_recorder: ObsRecorder,
    ):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._old_pather = old_pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit
        self._picked_up_items = False
        self.used_tps = 0
        self._api = api
        self._pather = pather
        self._obs_recorder = obs_recorder

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Pit")
        if not self._char.can_tp:
            raise ValueError("Pit requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(1, 5)
        return Location.A1_PIT_WP

    def _go_to_tamoe_plan_b(self):
        self._api.data["current_area"] if self._api.data else None
        for i in range(6):
            pos = self._screen.convert_abs_to_monitor((-600, 300))
            mouse.move(pos[0], pos[1], randomize=20)
            wait(0.1, 0.15)
            if self._char.can_tp:
                if not self._ui_manager.is_right_skill_selected(Skill.Teleport):
                    self._char.select_skill("teleport")
                    wait(0.04, 0.05)
                mouse.click(button="right")
                wait(self._char._cast_duration)
            else:
                keyboard.send(self._config.char["force_move"], do_release=False)
            wait(0.1, 0.15)
        current_area = self._api.data["current_area"] if self._api.data else None
        return current_area
        
                # char.pre_travel(True)
                # if not pather.traverse("Monastery Gate", char, dest_distance=12): return False
                # if not pather.go_to_area("Monastery Gate", "MonasteryGate", entrance_in_wall=False, randomize=3, char=char): return False

                # if not pather.traverse("Tamoe Highland", char, dest_distance=10): return False
                # if not pather.go_to_area("Tamoe Highland", "TamoeHighland", entrance_in_wall=False, randomize=4, char=char): return False
    def battle(self, do_pre_buff: bool=True) -> Union[bool, tuple[Location, bool]]:
        current_area = self._pather.wait_for_location("OuterCloister")
        self._char.pre_travel(do_pre_buff)

        if not self._pather.traverse("Monastery Gate", self._char, dest_distance=12): return False
        if not self._pather.go_to_area("Monastery Gate", "MonasteryGate", entrance_in_wall=False, randomize=3, char=self._char):
            current_area = self._pather.wander_towards((-600, 300), self._char, "TamoeHighland")
        wait(0.3)
        
        if current_area == "MonasteryGate":
            if not self._pather.traverse("Tamoe Highland", self._char, dest_distance=10): return False
            if not self._pather.go_to_area("Tamoe Highland", "TamoeHighland", entrance_in_wall=False, randomize=4, char=self._char):
                current_area = self._pather.wander_towards((-600, 300), self._char, "TamoeHighland")
            wait(0.3)
        
        if current_area != "TamoeHighland":
            current_area = self._pather.wander_towards((-600, 300), self._char, "TamoeHighland")
            wait(0.3)

        if not self._pather.traverse("Pit Level 1", self._char, verify_location=True, dest_distance=12): return False
        if not self._pather.go_to_area("Pit Level 1", "PitLevel1", entrance_in_wall=False, randomize=4, char=self._char): return False
        self._char.post_travel()

        picked_up_items = 0
        self._ui_manager.wait_for_loading_finish()
        wait(0.1, 0.2)
        self._ui_manager.disable_no_pickup()
        pickit_func = lambda: self._pickit.pick_up_items(self._char, skip_nopickup=True)

        pit_lvl2 = self._pather.get_entity_coords_from_str("Pit Level 2", "points_of_interest", False)
        picked_up_items += self._char.clear_zone(pit_lvl2, pickit_func)

        if not self._pather.traverse(pit_lvl2, self._char, kill=False, verify_location=True): return picked_up_items
        if do_pre_buff: self._char.pre_buff()
        
        if not self._pather.go_to_area("Pit Level 2", "PitLevel2", entrance_in_wall=True, randomize=2, time_out=25):
            if not self._pather.go_to_area("Pit Level 2", "PitLevel2", entrance_in_wall=False, randomize=4, time_out=25):
                return picked_up_items

        coords = self._pather.get_entity_coords_from_str("SparklyChest", "points_of_interest", False)
        picked_up_items += self._char.clear_zone(coords, pickit_func)

        self._pather.traverse("SparklyChest", self._char, kill=False, verify_location=True, obj=True)
        self._pather.activate_poi(coords, "PitLevel2", char=self._char, offset=[9.5, 39.5], entrance_in_wall=False) 
        picked_up_items = self._pickit.pick_up_items(self._char)

        self._ui_manager.enable_no_pickup()
        return (Location.A1_PIT_END, picked_up_items)
