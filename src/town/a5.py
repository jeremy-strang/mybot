import keyboard
from char import IChar
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

class A5(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, old_pather: OldPather, char: IChar, npc_manager: NpcManager, pather: Pather, api: D2rApi):
        super().__init__(screen, template_finder, old_pather, char, npc_manager, pather, api)

    def get_wp_location(self) -> Location: return Location.A5_WP
    def can_heal(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_resurrect(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_gamble(self) -> bool: return False
    def can_stash(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return False

    def heal(self, curr_loc: Location = Location.A5_TOWN_START) -> Union[Location, bool]:
        self._pather.walk_to_position((73, 22), char=self._char, do_pre_move=True)
        success = self.find_vendor_and_open_trade(Npc.MALAH, menu_selection=None, confirm_menu=None)
        return Location.A5_MALAH if success else False

    def open_trade_menu(self, curr_loc: Location = Location.A5_TOWN_START) -> Union[Location, bool]:
        self._pather.walk_to_position((73, 22), char=self._char, do_pre_move=True)
        success = self.find_vendor_and_open_trade(Npc.MALAH)
        return Location.A5_MALAH if success else False

    def resurrect(self, curr_loc: Location = Location.A5_TOWN_START) -> Union[Location, bool]:
        self._pather.walk_to_position((78, 83), char=self._char, do_pre_move=True)
        success = self.find_vendor_and_open_trade(Npc.QUAL_KEHK, menu_selection="resurrect", confirm_menu=None)
        return Location.A5_QUAL_KEHK if success else False

    def identify(self, curr_loc: Location = Location.A5_TOWN_START) -> Union[Location, bool]:
        self._pather.walk_to_position((78, 83), char=self._char, do_pre_move=True)
        success = self.find_vendor_and_open_trade(Npc.CAIN, menu_selection="identify", confirm_menu=None)
        return Location.A5_QUAL_KEHK if success else False

    def open_stash(self, curr_loc: Location = Location.A5_TOWN_START) -> Union[Location, bool]:
        self._pather.walk_to_poi("Harrogath", time_out=3, char=self._char, do_pre_move=True)
        bank = self._api.find_object("Bank")
        if bank and not self._pather.click_object("Bank"):
            if not self._pather.traverse_walking([119, 60],self._char, obj=False,threshold=10,static_npc=False,end_dist=10): return False
            self._pather.activate_poi("Bank", "Bank", collection='objects', char=self._char)    
            return Location.A5_LARZUK
        return Location.A5_LARZUK

    def open_trade_and_repair_menu(self, curr_loc: Location = Location.A5_TOWN_START) -> Union[Location, bool]:
        self._pather.walk_to_position((136, 43), char=self._char, do_pre_move=True)
        success = self.find_vendor_and_open_trade(Npc.LARZUK, "trade_repair", confirm_menu=D2rMenu.NpcShop, y_offset=0)
        return Location.A5_LARZUK if success else False

    def open_wp(self, curr_loc: Location = Location.A5_TOWN_START) -> bool:
        success = False
        self._pather.walk_to_position((114, 71))
        wp = self._api.find_object("ExpansionWaypoint")
        if wp:
            self._pather.walk_to_object("ExpansionWaypoint")
            self._pather.click_object("ExpansionWaypoint", (9.5, 0))
            success = self._api.wait_for_menu("waypoint")
        return success

    def wait_for_tp(self) -> Union[Location, bool]:
        return Location.A5_TOWN_START
