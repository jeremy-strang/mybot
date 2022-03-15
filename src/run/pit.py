from unittest.mock import seal
import cv2
import time
from char.i_char import IChar
from config import Config
from logger import Logger
from pathing import Location, OldPather, PathFinder
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


class Pit:
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
        Logger.info("Run Pit")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Pit requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(1, 5)
        return Location.A1_PIT_WP
    
    def battle(self, do_pre_buff: bool=True) -> Union[bool, tuple[Location, bool]]:
        self._char.pre_travel(do_pre_buff)
        if not self._pather.traverse("Monastery Gate", self._char, dest_distance=12): return False
        if not self._pather.go_to_area("Monastery Gate", "MonasteryGate", entrance_in_wall=False, randomize=3): return False

        if not self._pather.traverse("Tamoe Highland", self._char, dest_distance=10): return False
        if not self._pather.go_to_area("Tamoe Highland", "TamoeHighland", entrance_in_wall=False, randomize=4): return False
    
        if not self._pather.traverse("Pit Level 1", self._char, verify_location=True, dest_distance=12): return False
        if not self._pather.go_to_area("Pit Level 1", "PitLevel1", entrance_in_wall=False, randomize=4): return False
        self._char.post_travel()

        self._obs_recorder.start_recording_if_enabled()
        pit_lvl2 = self._pather.get_entity_coords_from_str("Pit Level 2", "poi", False)
        pf = PathFinder(self._api)
        nodes = pf.solve_tsp(pit_lvl2)
        for node in nodes:
            monster = self._pather.traverse(node, self._char, 0, True, False, True, True, self._pickit, time_out=6.0)
            while type(monster) is dict:
                self._char.kill_uniques(monster)
                picked_up_items = self._pickit.pick_up_items(self._char)  
                monster = self._pather.traverse(node, self._char, 0, True, False, True, True, self._pickit, time_out=6.0)
        self._char.post_attack()
        picked_up_items = self._pickit.pick_up_items(self._char)
        if not self._pather.traverse(pit_lvl2, self._char, kill=False, verify_location=True): return picked_up_items
        if do_pre_buff: self._char.pre_buff()
        self._char.post_attack()
        if not self._pather.go_to_area("Pit Level 2", "PitLevel2", entrance_in_wall=True, randomize=2, time_out=25):
            if not self._pather.go_to_area("Pit Level 2", "PitLevel2", entrance_in_wall=False, randomize=4, time_out=25):
                return picked_up_items

        monster = self._pather.traverse("SparklyChest", self._char, kill=True, verify_location=True, obj=True)
        while type(monster) is dict:
            self._char.kill_uniques(monster)
            self._char._
            picked_up_items = self._pickit.pick_up_items(self._char)
        self.post_attack()
        self._pather.traverse("SparklyChest", self._char, kill=False, verify_location=True)
        self._pather.activate_poi("SparklyChest", "SparklyChest", char=self._char) 
        picked_up_items = self._pickit.pick_up_items(self._char)

        self._obs_recorder.stop_recording_if_enabled()
        # for poi in ["Pit Level 2", "SparklyChest"]:
        #     monster = self._pather.traverse(poi, self._char, kill=True, verify_location=True)
        #     while type(monster) is dict:
        #         self._char.kill_uniques(monster)
        #         picked_up_items = self._pickit.pick_up_items(self._char)  
        #         monster = self._pather.traverse(poi, self._char, kill=True, verify_location=True, time_out=8.0)
        #     while self._api.data["current_area"] != poi.replace(" ",""):
        #         if "Pit Level" in poi:
        #             self._pather.go_to_area(poi, poi.replace(" ",""), entrance_in_wall=False, randomize=5, time_out=25)
        #             self._obs_recorder.stop_recording_if_enabled()
        #         elif poi == "SparklyChest":
        #             self._pather.activate_poi(poi, poi, char=self._char, offset=[-4, -6]) 
        #             wait(0.5, 1.0)
        #             picked_up_items = self._pickit.pick_up_items(self._char)
        #             break 
        #         else:
        #             self._pather.activate_poi(poi, poi, char=self._char)    
        return (Location.A1_PIT_END, picked_up_items)