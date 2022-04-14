from char import IChar
from town.i_act import IAct
from screen import Screen
from config import Config
from npc_manager import NpcManager, Npc
from pathing import OldPather, Location
from pathing import Pather
from d2r import D2rApi
from typing import Union
from template_finder import TemplateFinder
from utils.misc import wait

class A3(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, old_pather: OldPather, char: IChar, npc_manager: NpcManager, pather: Pather, api: D2rApi):
        super().__init__(screen, template_finder, old_pather, char, npc_manager, pather, api)

    def get_wp_location(self) -> Location: return Location.A3_STASH_WP
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_stash(self) -> bool: return True

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_walking("Ormus", self._char, obj=False, threshold=16, static_npc=True): return False
        self._npc_manager.open_npc_menu(Npc.ORMUS)
        return Location.A3_ORMUS

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_walking("Ormus", self._char, obj=False, threshold=16, static_npc=True): return False
        if not self.interact_with_npc(Npc.ORMUS):
            if self._npc_manager.open_npc_menu(Npc.ORMUS):
                self._npc_manager.press_npc_btn(Npc.ORMUS, "trade")
        return Location.A3_ORMUS

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        #if not self._pather.traverse_walking("Bank",self._char, obj=True, threshold=16, static_npc=False,end_dist=10): return False
        # if not self._pather.traverse_walking([147,60],self._char, obj=False, threshold=16, static_npc=False,end_dist=10): return False
        if not self._pather.walk_to_position((147, 60)): return False
        wait(0.4, 0.6)
        self._pather.click_object("Bank")    
        return Location.A3_STASH_WP

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather.walk_to_poi("Kurast Docks"): return False
        wait(0.4, 0.6)
        return self._pather.click_object("Act3TownWaypoint")
        # if not self._pather.traverse_walking("Kurast Docks", self._char, obj=False, threshold=16): return False
        # wait(0.4, 0.6)
        # result = self._pather.activate_waypoint("Kurast Docks", self._char,entrance_in_wall=False, is_wp = True)
        # return result

    def wait_for_tp(self) -> Union[Location, bool]:
        # template_match = self._template_finder.search_and_wait("A3_TOWN_10", time_out=15)
        # if template_match.valid:
        #     self._old_pather.traverse_nodes((Location.A3_STASH_WP, Location.A3_STASH_WP), self._char, force_move=True)
        #     return Location.A3_STASH_WP
        # return False
        return Location.A3_STASH_WP

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A3_STASH_WP), self._char): return False
        if self._npc_manager.open_npc_menu(Npc.CAIN):
            self._npc_manager.press_npc_btn(Npc.CAIN, "identify")
            return Location.A3_STASH_WP
        return False
