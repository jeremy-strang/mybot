from char import IChar
from town.i_act import IAct
from screen import Screen
from config import Config
from npc_manager import NpcManager, Npc
from pather import Pather, Location
from pather_v2 import PatherV2
from api import MapAssistApi
from typing import Union
from template_finder import TemplateFinder
from utils.misc import wait

class A3(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, pather: Pather, char: IChar, npc_manager: NpcManager, pather_v2: PatherV2, api: MapAssistApi):
        super().__init__(screen, template_finder, pather, char, npc_manager, pather_v2, api)

    def get_wp_location(self) -> Location: return Location.A3_STASH_WP
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_stash(self) -> bool: return True

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather_v2.traverse_walking("Ormus",self._char, obj=False,threshold=10,static_npc=True): return False
        self._npc_manager.open_npc_menu(Npc.ORMUS)
        return Location.A3_ORMUS

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather_v2.traverse_walking("Ormus",self._char, obj=False,threshold=10,static_npc=True): return False
        if self._npc_manager.open_npc_menu(Npc.ORMUS):
            self._npc_manager.press_npc_btn(Npc.ORMUS, "trade")
            return Location.A3_ORMUS
        return False

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        #if not self._pather_v2.traverse_walking("Bank",self._char, obj=True,threshold=10,static_npc=False,end_dist=10): return False
        if not self._pather_v2.traverse_walking([147,60],self._char, obj=False,threshold=10,static_npc=False,end_dist=10): return False
        self._pather_v2.activate_poi ("Bank", "Bank", typ='objects', char=self._char)    
        return Location.A3_STASH_WP


    def open_wp(self, curr_loc: Location) -> bool:

        if not self._pather_v2.traverse_walking("Kurast Docks",self._char, obj=False,threshold=16): return False
        #if not self._pather_v2.traverse("Kurast Docks", self._char, obj=False): return False
        wait(0.5, 0.7)
        result = self._pather_v2.activate_waypoint("Kurast Docks", self._char,entrance_in_wall=False, is_wp = True)
        return result

    def wait_for_tp(self) -> Union[Location, bool]:
        template_match = self._template_finder.search_and_wait("A3_TOWN_10", time_out=20)
        if template_match.valid:
            self._pather.traverse_nodes((Location.A3_STASH_WP, Location.A3_STASH_WP), self._char, force_move=True)
            return Location.A3_STASH_WP
        return False

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A3_STASH_WP), self._char): return False
        if self._npc_manager.open_npc_menu(Npc.CAIN):
            self._npc_manager.press_npc_btn(Npc.CAIN, "identify")
            return Location.A3_STASH_WP
        return False
