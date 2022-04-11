import pprint
import time
from typing import Union
from pathing import Location
from char import IChar
from screen import Screen
from config import Config
from npc_manager import NpcManager, Npc
from pathing import OldPather, Location
from pathing import Pather
from d2r_mem import D2rMemApi
from typing import Union
from template_finder import TemplateFinder
from utils.misc import wait
from utils.custom_mouse import mouse
pp = pprint.PrettyPrinter(depth=6)

class IAct:
    def __init__(self, screen: Screen, template_finder: TemplateFinder, old_pather: OldPather, char: IChar, npc_manager: NpcManager, pather: Pather, api: D2rMemApi):
        self._config = Config()
        self._screen = screen
        self._old_pather = old_pather
        self._char = char
        self._npc_manager = npc_manager
        self._template_finder = template_finder
        self._pather = pather
        self._api = api

    # Open waypoint menu
    def open_wp(self, curr_loc: Location) -> bool: return False
    
    # Get Location that is closest to waypoint to continue pathing from there
    def get_wp_location(self) -> Location: pass
    
    # Wait until we arrive in town after using town portal (by searching for templates close it)
    def wait_for_tp(self) -> Union[Location, bool]: return False

    # Is buying pots implemented for this Town?
    def can_buy_pots(self) -> bool: return False
    
    # Is healing implemented for this Town?
    def can_heal(self) -> bool: return False
    
    # Is merc resurrection implemented for this Town?
    def can_resurrect(self) -> bool: return False
    
    # Is stashing implemented in this Town?
    def can_stash(self) -> bool: return False
    
    # Is trade/repair implemented in this Town?
    def can_trade_and_repair(self) -> bool: return False
    
    # Is merc resurrection implemented for this Town?
    def can_identify(self) -> bool: return False    
    
    def can_gamble(self) -> bool: return False
    
    # If any of the above functions return True for the Town, the respective method must be implemented
    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]: return False
    
    def heal(self, curr_loc: Location) -> Union[Location, bool]: return False
    
    def resurrect(self, curr_loc: Location) -> Union[Location, bool]: return False
    
    def open_stash(self, curr_loc: Location) -> Union[Location, bool]: return False
    
    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]: return False
    
    def identify(self, curr_loc: Location) -> Union[Location, bool]: return False
    
    def gamble (self, curr_loc: Location) -> Union[Location, bool]: return False

    def trade_with_npc(self, npc: Npc, action_btn_key="trade") -> bool:
        m = self._api.find_npc(npc)
        if m is not None:
            menu_open = False
            start = time.time()
            while not menu_open and time.time() - start < 10:
                m = self._api.find_npc(npc)
                self._pather.move_mouse_to_abs_pos(m["position_abs"], m["dist"])
                if m is not None:
                    mouse.click(button="left")
                    wait(1.0)
                    # pp.pprint(m)
                    data = self._api.get_data()
                    menu_open = data is not None and data["npc_interact_open"]
                    if menu_open:
                        self._npc_manager.press_npc_btn(npc, action_btn_key)
                        return True
        return False
