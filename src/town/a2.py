import math
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


class A2(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, old_pather: OldPather, char: IChar, npc_manager: NpcManager, pather: Pather, api: D2rApi):
        super().__init__(screen, template_finder, old_pather, char, npc_manager, pather, api)

    def get_wp_location(self) -> Location: return Location.A2_WP
    def can_stash(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def _get_central_pos(self):
        pos1 = (123, 81)
        pos2 = (101, 95)
        if self._api.data:
            player_area = self._api.data["player_pos_area"]
            dist_pos1 = math.dist(pos1, player_area)
            dist_pos2 = math.dist(pos2, player_area)
            if dist_pos2 < dist_pos1:
                return pos2
        return pos1
    
    def _go_to_stash_area(self):
        self._pather.walk_to_position(self._get_central_pos(), time_out=15)
        self._pather.walk_to_position((123, 78), time_out=8)

    def heal(self, curr_loc: Location = Location.A2_TOWN_START) -> Union[Location, bool]:
        npc = Npc.FARA
        menu = None
        Logger.debug(f"Attempting to heal in Act 2, moving to {npc}...")
        self._pather.walk_to_position(self._get_central_pos(), time_out=15)
        self._pather.walk_to_position((123, 78), time_out=8)
        self.interact_with_npc(npc, menu)
        if self._api.wait_for_menu(D2rMenu.NpcInteract):
            keyboard.send("esc")
        return Location.A2_FARA_STASH

    def open_stash(self, curr_loc: Location = Location.A2_TOWN_START) -> Union[Location, bool]:
        self._go_to_stash_area()
        bank = self._api.wait_for_object("Bank", 1.0)
        if not bank:
            self._pather.walk_to_position(self._get_central_pos(), time_out=15)
            bank = self._api.wait_for_object("Bank", 3.0)
        self._pather.click_object("Bank")
        if not self._api.wait_for_menu(D2rMenu.Stash):
            return False
        return Location.A2_FARA_STASH

    def identify(self, curr_loc: Location = Location.A2_TOWN_START) -> Union[Location, bool]:
        npc = Npc.CAIN
        menu = "identify"
        Logger.debug(f"Attempting to identify in Act 2, moving to {npc}...")
        self._go_to_stash_area()
        if not self.interact_with_npc(npc, menu):
            Logger.warning(f"    Failed to {menu}, falling back to pixel method")
            if self._npc_manager.open_npc_menu(npc):
                self._npc_manager.press_npc_btn(npc, menu)
        return Location.A2_FARA_STASH

    def open_trade_menu(self, curr_loc: Location = Location.A2_TOWN_START) -> Union[Location, bool]:
        npc = Npc.LYSANDER
        menu = "trade"
        Logger.debug(f"Attempting to trade in Act 2, moving to {npc}...")
        self._pather.walk_to_position(self._get_central_pos(), time_out=15)
        if not self.interact_with_npc(npc, menu):
            Logger.warning(f"    Failed to {menu}, falling back to pixel method")
            if self._npc_manager.open_npc_menu(npc):
                self._npc_manager.press_npc_btn(npc, menu)
        return Location.A2_LYSANDER

    def open_trade_and_repair_menu(self, curr_loc: Location = Location.A2_TOWN_START) -> Union[Location, bool]:
        npc = Npc.FARA
        menu = "trade_repair"
        Logger.debug(f"Attempting to trade/repair in Act 2, moving to {npc}...")
        self._pather.walk_to_position(self._get_central_pos(), time_out=15)
        if not self.interact_with_npc(npc, menu):
            Logger.warning(f"    Failed to {menu}, falling back to pixel method")
            if self._npc_manager.open_npc_menu(npc):
                self._npc_manager.press_npc_btn(npc, menu)
        return Location.A2_FARA_STASH

    def open_wp(self, curr_loc: Location = Location.A2_TOWN_START) -> bool:
        success = False
        self._go_to_stash_area()
        if self._pather.walk_to_poi("Lut Gholein", time_out=15):
            self._pather.click_poi()
            success = self._api.wait_for_menu(D2rMenu.Waypoint)
        return success

    def wait_for_tp(self) -> Union[Location, bool]:
        return Location.A2_FARA_STASH
