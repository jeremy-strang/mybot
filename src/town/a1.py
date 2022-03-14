from char import IChar
from town.i_act import IAct
from screen import Screen
from config import Config
from npc_manager import NpcManager, Npc
from pathing import OldPather, Location
from pathing import Pather
from api import MapAssistApi
from typing import Union
from template_finder import TemplateFinder
from utils.misc import wait

class A1(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, old_pather: OldPather, char: IChar, npc_manager: NpcManager, pather: Pather, api: MapAssistApi):
        super().__init__(screen, template_finder, old_pather, char, npc_manager, pather, api)

    def get_wp_location(self) -> Location: return Location.A1_WP_NORTH
    def can_resurrect(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_stash(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A1_KASHYA_CAIN), self._char, force_move=True):
            return False
        if self._npc_manager.open_npc_menu(Npc.KASHYA):
            self._npc_manager.press_npc_btn(Npc.KASHYA, "resurrect")
            return Location.A1_KASHYA_CAIN
        return False

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather.traverse_walking("Rogue Encampment", self._char, obj=False, threshold=10): return False
        wait(0.5, 0.7)
        result = self._pather.activate_waypoint("Rogue Encampment", self._char,entrance_in_wall=False, is_wp = True)
        return result        

    def wait_for_tp(self) -> Union[Location, bool]:
        success = self._template_finder.search_and_wait(["A1_TOWN_7", "A1_TOWN_9"], time_out=20).valid
        if not self._old_pather.traverse_nodes([Location.A1_TOWN_TP, Location.A1_KASHYA_CAIN], self._char, force_move=True): return False
        if success:
            return Location.A1_KASHYA_CAIN
        return False

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A1_KASHYA_CAIN), self._char): return False
        if self._npc_manager.open_npc_menu(Npc.CAIN):
            self._npc_manager.press_npc_btn(Npc.CAIN, "identify")
            return Location.A1_KASHYA_CAIN
        return False

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_walking("Akara",self._char, obj=False, threshold=10, static_npc=True): return False
        if not self.trade_with_npc(Npc.AKARA):
            self._npc_manager.open_npc_menu(Npc.AKARA)
            self._npc_manager.press_npc_btn(Npc.AKARA, "trade")
        return Location.A1_AKARA

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_walking("Bank",self._char, obj=True,threshold=10,static_npc=False,end_dist=8): return False
        self._pather.activate_poi ("Bank", "Bank", typ='objects', char=self._char)    
        return Location.A1_STASH

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        #if not self._old_pather.traverse_nodes((curr_loc, Location.A1_AKARA), self._char, force_move=True): return False
        if not self._pather.traverse_walking("Akara",self._char, obj=False,threshold=10,static_npc=True): return False
        self._npc_manager.open_npc_menu(Npc.AKARA)
        return Location.A1_AKARA

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_walking("Charsi",self._char, obj=False,threshold=10,static_npc=True): return False    
        #if not self._old_pather.traverse_nodes((curr_loc, Location.A1_CHARSI), self._char): return False
        self._npc_manager.open_npc_menu(Npc.CHARSI)
        self._npc_manager.press_npc_btn(Npc.CHARSI, "trade_repair")
        return Location.A1_CHARSI
