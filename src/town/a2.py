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


class A2(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, old_pather: OldPather, char: IChar, npc_manager: NpcManager, pather: Pather, api: MapAssistApi):
        super().__init__(screen, template_finder, old_pather, char, npc_manager, pather, api)

    def get_wp_location(self) -> Location: return Location.A2_WP
    def can_stash(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A2_FARA_STASH), self._char, force_move=True): return False
        if self._npc_manager.open_npc_menu(Npc.FARA):
            return Location.A2_FARA_STASH
        return False

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_walking("Bank",self._char, obj=True,threshold=10,static_npc=False,end_dist=8): return False
        wait(0.2, 0.3)
        coords = self._pather.get_entity_coords_from_str("Bank", "objects", False)
        self._pather.activate_poi(coords, Location.A2_FARA_STASH, char=self._char, entrance_in_wall=False)
        return Location.A2_FARA_STASH

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A2_FARA_STASH), self._char, force_move=True): return False
        if self._npc_manager.open_npc_menu(Npc.CAIN):
            self._npc_manager.press_npc_btn(Npc.CAIN, "identify")
            return Location.A2_FARA_STASH
        return False

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A2_LYSANDER), self._char, force_move=True): return False
        if self._npc_manager.open_npc_menu(Npc.LYSANDER):
            self._npc_manager.press_npc_btn(Npc.LYSANDER, "trade")
            return Location.A2_LYSANDER
        return False

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A2_FARA_STASH), self._char, force_move=True): return
        if self._npc_manager.open_npc_menu(Npc.FARA):
            self._npc_manager.press_npc_btn(Npc.FARA, "trade_repair")
            return Location.A2_FARA_STASH
        return False

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A2_WP), self._char, force_move=True): return False
        wait(0.5, 0.7)
        found_wp_func = lambda: self._template_finder.search("WAYPOINT_MENU", self._screen.grab()).valid
        return self._char.select_by_template(["A2_WP_LIGHT", "A2_WP_DARK"], found_wp_func, telekinesis=True)

    def wait_for_tp(self) -> Union[Location, bool]:
        template_match = self._template_finder.search_and_wait(["A2_TOWN_21", "A2_TOWN_22", "A2_TOWN_20", "A2_TOWN_19"], time_out=20)
        if template_match.valid:
            self._old_pather.traverse_nodes((Location.A2_TP, Location.A2_FARA_STASH), self._char, force_move=True)
            return Location.A2_FARA_STASH
        return False
