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
from d2r.d2r_api import D2rApi
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
        api: D2rApi,
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
    
    def _end_run(self, picked_up_items):
        self._ui_manager.enable_no_pickup()
        self._ui_manager.hide_map()
        return (Location.A1_PIT_END, picked_up_items)

    def battle(self, do_pre_buff: bool=True) -> Union[bool, tuple[Location, bool]]:
        current_area = self._api.wait_for_area("OuterCloister")
        self._char.pre_travel(do_pre_buff)

        self._ui_manager.show_map()

        in_tamoe = False
        if self._char.can_tp:
            mouse.move(*self._screen.convert_abs_to_monitor((-540, 100)), delay_factor=[0.10, 0.15])
            keyboard.send(self._char._skill_hotkeys["teleport"], do_release=False)
            wait((self._char._cast_duration - 0.01) * 4 + 0.02)
            mouse.move(*self._screen.convert_abs_to_monitor((-540, 300)), delay_factor=[0.10, 0.15])
            keyboard.send(self._char._skill_hotkeys["teleport"], do_release=False)
            wait((self._char._cast_duration - 0.01) * 4 + 0.02)
            keyboard.release(self._char._skill_hotkeys["teleport"])
            wait(0.3)
            data = self._api.get_data()
            current_area = data["current_area"] if data and data["current_area"] is not None else ""
            if current_area.startswith("Tamoe"):
                in_tamoe = True
        
        Logger.debug(f"Initial tele result: {current_area}, in_tamoe: {in_tamoe}")

        if not in_tamoe:
            if "Cloister" in current_area:
                Logger.debug(f"We are still in the Cloister")
                self._pather.traverse("Monastery Gate", self._char, dest_distance=12, slow_finish=True)
                if not self._pather.go_to_area("Monastery Gate", "MonasteryGate", entrance_in_wall=False, randomize=3, char=self._char):
                    Logger.debug(f"    Didn't make it to the Monastery Gate, wandering there...")
                    current_area = self._pather.wander_towards((-600, 300), self._char, "TamoeHighland")
                wait(0.3)
        
            if current_area == "MonasteryGate":
                Logger.debug(f"We are in the Monastery Gate")
                self._pather.traverse("Tamoe Highland", self._char, dest_distance=10, slow_finish=True)
                if not self._pather.go_to_area("Tamoe Highland", "TamoeHighland", entrance_in_wall=False, randomize=4, char=self._char):
                    Logger.debug(f"    Didn't make it to the Tamoe Highland, wandering there...")
                    current_area = self._pather.wander_towards((-600, 300), self._char, "TamoeHighland")
                wait(0.3)
            
            if current_area != "TamoeHighland":
                Logger.debug(f"    Stil didn't make it to the Tamoe Highland, wandering there again...")
                current_area = self._pather.wander_towards((-600, 300), self._char, "TamoeHighland")
                wait(0.3)

        if not self._pather.traverse("Pit Level 1", self._char, verify_location=True, dest_distance=12, slow_finish=True):
            Logger.debug(f"    Failed initial traverse to Pit Level 1, wandering...")
            current_area = self._pather.wander_towards((-600, 300), self._char, "TamoeHighland")
            if not self._pather.traverse("Pit Level 1", self._char, verify_location=True, dest_distance=12, slow_finish=True): return False

        if not self._pather.go_to_area("Pit Level 1", "PitLevel1", entrance_in_wall=False, randomize=4, char=self._char): return False
        if not self._api.wait_for_area("PitLevel1"): return False
        picked_up_items = 0
        self._ui_manager.wait_for_loading_finish()
        wait(0.5, 0.6)
        self._char.post_travel()

        if self._config.char["enable_combat_walking"]:
            self._char.toggle_run_walk(True, test_pos_abs=(-100, 150))

        self._ui_manager.disable_no_pickup()
        pickit_func = lambda: self._pickit.pick_up_items(self._char, skip_nopickup=True)

        pit_lvl2 = self._pather.get_entity_coords_from_str("Pit Level 2", "points_of_interest", False)
        picked_up_items += self._char.clear_zone(pit_lvl2, pickit_func, jump_distance=12)

        if not self._pather.traverse(pit_lvl2, self._char, kill=False, verify_location=True, slow_finish=True, jump_distance=12):
            return self._end_run(picked_up_items)
        if do_pre_buff: self._char.pre_buff()
        
        if not self._pather.go_to_area("Pit Level 2", "PitLevel2", entrance_in_wall=True, randomize=2, time_out=15):
            self._pather.walk_to_poi("Pit Level 2")
            if not self._pather.go_to_area("Pit Level 2", "PitLevel2", entrance_in_wall=False, randomize=4, time_out=15):
                return self._end_run(picked_up_items)
        if not self._api.wait_for_area("PitLevel2"):
            return self._end_run(picked_up_items)
        self._ui_manager.wait_for_loading_finish()
        wait(0.5, 0.6)

        coords = self._pather.get_entity_coords_from_str("SparklyChest", "points_of_interest", False)
        picked_up_items += self._char.clear_zone(coords, pickit_func, jump_distance=12)

        self._pather.traverse("SparklyChest", self._char, kill=False, verify_location=False, obj=True, jump_distance=12)
        self._pather.activate_poi(coords, "PitLevel2", char=self._char, offset=[9.5, 39.5], entrance_in_wall=False)
        wait(1.0)
        picked_up_items = self._pickit.pick_up_items(self._char)

        if self._config.char["enable_combat_walking"]:
            self._char.toggle_run_walk(True, skip_verification=True)

        return self._end_run(picked_up_items)
