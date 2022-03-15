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


class A4(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, old_pather: OldPather, char: IChar, npc_manager: NpcManager, pather: Pather, api: MapAssistApi):
        super().__init__(screen, template_finder, old_pather, char, npc_manager, pather, api)

    def get_wp_location(self) -> Location: return Location.A4_WP
    def can_resurrect(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_gamble(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_stash(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A4_TYRAEL_STASH), self._char, force_move=True):
            return False
        if self._npc_manager.open_npc_menu(Npc.TYRAEL):
            self._npc_manager.press_npc_btn(Npc.TYRAEL, "resurrect")
            return Location.A4_TYRAEL_STASH
        return False

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A4_WP), self._char): return False
        wait(0.5, 0.7)
        found_wp_func = lambda: self._template_finder.search("WAYPOINT_MENU", self._screen.grab()).valid
        # decreased threshold because we sometimes walk "over" it during pathing
        return self._char.select_by_template(["A4_WP", "A4_WP_2"], found_wp_func, threshold=0.62, telekinesis=False)

    def wait_for_tp(self) -> Union[Location, bool]:
        success = self._template_finder.search_and_wait(["A4_TOWN_4", "A4_TOWN_5", "A4_TOWN_6"], time_out=20).valid
        if success:
            return Location.A4_TOWN_START
        return False

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A4_TYRAEL_STASH), self._char, force_move=True): return False
        if self._npc_manager.open_npc_menu(Npc.CAIN):
            self._npc_manager.press_npc_btn(Npc.CAIN, "identify")
            return Location.A4_TYRAEL_STASH
        return False
    
    def gamble (self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A4_JAMELLA), self._char, force_move=True): return False
        if self._npc_manager.open_npc_menu(Npc.JAMELLA):
            self._npc_manager.press_npc_btn(Npc.JAMELLA, "gamble")
            return Location.A4_JAMELLA
        return False

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_walking("Jamella",self._char, obj=False,threshold=10,static_npc=True): return False
        if self._npc_manager.open_npc_menu(Npc.JAMELLA):
            self._npc_manager.press_npc_btn(Npc.JAMELLA, "trade")
            return Location.A4_JAMELLA
        return False

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_walking("Bank",self._char, obj=True,threshold=8,static_npc=False,end_dist=6): return False
        wait(0.2, 0.3)
        coords = self._pather.get_entity_coords_from_str("Bank", "objects", False)
        self._pather.activate_poi(coords, Location.A4_TYRAEL_STASH, char=self._char, entrance_in_wall=False)
        return Location.A4_TYRAEL_STASH

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        #if not self._old_pather.traverse_nodes((curr_loc, Location.A4_JAMELLA), self._char, force_move=True): return False
        if not self._pather.traverse_walking("Jamella",self._char, obj=False,threshold=10,static_npc=True): return False
        if self._npc_manager.open_npc_menu(Npc.JAMELLA):
            return Location.A4_JAMELLA
        return False

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A4_HALBU), self._char): return False
        if self._npc_manager.open_npc_menu(Npc.HALBU):
            self._npc_manager.press_npc_btn(Npc.HALBU, "trade_repair")
            return Location.A4_HALBU
        return False
