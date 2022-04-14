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


class A4(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, old_pather: OldPather, char: IChar, npc_manager: NpcManager, pather: Pather, api: D2rApi):
        super().__init__(screen, template_finder, old_pather, char, npc_manager, pather, api)

    def get_wp_location(self) -> Location: return Location.A4_WP
    def can_resurrect(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_gamble(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_stash(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def resurrect(self, curr_loc: Location = Location.A4_TOWN_START) -> Union[Location, bool]:
        npc = Npc.TYRAEL
        menu = "resurrect"
        self._pather.walk_to_position((27, 41), time_out=5)
        if not self._pather.walk_to_monster(npc):
            Logger.error(f"    Failed to walk to NPC: {npc}")
            # Logger.error(f"    Failed to walk to NPC: {npc}, trying traverse...")
            # self._pather.traverse_walking(npc, self._char, threshold=10)
        if not self.interact_with_npc(npc, menu):
            Logger.warning(f"    Failed to {menu}, falling back to pixel method")
            if self._npc_manager.open_npc_menu(npc):
                self._npc_manager.press_npc_btn(npc, menu)
        return Location.A4_TYRAEL_STASH

    def open_wp(self, curr_loc: Location = Location.A4_TOWN_START) -> bool:
        Logger.debug("Opening waypoint...")
        self._pather.walk_to_object("PandamoniumFortressWaypoint")
        wait(0.7)
        self._pather.click_object("PandamoniumFortressWaypoint", (9.5, 0))
        return self._api.wait_for_menu("waypoint")

    def wait_for_tp(self) -> Union[Location, bool]:
        # success = self._template_finder.search_and_wait(["A4_TOWN_4", "A4_TOWN_5", "A4_TOWN_6"], time_out=20).valid
        # if success:
        #     return Location.A4_TOWN_START
        # return False
        return Location.A4_TOWN_START

    def identify(self, curr_loc: Location = Location.A4_TOWN_START) -> Union[Location, bool]:
        npc = Npc.CAIN
        menu = "identify"
        Logger.debug(f"Attempting to identify in Act 4, moving to {npc}...")
        self._pather.walk_to_position((27, 41), time_out=5)
        if not self._pather.walk_to_monster(npc):
            Logger.error(f"    Failed to walk to NPC: {npc}")
        if not self.interact_with_npc(npc, menu):
            Logger.warning(f"    Failed to {menu}, falling back to pixel method")
            if self._npc_manager.open_npc_menu(npc):
                self._npc_manager.press_npc_btn(Npc.CAIN, menu)
        return Location.A4_TYRAEL_STASH
    
    def gamble(self, curr_loc: Location = Location.A4_TOWN_START) -> Union[Location, bool]:
        npc = Npc.JAMELLA
        menu = "gamble"
        Logger.debug(f"Attempting to gamble in Act 4, moving to {npc}...")
        self._pather.walk_to_position((78, 43), time_out=5)
        if not self._pather.walk_to_monster(npc):
            Logger.error(f"    Failed to walk to NPC: {npc}")
            # Logger.error(f"    Failed to walk to NPC: {npc}, trying traverse...")
            # self._pather.traverse_walking(npc, self._char, threshold=10)
        if not self.interact_with_npc(npc, menu):
            Logger.warning(f"    Failed to {menu}, falling back to pixel method")
            if self._npc_manager.open_npc_menu(npc):
                self._npc_manager.press_npc_btn(npc, menu)
        return Location.A4_JAMELLA

    def open_trade_menu(self, curr_loc: Location = Location.A4_TOWN_START) -> Union[Location, bool]:
        npc = Npc.JAMELLA
        menu = "trade"
        Logger.debug(f"Attempting to open_trade_menu in Act 4, moving to {npc}...")
        self._pather.walk_to_position((78, 43), time_out=5)
        if not self._pather.walk_to_monster(npc):
            Logger.error(f"    Failed to walk to NPC: {npc}")
            # Logger.error(f"    Failed to walk to NPC: {npc}, trying traverse...")
            # self._pather.traverse_walking(npc, self._char, threshold=10)
        if not self.interact_with_npc(npc, menu):
            Logger.warning(f"    Failed to {menu}, falling back to pixel method")
            if self._npc_manager.open_npc_menu(npc):
                self._npc_manager.press_npc_btn(npc, menu)
        return Location.A4_JAMELLA

    def open_stash(self, curr_loc: Location = Location.A4_TOWN_START) -> Union[Location, bool]:
        self._pather.walk_to_position((27, 41), time_out=5)
        self._pather.walk_to_object("Bank")
        wait(0.3, 0.4)
        self._pather.click_object("Bank")
        if not self._api.wait_for_menu(D2rMenu.Stash):
            return False
        return Location.A4_TYRAEL_STASH

    def heal(self, curr_loc: Location = Location.A4_TOWN_START) -> Union[Location, bool]:
        npc = Npc.JAMELLA
        menu = None
        Logger.debug(f"Attempting to heal in Act 4, moving to {npc}...")
        self._pather.walk_to_position((78, 43), time_out=5)
        if not self._pather.walk_to_monster(npc):
            Logger.error(f"    Failed to walk to NPC: {npc}")
        self.interact_with_npc(npc, menu)
        if self._api.wait_for_menu(D2rMenu.NpcInteract):
            keyboard.send("esc")
            wait(0.12, 0.15)
        return Location.A4_JAMELLA

    def open_trade_and_repair_menu(self, curr_loc: Location = Location.A4_TOWN_START) -> Union[Location, bool]:
        npc = Npc.HALBU
        menu = "trade_repair"
        Logger.debug(f"Attempting to open trade and repair menu in Act 4, moving to {npc}...")
        self._pather.walk_to_position((78, 43), time_out=5)
        if not self._pather.walk_to_monster(npc):
            Logger.error(f"    Failed to walk to NPC: {npc}")
            # Logger.error(f"    Failed to walk to NPC: {npc}, trying traverse...")
            # self._pather.traverse_walking(npc, self._char, threshold=10)
        if not self.interact_with_npc(npc, menu):
            Logger.warning(f"    Failed to {menu}, falling back to pixel method")
            if self._npc_manager.open_npc_menu(npc):
                self._npc_manager.press_npc_btn(npc, menu)
        return Location.A4_HALBU
