from api.mapassist import MapAssistApi
from char import IChar
from config import Config
from logger import Logger
from old_pather import Location, OldPather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from state_monitor import StateMonitor
from pathing import Pather
from obs import ObsRecorder

class Pindle:
    def __init__(
        self,
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
        self._template_finder = template_finder
        self._old_pather = old_pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit
        self._api = api
        self._pather = pather
        self._obs_recorder = obs_recorder

    def approach(self, start_loc: Location) -> Union[bool, Location]:
        # Go through Red Portal in A5
        Logger.info("Run Pindle")
        loc = self._town_manager.go_to_act(5, start_loc)
        if not loc:
            return False
        #if not self._old_pather.traverse_nodes((loc, Location.A5_NIHLATHAK_PORTAL), self._char):
        #    return False
        #self._pather.traverse([122,122], self._char,verify_location=True)
        if not self._pather.traverse_walking([122,122],self._char, obj=False,threshold=10,static_npc=False,end_dist=5): return False
        wait(0.5, 0.6)
        found_loading_screen_func = lambda: self._ui_manager.wait_for_loading_screen(2.0)
        if not self._char.select_by_template(["A5_RED_PORTAL", "A5_RED_PORTAL_TEXT"], found_loading_screen_func, telekinesis=False):
            return False
        return Location.A5_PINDLE_START

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        # Kill Pindle
        if not self._template_finder.search_and_wait(["PINDLE_0", "PINDLE_1"], threshold=0.65, time_out=20).valid:
            return False
        if do_pre_buff:
            self._char.pre_buff()
        # move to pindle
        if self._char.capabilities.can_teleport_natively and self._config.char['type'] != 'necro':
            self._old_pather.traverse_nodes_fixed("pindle_safe_dist", self._char)
        else:
            self._pather.traverse([62,90], self._char,verify_location=True)
            #if not self._old_pather.traverse_nodes((Location.A5_PINDLE_START, Location.A5_PINDLE_SAFE_DIST), self._char):
                #return False
        if self._char._char_config['type'] == 'necro':
            game_state = StateMonitor(['DefiledWarrior'], self._api,super_unique=True)
            result = self._char.kill_pindle_mem(game_state)
            if result:
                Logger.info("Pindle died...")
            wait(0.2, .4)
            x = game_state._area_pos[0]
            y = game_state._area_pos[1]
            #go to andys body
            self._pather.traverse((x, y), self._char)
            game_state.stop()
        else:
            self._char.kill_pindle()
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)
        #picked_up_items = self._pickit2.pick_up_items(self._char, is_at_trav=True)
        return (Location.A5_PINDLE_END, picked_up_items)
