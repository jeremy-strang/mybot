from api.mapassist import MapAssistApi
from char import IChar
from config import Config
from logger import Logger
from pathing import Location, OldPather
from typing import Union
from item.pickit import PickIt
from pathing import Pather
import state_monitor
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from state_monitor import StateMonitor
from obs import ObsRecorder

class Travincal:
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
        # Go to Travincal via waypoint
        Logger.info("Run Trav")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(3, 7):
            return Location.A3_TRAV_START
        return False
    
    def _avoid_durance(self):
        # Hack in case we end up in Durance by accidentally clicking the stairs
        data = self._api.get_data()
        if data is not None and data["current_area"] == "DuranceOfHateLevel1":
            if not self._pather.go_to_area("Travincal", "Travincal", True, time_out=5.0):
                self._pather.go_to_area("Travincal", "Travincal", True, time_out=5.0)

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        tele_swap = self._config.char["teleport_weapon_swap"]
        # Kill Council
        if not self._template_finder.search_and_wait(["TRAV_0", "TRAV_1", "TRAV_20"], threshold=0.65, time_out=20).valid:
            return False
        if do_pre_buff:
            self._char.pre_buff(switch_back=not tele_swap)

        if self._config.char["teleport_weapon_swap"] and not self._config.char["barb_pre_buff_weapon_swap"]:
            self._char.switch_weapon()

        if self._char.capabilities.can_teleport_natively:
            if self._char._char_config['type'] == 'necro' and not self._pather.traverse("Durance of Hate Level 1", self._char): return False
            elif not self._pather.traverse((156, 113), self._char, verify_location=False): return False
        elif not self._pather.traverse_walking((155, 113), self._char):
            return False
        
        if tele_swap:
            self._char.switch_weapon()
            self._char.verify_active_weapon_tab()

        self._obs_recorder.start_recording_if_enabled()
        self._api.start_timer()
        if self._char._char_config['type'] == 'hammerdin':
            game_state = StateMonitor(['CouncilMember'], self._api, unique_id=-1, many=True)
            self._char.kill_council(game_state)
            self._avoid_durance()
            game_state.stop()
        elif self._char._char_config['type'] == 'barbarian' or self._char._char_config['type'] == 'zerker_barb':
            # First kill council
            self._char.kill_council(None)
            # Loot once before hork to get anything that might get covered up after hork
            picked_up_items = self._pickit.pick_up_items(self._char, is_at_trav=True)
            wait(0.1, 0.2)
            self._avoid_durance()
            # Hork hork hork
            self._char.do_hork(names=["CouncilMember"], boundary=[122, 80, 50, 50])
        elif self._char._char_config['type'] == 'light_sorc' or self._char._char_config['type'] == 'necro':
            game_state = StateMonitor(['CouncilMember'], self._api, unique_id=-1, many=True)
            self._char.kill_council(game_state)
            x = game_state._area_pos[0]
            y = game_state._area_pos[1]
            wait(0.05, .1)
            game_state.stop()
            self._avoid_durance()
            self._pather.traverse((x, y), self._char, time_out=4.0)
        else:
            raise ValueError("Unsupport character")
        self._api.get_metrics()

        # Check for loot once wherever we ended up after combat
        picked_up_items = self._pickit.pick_up_items(self._char, is_at_trav=True)
        wait(0.1, 0.15)
        self._avoid_durance()

        # If we can teleport we want to move back inside and also check loot there
        if self._char.capabilities.can_teleport_natively or self._char.capabilities.can_teleport_with_charges:
            self._pather.traverse((156, 113), self._char, time_out=4.0)
            picked_up_items |= self._pickit.pick_up_items(self._char, is_at_trav=True)
            #wait(0.1, 0.2)
            # Go back to a good spot to TP
            self._avoid_durance()
            self._pather.traverse((154, 111), self._char, time_out=4.0)

        else: # Else we need to make sure we loot both inside and outside the council room
            self._old_pather.traverse_nodes([228, 226], self._char, time_out=2, force_move=True)
            picked_up_items |= self._pickit.pick_up_items(self._char, is_at_trav=True)
            wait(0.1, 0.2)
            self._old_pather.traverse_nodes([226, 228, 229], self._char, time_out=2, force_move=True)
            picked_up_items |= self._pickit.pick_up_items(self._char, is_at_trav=True)
            wait(0.1, 0.2)
            self._old_pather.traverse_nodes([230], self._char, time_out=2)
        # self._obs_recorder.stop_recording_if_enabled()
        return (Location.A3_TRAV_CENTER_STAIRS, picked_up_items)
