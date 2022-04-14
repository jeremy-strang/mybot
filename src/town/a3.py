import keyboard
from char import IChar
from logger import Logger
from town.i_act import IAct
from screen import Screen
from config import Config
from npc_manager import NpcManager, Npc
from pathing import OldPather, Location
from pathing import Pather
from d2r import D2rApi, D2rMenu
from typing import Union
from template_finder import TemplateFinder
from utils.misc import wait

class A3(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, old_pather: OldPather, char: IChar, npc_manager: NpcManager, pather: Pather, api: D2rApi):
        super().__init__(screen, template_finder, old_pather, char, npc_manager, pather, api)

    def get_wp_location(self) -> Location: return Location.A3_STASH_WP
    def can_resurrect(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_stash(self) -> bool: return True

    def resurrect(self, curr_loc: Location = Location.A3_ORMUS) -> Union[Location, bool]:
        npc = Npc.ASHEARA
        menu = "resurrect"
        self._pather.walk_to_position((120, 90), time_out=12)
        self._pather.walk_to_position((48, 91), time_out=12)
        self.interact_with_npc(npc, menu)
        self._pather.walk_to_position((120, 90), time_out=12)
        return Location.A3_ORMUS

    def heal(self, curr_loc: Location = Location.A3_ORMUS) -> Union[Location, bool]:
        npc = Npc.ORMUS
        menu = None
        Logger.debug(f"Attempting to heal in Act 3, moving to {npc}...")
        if not self._pather.walk_to_monster(npc):
            Logger.error(f"    Failed to walk to NPC: {npc}")
        self.interact_with_npc(npc, menu)
        if self._api.wait_for_menu(D2rMenu.NpcInteract):
            keyboard.send("esc")
        return Location.A3_ORMUS

    def open_trade_menu(self, curr_loc: Location = Location.A3_ORMUS) -> Union[Location, bool]:
        npc = Npc.ORMUS
        menu = "trade"
        Logger.debug(f"Attempting to trade in Act 3, moving to {npc}...")
        if not self._pather.walk_to_monster(npc):
            Logger.error(f"    Failed to walk to NPC: {npc}")
        if not self.interact_with_npc(npc, menu):
            Logger.warning(f"    Failed to {menu}, falling back to pixel method")
            if self._npc_manager.open_npc_menu(npc):
                self._npc_manager.press_npc_btn(npc, menu)
        return Location.A3_ORMUS

    def open_stash(self, curr_loc: Location = Location.A3_ORMUS) -> Union[Location, bool]:
        if not self._pather.walk_to_position((147, 60)): return False
        wait(0.4, 0.5)
        self._pather.click_object("Bank")    
        return Location.A3_STASH_WP

    def open_wp(self, curr_loc: Location = Location.A3_ORMUS) -> bool:
        if not self._pather.walk_to_poi("Kurast Docks"): return False
        wait(0.4, 0.5)
        return self._pather.click_object("Act3TownWaypoint")

    def wait_for_tp(self) -> Union[Location, bool]:
        return Location.A3_STASH_WP

    def identify(self, curr_loc: Location = Location.A3_ORMUS) -> Union[Location, bool]:
        npc = Npc.CAIN
        menu = "identify"
        Logger.debug(f"Attempting to identify in Act 3, moving to {npc}...")
        self._pather.walk_to_poi("KurastDocks", time_out=10)
        if not self._pather.walk_to_monster(npc):
            Logger.error(f"    Failed to walk to NPC: {npc}")
        if not self.interact_with_npc(npc, menu):
            Logger.warning(f"    Failed to {menu}, falling back to pixel method")
            if self._npc_manager.open_npc_menu(npc):
                self._npc_manager.press_npc_btn(npc, menu)
        return Location.A3_STASH_WP