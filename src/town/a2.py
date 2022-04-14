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
    def can_stash(self) -> bool: return False # Temporary until I fix pathing to the stash
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

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        # if not self._old_pather.traverse_nodes((curr_loc, Location.A2_FARA_STASH), self._char, force_move=True): return False
        # if self._npc_manager.open_npc_menu(Npc.FARA):
        #     return Location.A2_FARA_STASH
        # return False
        npc = Npc.FARA
        menu = None
        Logger.debug(f"Attempting to heal in Act 3, moving to {npc}...")
        if not self._pather.walk_to_monster(npc):
            Logger.error(f"    Failed to walk to NPC: {npc}")
        self.interact_with_npc(npc, menu)
        if self._api.wait_for_menu(D2rMenu.NpcInteract):
            keyboard.send("esc")
        return Location.A2_FARA_STASH

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        self._pather.walk_to_position(self._get_central_pos(), time_out=15)
        self._pather.walk_to_position((123, 78), time_out=8)
        bank = self._api.wait_for_object("Bank", 1.0)
        if not bank:
            self._pather.walk_to_position(self._get_central_pos(), time_out=15)
            bank = self._api.wait_for_object("Bank", 3.0)
        self._pather.click_object("Bank")
        if not self._api.wait_for_menu(D2rMenu.Stash):
            return False
        return Location.A2_FARA_STASH

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A2_FARA_STASH), self._char, force_move=True): return False
        if self._npc_manager.open_npc_menu(Npc.CAIN):
            self._npc_manager.press_npc_btn(Npc.CAIN, "identify")
            return Location.A2_FARA_STASH
        return False

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        # if not self._pather.traverse_walking("Lysander", self._char, obj=False, threshold=16, static_npc=True): return False
        # if not self.interact_with_npc(Npc.LYSANDER):
        #     if self._npc_manager.open_npc_menu(Npc.LYSANDER):
        #         self._npc_manager.press_npc_btn(Npc.LYSANDER, "trade")
        # return Location.A2_LYSANDER
        npc = Npc.A2_LYSANDER
        menu = "trade"
        Logger.debug(f"Attempting to trade in Act 3, moving to {npc}...")
        if not self._pather.walk_to_monster(npc):
            Logger.error(f"    Failed to walk to NPC: {npc}")
        if not self.interact_with_npc(npc, menu):
            Logger.warning(f"    Failed to {menu}, falling back to pixel method")
            if self._npc_manager.open_npc_menu(npc):
                self._npc_manager.press_npc_btn(npc, menu)
        return Location.A2_LYSANDER

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._old_pather.traverse_nodes((curr_loc, Location.A2_FARA_STASH), self._char, force_move=True): return
        if self._npc_manager.open_npc_menu(Npc.FARA):
            self._npc_manager.press_npc_btn(Npc.FARA, "trade_repair")
            return Location.A2_FARA_STASH
        return False

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather.traverse_walking("Lut Gholein", self._char, False, threshold=4, end_dist=10):
            if not self._old_pather.traverse_nodes((curr_loc, Location.A2_WP), self._char, force_move=True): return False
        if not self._pather.activate_waypoint("Lut Gholein", self._char, False, True):
            found_wp_func = lambda: self._template_finder.search("WAYPOINT_MENU", self._screen.grab()).valid
            return self._char.select_by_template(["A2_WP_DARK", "A2_WP_LIGHT"], found_wp_func, threshold=0.62, telekinesis=False)
        return True

    def wait_for_tp(self) -> Union[Location, bool]:
        # template_match = self._template_finder.search_and_wait(["A2_TOWN_21", "A2_TOWN_22", "A2_TOWN_20", "A2_TOWN_19"], time_out=20)
        # if template_match.valid:
        #     self._old_pather.traverse_nodes((Location.A2_TP, Location.A2_FARA_STASH), self._char, force_move=True)
        #     return Location.A2_FARA_STASH
        # return False
        return Location.A2_FARA_STASH
