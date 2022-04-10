from char.i_char import IChar
from config import Config
from logger import Logger
from pathing import Location, OldPather
from typing import Union
from pickit.pixel_pickit import PixelPickit
from api import MapAssistApi
from pathing import Pather
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait, is_in_roi
from utils.custom_mouse import mouse
from screen import Screen
import time
from state_monitor import StateMonitor
from obs import ObsRecorder

class Countess:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        old_pather: OldPather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PixelPickit,
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
        Logger.info("Run Tower")
        if not self._char.can_tp:
            raise ValueError("Tower requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(1, 4):
            return Location.A1_TOWER_START
        return False

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._pather.wait_for_location("BlackMarsh"): return False

        self._char.pre_travel(do_pre_buff)
        jump_dist = 15
        for destination in ["Forgotten Tower", *map(lambda x: f"Tower Cellar Level {x}", [1, 2, 3, 4, 5])]:
            if not self._pather.traverse(destination, self._char, verify_location=True, jump_distance=jump_dist):
                if not self._pather.traverse(destination, self._char, verify_location=True, jump_distance=8): return False
            if not self._pather.go_to_area(destination, destination, entrance_in_wall=False, randomize=4, char=self._char): return False
            jump_dist = 10
        self._char.post_travel()

        if not self._pather.traverse("GoodChest", self._char, verify_location=True): return False
        self._char.kill_countess()
        picked_up_items = self._pickit.pick_up_items(self._char)
        Logger.debug(f"Picked up {picked_up_items} items")
        return (Location.A1_TOWER_END, picked_up_items)
