from api.mapassist import MapAssistApi
from char.i_char import IChar
from config import Config
from logger import Logger
from pathing import Location, OldPather
from typing import Union
from pickit.pixel_pickit import PixelPickit
from pathing import Pather
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from dataclasses import dataclass
from chest import Chest
from screen import Screen
from obs import ObsRecorder

class Summoner:
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

    def approach(self, start_loc: Location) -> Union[bool, Location]:
        Logger.info("Run Summoner")
        if not self._char.can_tp:
            raise ValueError("Summoner requires Teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(2, 7):
            return Location.A2_ARC_START
        return False

    def _go_to_summoner(self, dest_dist):
        if not self._pather.traverse("The Summoner", self._char, verify_location=True, dest_distance=dest_dist):
            if not self._pather.traverse("The Summoner", self._char, verify_location=True, jump_distance=8, dest_distance=dest_dist): return False
        return True

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        is_barb = "_barb" in self._char._char_config["type"]
        if not self._pather.wait_for_location("ArcaneSanctuary"): return False
        
        self._char.pre_travel(do_pre_buff)
        self._go_to_summoner(50)
        if is_barb: self._char.cast_aoe("howl")
        self._char.post_travel()

        if not self._go_to_summoner(15): return False
        self._char.kill_summoner()
        
        if is_barb: self._char.cast_aoe("howl")
        return (Location.A2_ARC_END, self._pickit.pick_up_items(self._char, False))
