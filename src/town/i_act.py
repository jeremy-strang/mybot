import time
import keyboard
from typing import Union
from logger import Logger
from pathing import Location
from char import IChar
from screen import Screen
from config import Config
from npc_manager import NpcManager, Npc
from pathing import OldPather, Location
from pathing import Pather
from d2r import D2rApi, D2rMenu
from typing import Union
from template_finder import TemplateFinder
from utils.misc import wait
from utils.custom_mouse import mouse

class IAct:
    def __init__(self, screen: Screen, template_finder: TemplateFinder, old_pather: OldPather, char: IChar, npc_manager: NpcManager, pather: Pather, api: D2rApi):
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

    def close_menus(self):
        wait(0.1)
        data = self._api.wait_for_data()
        if data and data["any_menu_open"]:
            Logger.debug(f"Detected {', '.join(list(data['open_menus']))} menu open, closing")
            keyboard.send("esc")
            wait(0.05)

    def click_trade_button(self, npc: Union[dict, str], y_offset: int = 0) -> bool:
        if type(npc) is str:
            npc = self._api.find_monster_by_name(npc)
        elif type(npc) is dict:
            npc = self._api.find_monster_by_name(npc["name"])
        if npc:
            mon_x, mon_y = self._screen.convert_abs_to_monitor(npc["position_abs"])
            mon_x = mon_x - 9.5
            mon_y = mon_y - 39.5 - 153
            mouse.move(mon_x, mon_y + y_offset)
            wait(0.1)
            mouse.click(button="left")
            wait(2)
        return False

    def find_vendor_and_open_trade(self, npc_name: Npc, menu_selection: str = "trade", confirm_menu: D2rMenu = D2rMenu.NpcShop, y_offset: int = 0) -> bool:
        success = False
        npc = self._api.find_monster_by_name(npc_name)
        if npc and npc["dist"] > 10:
            self._pather.walk_to_monster(npc_name)
            wait(0.1)
        npc = self._api.find_monster_by_name(npc_name)
        if npc and self.interact_with_npc(npc_name, None):
            wait(0.1)
            if menu_selection is not None:
                self.click_trade_button(npc, y_offset=y_offset)
            if confirm_menu is not None:
                success = self._api.wait_for_menu(confirm_menu)
            else:
                success = True
        if success:
            Logger.debug(f"Successfully opened NPC vendor menu ({npc_name}) using only memory")
        else:
            Logger.debug(f"Failed to open menu using memory, using pixels instead")
        
        if not success and not self.interact_with_npc(npc_name, menu_selection):
            if self._npc_manager.open_npc_menu(npc_name):
                self._npc_manager.press_npc_btn(npc_name, menu_selection)
                return True
        return success

    def interact_with_npc(self, npc: Npc, menu_selection: str = "trade") -> bool:
        result = False
        m = self._api.find_monster_by_name(npc)
        if m is not None:
            menu_open = False
            start = time.time()
            while not menu_open and time.time() - start < 10:
                m = self._api.find_monster_by_name(npc)
                self._pather.move_mouse_to_abs_pos(m["position_abs"], m["dist"])
                wait(0.05)
                m = self._api.find_monster_by_name(npc)
                if m is not None:
                    mouse.click(button="left")
                    menu_open = self._api.wait_for_menu("npc_interact")
                    if menu_open:
                        if menu_selection is not None:
                            self._npc_manager.press_npc_btn(npc, menu_selection)
                        result = True
                        break
        return result
