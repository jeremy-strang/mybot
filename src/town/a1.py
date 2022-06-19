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

class A1(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, old_pather: OldPather, char: IChar, npc_manager: NpcManager, pather: Pather, api: D2rApi):
        super().__init__(screen, template_finder, old_pather, char, npc_manager, pather, api)

    def get_wp_location(self) -> Location: return Location.A1_WP_NORTH
    def can_resurrect(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_stash(self) -> bool: return False # Temporary
    def can_trade_and_repair(self) -> bool: return True

    def resurrect(self, curr_loc: Location = Location.A1_TOWN_START) -> Union[Location, bool]:
        npc = self._api.find_monster_by_name(Npc.KASHYA)
        if npc:
            self._pather.walk_to_monster(npc)
            if self.interact_with_npc(Npc.KASHYA, "resurrect"):
                return Location.A1_KASHYA_CAIN
        self._npc_manager.open_npc_menu(Npc.KASHYA)
        self._npc_manager.press_npc_btn(Npc.KASHYA, "resurrect")
        return Location.A1_KASHYA_CAIN

    def open_wp(self, curr_loc: Location = Location.A1_TOWN_START) -> bool:
        Logger.debug("Opening Act 1 waypoint...")
        success = False
        self._pather.walk_to_poi("Rogue Encampment", time_out=15)
        obj = self._api.find_object("WaypointPortal")
        if obj:
            self._pather.walk_to_object(obj)
            success = self._pather.click_object("WaypointPortal", offset=(0, -20), target_menu=D2rMenu.Waypoint)
        if not success:
            Logger.warning("    Failed the first attempt at opening the waypoint, trying again...")
            wait(0.7)
            self._pather.walk_to_poi("Rogue Encampment", time_out=15)
            self._pather.click_poi("Rogue Encampment", offset=(0, -20), target_menu=D2rMenu.Waypoint)
            success = self._api.wait_for_menu(D2rMenu.Waypoint)
        return success

    def wait_for_tp(self) -> Union[Location, bool]:
        return Location.A1_KASHYA_CAIN

    def identify(self, curr_loc: Location = Location.A1_TOWN_START) -> Union[Location, bool]:
        npc = Npc.CAIN
        menu = "identify"
        self._pather.walk_to_monster(npc)
        if not self.interact_with_npc(npc, menu):
            if self._npc_manager.open_npc_menu(npc):
                self._npc_manager.press_npc_btn(npc, menu)
        return Location.A1_KASHYA_CAIN

    def _go_to_akara(self):
        npc = self._api.find_monster_by_name(Npc.AKARA)
        wander_pos = (200, 10)
        if not npc:
            self._pather.wander_towards(wander_pos, self._char, time_out = 5, iterations = 5)
            wait(0.1, 0.15)
            npc = self._api.find_monster_by_name(Npc.AKARA)
        if not npc:
            self._pather.wander_towards(wander_pos, self._char, time_out = 5, iterations = 5)
            wait(0.1, 0.15)
            npc = self._api.find_monster_by_name(Npc.AKARA)
        if npc:
            try:
                self._pather.walk_to_position(npc["position_area"], step_size=4)
                wait(0.4, 0.5)
            except:
                return False
        return True if npc else False

    def open_trade_menu(self, curr_loc: Location = Location.A1_TOWN_START) -> Union[Location, bool]:
        self._go_to_akara()
        if not self.interact_with_npc(Npc.AKARA, "trade"):
            self._npc_manager.open_npc_menu(Npc.AKARA)
            self._npc_manager.press_npc_btn(Npc.AKARA, "trade")
        return Location.A1_AKARA

    def open_stash(self, curr_loc: Location = Location.A1_TOWN_START) -> Union[Location, bool]:
        self._pather.walk_to_position((152, 66))
        wait(0.4, 0.5)
        self._pather.click_object("Bank", target_menu="stash")    
        return Location.A3_STASH_WP

    def heal(self, curr_loc: Location = Location.A1_TOWN_START) -> Union[Location, bool]:
        self._go_to_akara()
        self.interact_with_npc(Npc.AKARA, "trade")
        if self._api.wait_for_menu(D2rMenu.NpcInteract):
            keyboard.send("esc")
            wait(0.12, 0.15)
        return Location.A1_AKARA

    def open_trade_and_repair_menu(self, curr_loc: Location = Location.A1_TOWN_START) -> Union[Location, bool]:
        npc = self._api.find_npc(Npc.CHARSI)
        if npc:
            self._pather.walk_to_position(npc["position_area"])
            wait(0.4, 0.5)
        if not self.interact_with_npc(Npc.CHARSI, "trade_repair"):
            self._npc_manager.open_npc_menu(Npc.CHARSI)
            self._npc_manager.press_npc_btn(Npc.CHARSI, "trade_repair")
        return Location.A1_CHARSI
