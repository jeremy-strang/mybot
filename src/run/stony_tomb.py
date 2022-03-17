from unittest.mock import seal
import cv2
import time
from char.i_char import IChar
from config import Config
from logger import Logger
from pathing import Location, OldPather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from utils.custom_mouse import mouse
from screen import Screen
import math
from api.mapassist import MapAssistApi
from pathing import Pather
from obs import ObsRecorder


class Stony_Tomb:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        old_pather: OldPather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PickIt,
        api: MapAssistApi,
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
        Logger.info("Run Stony Tomb")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Pit requires teleport")

        if "a2_" not in self._api.data["current_area"]:
            self._pather.activate_waypoint("Lut Gholein", self._char, entrance_in_wall=False, is_wp = True)
            self._ui_manager.use_wp(2, 2)
        else:
            if not self._pather.traverse_walking("Lut Gholein", self._char, obj=False, threshold=16, max_distance=15): return False
            if not self._pather.traverse_walking("Drognan", self._char, obj=False, threshold=16, max_distance=15): return False
            if not self._pather.traverse_walking("Rocky Waste", self._char, obj=False, threshold=16, max_distance=10): return False
            wait(0.4)
        return Location.A2_STONY_WP
    
    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._pather.traverse_walking("Rocky Waste", self._char): return False
        if not self._pather.go_to_area("Rocky Waste", "RockyWaste", entrance_in_wall=False, randomize=2): return False

        while (self._api.data["current_area"] != 'RockyWaste'):
            self._pather.go_to_area("Rocky Waste", "RockyWaste", entrance_in_wall=False, randomize=2)
            wait (0.03, 0.05)
            count +=1
            if count > 3:
                Logger.error(f"Failed to travel to Rocky Waste")
                return False

        self._char.pre_travel(do_pre_buff)
        if not self._pather.traverse("Stony Tomb Level 1", self._char, verify_location=True, dest_distance=12): return False
        if not self._pather.go_to_area("Stony Tomb Level 1", "StonyTombLevel1", entrance_in_wall=True, randomize=3): return False
        self._char.post_travel()

        picked_up_items = 0
        lvl2 = self._pather.get_entity_coords_from_str("Stony Tomb Level", "poi", False)

        pickit_func = lambda: self._pickit.pick_up_items(self._char)
        picked_up_items += self._char.clear_zone(lvl2, pickit_func)

        if not self._pather.traverse(lvl2, self._char, kill=False, verify_location=True): return picked_up_items
        if do_pre_buff: self._char.pre_buff()

        if not self._pather.go_to_area("Stony Tomb Level 2", "StonyTombLevel2", entrance_in_wall=True, randomize=2, time_out=25):
            if not self._pather.go_to_area("Stony Tomb Level 2", "StonyTombLevel2", entrance_in_wall=False, randomize=4, time_out=25):
                return picked_up_items

        coords = self._pather.get_entity_coords_from_str("SparklyChest", "poi", False)
        picked_up_items += self._char.clear_zone(coords, pickit_func)

        self._pather.traverse("SparklyChest", self._char, kill=False, verify_location=True, obj=True)
        self._pather.activate_poi(coords, "StonyTombLevel2", char=self._char, offset=[9.5, 39.5], entrance_in_wall=False) 
        picked_up_items = self._pickit.pick_up_items(self._char)  
        
        return (Location.A2_STONY_END, picked_up_items)