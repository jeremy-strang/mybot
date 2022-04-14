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
    def can_stash(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        malah = self._api.find_monster_by_name("Malah")
        if malah and not self._pather.walk_to_monster(malah["id"]):
            self._pather.traverse_walking("Malah", self._char, obj=False, threshold=16, static_npc=True)
        self.interact_with_npc(Npc.MALAH, None)
        if self._api.wait_for_menu("npc_interact"):
            keyboard.send("esc")
        return Location.A5_MALAH

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        malah = self._api.find_monster_by_name("Malah")
        if malah and not self._pather.walk_to_monster(malah["id"]):
            self._pather.traverse_walking("Malah", self._char, obj=False, threshold=16, static_npc=True)
        if not self.interact_with_npc(Npc.MALAH):
            if self._npc_manager.open_npc_menu(Npc.MALAH):
                self._npc_manager.press_npc_btn(Npc.MALAH, "trade")
        return Location.A5_MALAH

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        self._pather.walk_to_poi("Harrogath", time_out=3)
        qual = self._api.find_monster_by_name("QualKehk")
        if qual and not self.interact_with_npc(Npc.QUAL_KEHK):
            if self._npc_manager.open_npc_menu(Npc.QUAL_KEHK):
                self._npc_manager.press_npc_btn(Npc.QUAL_KEHK, "resurrect")
            return Location.A5_QUAL_KEHK
        return False

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_walking("QualKehk",self._char, obj=False,threshold=10,static_npc=True): return False
        if self._npc_manager.open_npc_menu(Npc.CAIN):
            self._npc_manager.press_npc_btn(Npc.CAIN, "identify")
            return Location.A5_QUAL_KEHK
        return False

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        self._pather.walk_to_poi("Harrogath", time_out=3)
        bank = self._api.find_object("Bank")
        if bank and not self._pather.click_object("Bank"):
            if not self._pather.traverse_walking([119, 60],self._char, obj=False,threshold=10,static_npc=False,end_dist=10): return False
            self._pather.activate_poi("Bank", "Bank", collection='objects', char=self._char)    
            return Location.A5_LARZUK
        return Location.A5_LARZUK

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.walk_to_position([141, 43]): return False
        if not self.interact_with_npc(Npc.LARZUK, "trade_repair"):
            self._npc_manager.open_npc_menu(Npc.LARZUK)
            self._npc_manager.press_npc_btn(Npc.LARZUK, "trade_repair")
        return Location.A5_LARZUK

    def open_wp(self, curr_loc: Location) -> bool:
        self._pather.walk_to_poi("Harrogath")
        wait(0.7)
        self._pather.click_object("ExpansionWaypoint", (9.5, 0))
        return self._api.wait_for_menu("waypoint")

    def wait_for_tp(self) -> Union[Location, bool]:
        return Location.A5_TOWN_START
