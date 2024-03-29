from d2r.d2r_api import D2rApi
from char import IChar
from config import Config
from logger import Logger
from pathing import OldPather, Location
from typing import Union
from pickit.pixel_pickit import PixelPickit
from screen import Screen
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from state_monitor import StateMonitor
from pathing import Pather
from obs import ObsRecorder

class Pindleskin:
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

    def approach(self, start_loc: Location) -> Union[bool, Location]:
        # Go through Red Portal in A5
        Logger.info("Run Pindleskin")
        loc = self._town_manager.go_to_act(5, start_loc)
        if not loc: return False
        if not self._pather.walk_to_position((122, 120)): return False
        wait(0.1)
        self._pather.click_object("PermanentTownPortal", (50, -50))
        if not self._api.wait_for_area("NihlathaksTemple"):
            if not self._pather.click_object("PermanentTownPortal"): return False
            if not self._api.wait_for_area("NihlathaksTemple"): return False
        return Location.A5_PINDLE_START

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._api.wait_for_area("NihlathaksTemple"): return False
        wait(1)
        
        Logger.info(f'do_pre_buff: {do_pre_buff}.')
        if do_pre_buff:
            self._char.pre_buff()

        # Move to Pindle
        self._char.pre_move()
        if self._char.can_tp:
            self._pather.traverse((61, 54), self._char)
        else:
            self._pather.walk_to_position((59, 59))
        self._char.kill_pindleskin()
        wait(0.1)

        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A5_PINDLE_END, picked_up_items)
