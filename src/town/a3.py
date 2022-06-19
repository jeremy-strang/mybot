import time
from click import confirm
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
        Logger.debug("A3: Resurrecting mercenary...")
        success = True
        self._pather.walk_to_position((130, 96), char=self._char, do_pre_move=True)
        self._pather.walk_to_position((48, 91))
        
        npc_name = Npc.ASHEARA
        menu_selection = "resurrect"
        if not self.interact_with_npc(npc_name, menu_selection):
            if self._npc_manager.open_npc_menu(npc_name):
                self._npc_manager.press_npc_btn(npc_name, menu_selection)
        self._pather.walk_to_position((120, 90))
        return Location.A3_ORMUS if success else False

    def heal(self, curr_loc: Location = Location.A3_ORMUS) -> Union[Location, bool]:
        Logger.debug("A3: Healing at Ormus...")
        self._pather.walk_to_position((130, 96), char=self._char, do_pre_move=True)
        success = self.find_vendor_and_open_trade(Npc.ORMUS, menu_selection=None, confirm_menu=None)
        Logger.debug(f"    A3: Heal success: {success}")
        return Location.A3_ORMUS if success else False

    def open_trade_menu(self, curr_loc: Location = Location.A3_ORMUS) -> Union[Location, bool]:
        Logger.debug("A3: Opening trade menu with Ormus...")
        self._pather.walk_to_position((130, 96), char=self._char, do_pre_move=True)
        success = self.find_vendor_and_open_trade(Npc.ORMUS, y_offset=4)
        if not success:
            success = self._api.wait_for_menu(D2rMenu.NpcShop)
        Logger.debug(f"    A3: Open trade success: {success}")
        return Location.A3_ORMUS if success else False

    def open_stash(self, curr_loc: Location = Location.A3_ORMUS) -> Union[Location, bool]:
        Logger.debug("A3: Opening stash...")
        self._pather.walk_to_position((155, 63))
        wait(0.2)
        start = time.time()
        success = False
        while time.time() - start < 15 and not success:
            if not self._pather.click_object("Bank", time_out=4, target_menu=D2rMenu.Stash, offset=(25, -15)):
                wait(0.2)
                Logger.debug(f"    stash_open: {self._api.data['stash_open']}")
                hovered = self._api.data["hovered_unit"]
                if hovered and "name" in hovered and "cain" in hovered["name"].lower():
                    self._pather.click_object("Bank", time_out=4, target_menu=D2rMenu.Stash, offset=(25, -15))
                    wait(0.2)
            success = self._api.wait_for_menu(D2rMenu.Stash, 0.4)
        Logger.debug(f"    A3: Open stash success: {success}")
        return Location.A3_STASH_WP if success else False

    def open_wp(self, curr_loc: Location = Location.A3_ORMUS) -> bool:
        Logger.debug("A3: Opening WP...")
        success = True
        if not self._pather.walk_to_position((158, 56)):
            self._pather.walk_to_poi("Kurast Docks")
        wait(0.2)
        if not self._pather.click_object("Act3TownWaypoint", target_menu=D2rMenu.Waypoint):
            if not self._pather.click_object("Act3TownWaypoint", target_menu=D2rMenu.Waypoint):
                sucess = False
        return Location.A3_STASH_WP if success else False

    def wait_for_tp(self) -> Union[Location, bool]:
        return Location.A3_STASH_WP

    def identify(self, curr_loc: Location = Location.A3_ORMUS) -> Union[Location, bool]:
        Logger.debug("A3: Identifying items")
        self._pather.walk_to_position((155, 63))
        success = self.find_vendor_and_open_trade(Npc.CAIN, menu_selection="identify", confirm_menu=None)
        return Location.A3_STASH_WP if success else False
