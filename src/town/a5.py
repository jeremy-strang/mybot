from char import IChar
from town.i_act import IAct
from screen import Screen
from config import Config
from npc_manager import NpcManager, Npc
from pather import Pather, Location
from pather_v2 import PatherV2
from typing import Union
from template_finder import TemplateFinder
from utils.misc import wait

class A5(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, pather: Pather, char: IChar, npc_manager: NpcManager,pather_v2: PatherV2):
        self._config = Config()
        self._screen = screen
        self._pather = pather
        self._char = char
        self._npc_manager = npc_manager
        self._template_finder = template_finder
        self._pather_v2 = pather_v2

    def get_wp_location(self) -> Location: return Location.A5_WP
    def can_heal(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_resurrect(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_stash(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        #malah static location
        if not self._pather_v2.traverse_walking("Malah",self._char, obj=False,threshold=10,static_npc=True,end_dist=0): return False
        #malah location of instance
        if not self._pather_v2.traverse_walking("Malah",self._char, obj=False,threshold=10,static_npc=False,end_dist=0): return False
        if not self._npc_manager.open_npc_menu(Npc.MALAH): return False
        if not self._pather.traverse_nodes((Location.A5_MALAH, Location.A5_TOWN_START), self._char, force_move=True): return False
        return Location.A5_TOWN_START

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        #75 24
        #if not self._pather.traverse_nodes((curr_loc, Location.A5_MALAH), self._char, force_move=True): return False
        if not self._pather_v2.traverse_walking("Malah",self._char, obj=False,threshold=10,static_npc=True,end_dist=0): return False
        if not self._pather_v2.traverse_walking("Malah",self._char, obj=False,threshold=10,static_npc=False,end_dist=0): return False
        if self._npc_manager.open_npc_menu(Npc.MALAH):
            self._npc_manager.press_npc_btn(Npc.MALAH, "trade")
            return Location.A5_MALAH
        return False

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        #if not self._pather.traverse_nodes((curr_loc, Location.A5_QUAL_KEHK), self._char): return False
        if not self._pather_v2.traverse_walking("QualKehk",self._char, obj=False,threshold=10,static_npc=True): return False
        if self._npc_manager.open_npc_menu(Npc.QUAL_KEHK):
            self._npc_manager.press_npc_btn(Npc.QUAL_KEHK, "resurrect")
            return Location.A5_QUAL_KEHK
        return False

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        #if not self._pather.traverse_nodes((curr_loc, Location.A5_QUAL_KEHK), self._char): return False
        if not self._pather_v2.traverse_walking("QualKehk",self._char, obj=False,threshold=10,static_npc=True): return False
        if self._npc_manager.open_npc_menu(Npc.CAIN):
            self._npc_manager.press_npc_btn(Npc.CAIN, "identify")
            return Location.A5_QUAL_KEHK
        return False

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        #if not self._pather_v2.traverse_walking("Bank",self._char, obj=True,threshold=8,static_npc=False,end_dist=6): return False
        if not self._pather_v2.traverse_walking([127,58],self._char, obj=False,threshold=8,static_npc=False,end_dist=6): return False
        self._pather_v2.activate_poi ("Bank", "Bank", typ='objects', char=self._char)    
        return Location.A5_STASH

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather_v2.traverse_walking([141,43],self._char, obj=False,threshold=10,static_npc=False,end_dist=5): return False
        self._npc_manager.open_npc_menu(Npc.LARZUK)
        self._npc_manager.press_npc_btn(Npc.LARZUK, "trade_repair")
        return Location.A5_LARZUK

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather_v2.traverse_walking("Harrogath",self._char, obj=False,threshold=10): return False
        wait(0.5, 0.7)
        return self._pather_v2.activate_waypoint("Harrogath", self._char,entrance_in_wall=False, is_wp = True)



    def wait_for_tp(self) -> Union[Location, bool]:
        success = self._template_finder.search_and_wait(["A5_TOWN_1", "A5_TOWN_0"], time_out=20).valid
        if success:
            return Location.A5_TOWN_START
        return False
