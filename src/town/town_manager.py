import time
from typing import Union
from api.mapassist import MapAssistApi
from item import ItemFinder
from obs.obs_recorder import ObsRecorder
from template_finder import TemplateFinder
from config import Config
from pathing import Location
from logger import Logger
from transmute import Transmute
from ui import UiManager
from town import IAct, A1, A2, A3, A4, A5
from utils.misc import wait
from api import MapAssistApi

TOWN_MARKERS = [
            "A5_TOWN_0", "A5_TOWN_1",
            "A4_TOWN_4", "A4_TOWN_5",
            "A3_TOWN_0", "A3_TOWN_1",
            "A2_TOWN_0", "A2_TOWN_1", "A2_TOWN_10",
            "A1_TOWN_1", "A1_TOWN_3"
        ]

class TownManager:

    def __init__(self, template_finder: TemplateFinder, ui_manager: UiManager, item_finder: ItemFinder, api: MapAssistApi, a1: A1, a2: A2, a3: A3, a4: A4, a5: A5):
        self._config = Config()
        self._template_finder = template_finder
        self._ui_manager = ui_manager
        self._item_finder = item_finder
        self._api = api
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.a5 = a5
        self._acts: dict[Location, IAct] = {
            Location.A1_TOWN_START: a1,
            Location.A2_TOWN_START: a2,
            Location.A3_TOWN_START: a3,
            Location.A4_TOWN_START: a4,
            Location.A5_TOWN_START: a5
        }

    @staticmethod
    def get_act_from_location(loc: Location) -> Location:
        location = None
        if loc.upper().startswith("A5_"):
            location = Location.A5_TOWN_START
        elif loc.upper().startswith("A4_"):
            location = Location.A4_TOWN_START
        elif loc.upper().startswith("A3_"):
            location = Location.A3_TOWN_START
        elif loc.upper().startswith("A2_"):
            location = Location.A2_TOWN_START
        elif loc.upper().startswith("A1_"):
            location = Location.A1_TOWN_START
        return location

    def get_act_from_current_area(self, time_out=30) -> Location:
        location = None
        current_area = None
        start = time.time()
        while location is None and time.time() - start < time_out:
            data = self._api.get_data()
            if data is not None and "current_area" in data and len(data["current_area"]) > 0:
                current_area = data["current_area"]
            if current_area == "Harrogath":
                location = Location.A5_TOWN_START
            elif current_area == "ThePandemoniumFortress":
                location = Location.A4_TOWN_START
            elif current_area == "KurastDocks":
                location = Location.A3_TOWN_START
            elif current_area == "LutGholein":
                location = Location.A2_TOWN_START
            elif current_area == "RogueEncampment":
                location = Location.A1_TOWN_START
            else:
                wait(0.02, 0.04)
        return location

    def wait_for_town_spawn(self, time_out: float = None) -> Location:
        """Wait for the char to spawn in town after starting a new game
        :param time_out: Optional float value for time out in seconds, defaults to None
        :return: Location of the town (e.g. Location.A4_TOWN_START) or None if nothing was found within time_out time
        """
        loc = self.get_act_from_current_area()
        if loc is not None: return loc
        
        print(f"Unable to determine location: {loc}")
        template_match = self._template_finder.search_and_wait(TOWN_MARKERS, best_match=True, time_out=time_out)
        if template_match.valid:
            return TownManager.get_act_from_location(template_match.name)
        return None

    def wait_for_tp(self, curr_loc: Location):
        curr_act = self.get_act_from_current_area()
        if curr_act is None:
            curr_act = TownManager.get_act_from_location(curr_loc)
            if curr_act is None: return False
        return self._acts[curr_act].wait_for_tp()

    def open_wp(self, curr_loc: Location):
        curr_act = self.get_act_from_current_area()
        if curr_act is None:
            curr_act = TownManager.get_act_from_location(curr_loc)
            if curr_act is None: return False
        return self._acts[curr_act].open_wp(curr_loc)

    def go_to_act(self, act_idx: int, curr_loc: Location) -> Union[Location, bool]:
        curr_act = self.get_act_from_current_area()
        if curr_act is None:
            curr_act = TownManager.get_act_from_location(curr_loc)
            if curr_act is None: return False
        # check if we already are in the desired act
        if act_idx == 1: act = Location.A1_TOWN_START
        elif act_idx == 2: act = Location.A2_TOWN_START
        elif act_idx == 3: act = Location.A3_TOWN_START
        elif act_idx == 4: act = Location.A4_TOWN_START
        elif act_idx == 5: act = Location.A5_TOWN_START
        else:
            Logger.error(f"Act {act_idx} is not supported")
            return False
        if curr_act == act:
            return curr_loc
        # if not, move to the desired act via waypoint
        if not self._acts[curr_act].open_wp(curr_loc): return False
        self._ui_manager.use_wp(act_idx, 0)
        return self._acts[act].get_wp_location()

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = self.get_act_from_current_area()
        if curr_act is None:
            curr_act = TownManager.get_act_from_location(curr_loc)
            if curr_act is None: return False
        # check if we can heal in current act
        if self._acts[curr_act].can_heal():
            return self._acts[curr_act].heal(curr_loc)
        Logger.warning(f"Could not heal in {curr_act}. Continue without healing")
        return curr_loc

    def buy_pots(self, curr_loc: Location, healing_pots: int = 0, mana_pots: int = 0) -> Union[Location, bool]:
        Logger.debug(f"Buying {healing_pots} health and {mana_pots} mana potions")
        curr_act = self.get_act_from_current_area()
        if curr_act is None:
            curr_act = TownManager.get_act_from_location(curr_loc)
            if curr_act is None: return False
        # check if we can buy pots in current act
        if self._acts[curr_act].can_buy_pots():
            new_loc = self._acts[curr_act].open_trade_menu(curr_loc)
            if not new_loc: return False
            self._ui_manager.buy_pots(healing_pots, mana_pots)
            wait(0.1, 0.2)
            self._ui_manager.close_vendor_screen()
            return new_loc
        Logger.warning(f"Could not buy pots in {curr_act}. Continue without buy pots")
        return curr_loc

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = self.get_act_from_current_area()
        if curr_act is None:
            curr_act = TownManager.get_act_from_location(curr_loc)
            if curr_act is None: return False
        # check if we can resurrect in current act
        if self._acts[curr_act].can_resurrect():
            return self._acts[curr_act].resurrect(curr_loc)
        new_loc = self.go_to_act(4, curr_loc)
        if not new_loc: return False
        return self._acts[Location.A4_TOWN_START].resurrect(new_loc)

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = self.get_act_from_current_area()
        if curr_act is None:
            curr_act = TownManager.get_act_from_location(curr_loc)
            if curr_act is None: return False
        # check if we can Identify in current act
        if self._acts[curr_act].can_identify():
            return self._acts[curr_act].identify(curr_loc)
        new_loc = self.go_to_act(5, curr_loc)
        if not new_loc: return False
        return self._acts[Location.A5_TOWN_START].identify(new_loc)

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = self.get_act_from_current_area()
        if curr_act is None:
            curr_act = TownManager.get_act_from_location(curr_loc)
            if curr_act is None: return False
        new_loc = curr_act
        if not self._acts[curr_act].can_stash():
            new_loc = self.go_to_act(5, curr_loc)
            if not new_loc: return False
            curr_act = Location.A5_TOWN_START
        new_loc = self._acts[curr_act].open_stash(new_loc)
        if not new_loc: return False
        return new_loc

    def gamble(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = self.get_act_from_current_area()
        if curr_act is None:
            curr_act = TownManager.get_act_from_location(curr_loc)
            if curr_act is None: return False
        # check if we can Identify in current act
        if self._acts[curr_act].can_gamble():
            return self._acts[curr_act].gamble(curr_loc)
        new_loc = self.go_to_act(4, curr_loc)
        if not new_loc: return False
        return self._acts[Location.A4_TOWN_START].gamble(new_loc)

    def stash(self, curr_loc: Location, gamble=False) -> Union[Location, bool]:
        curr_act = self.get_act_from_current_area()
        if curr_act is None:
            curr_act = TownManager.get_act_from_location(curr_loc)
            if curr_act is None: return False
        # check if we can stash in current act
        Logger.debug(f"Location is {curr_act}")
        if self._acts[curr_act].can_stash():
            self._ui_manager.throw_out_junk(self._item_finder)
            should_stash = self._ui_manager.should_stash()
            if not should_stash: return curr_loc
            new_loc = self._acts[curr_act].open_stash(curr_loc)
            if not new_loc: return False
            wait(1.0)
            self._ui_manager.stash_all_items(self._config.char["num_loot_columns"], self._item_finder, gamble)
            return new_loc
        new_loc = self.go_to_act(5, curr_loc)
        if not new_loc: return False
        new_loc = self._acts[Location.A5_TOWN_START].open_stash(new_loc)
        if not new_loc: return False
        wait(1.0)
        self._ui_manager.stash_all_items(self._config.char["num_loot_columns"], self._item_finder)
        return new_loc

    def repair_and_fill_tps(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = self.get_act_from_current_area()
        if curr_act is None:
            curr_act = TownManager.get_act_from_location(curr_loc)
            if curr_act is None: return False
        # check if we can rapair in current act
        if self._acts[curr_act].can_trade_and_repair():
            new_loc = self._acts[curr_act].open_trade_and_repair_menu(curr_loc)
            if not new_loc: return False
            if self._ui_manager.repair_and_fill_up_tp():
                wait(0.1, 0.2)
                self._ui_manager.close_vendor_screen()
                return new_loc
        new_loc = self.go_to_act(5, curr_loc)
        if not new_loc: return False
        new_loc = self._acts[Location.A5_TOWN_START].open_trade_and_repair_menu(new_loc)
        if not new_loc: return False
        if self._ui_manager.repair_and_fill_up_tp():
            wait(0.1, 0.2)
            self._ui_manager.close_vendor_screen()
            return new_loc
        return False


