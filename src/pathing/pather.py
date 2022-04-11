from ast import Tuple
import cv2
from pytest import skip
from char.skill import Skill
from utils.coordinates import world_to_abs
import numpy as np
import pyastar2d
from copy import deepcopy
import math
import time
from typing import Union
import random
from api import MapAssistApi
from screen import Screen
from config import Config
from utils.misc import is_in_roi, wait
from utils.custom_mouse import mouse
import mouse as _mouse
from logger import Logger
import collections
import keyboard
from scipy.spatial.distance import cdist
from scipy.spatial.distance import cityblock
from scipy.cluster.vq import kmeans
from utils.misc import unit_vector, clip_abs_point
from scipy.ndimage.filters import gaussian_filter
from pathing.path_finder import PathFinder

class Pather:
    def __init__(self, screen: Screen, api: MapAssistApi):
        self._api = api
        self._screen = screen
        self._config = Config()
        self._range_x = [-self._config.ui_pos["center_x"] +
                         7, self._config.ui_pos["center_x"] - 7]
        self._range_y = [-self._config.ui_pos["center_y"] + 7,
                         self._config.ui_pos["center_y"] - self._config.ui_pos["skill_bar_height"] - 33]
    
    def _should_abort_pathing(self) -> bool:
        if self._api.data:
            if self._api.data["should_chicken"]:
                Logger.warning(f"    Aborting pathing because chicken life threshold was reached")
                return True

            if self._api.data["inventory_open"]:
                Logger.warning(f"    Aborting pathing, inventory is open")
                return True
        return False

    def _adjust_abs_range_to_screen(self, abs_pos: tuple[float, float]) -> tuple[float, float]:
        """
        Adjust an absolute coordinate so it will not go out of screen or click on any ui which will not move the char
        :param abs_pos: Absolute position of the desired position to move to
        :return: Absolute position of a valid position that can be clicked on
        """
        f = 1.0
        # Check for x-range
        if abs_pos[0] > self._range_x[1]:
            f = min(f, abs(self._range_x[1] / float(abs_pos[0])))
        elif abs_pos[0] < self._range_x[0]:
            f = min(f, abs(self._range_x[0] / float(abs_pos[0])))
        # Check y-range
        if abs_pos[1] > self._range_y[1]:
            f = min(f, abs(self._range_y[1] / float(abs_pos[1])))
        if abs_pos[1] < self._range_y[0]:
            f = min(f, abs(self._range_y[0] / float(abs_pos[1])))
        # Scale the position by the factor f
        if f < 1.0:
            abs_pos = (int(abs_pos[0] * f), int(abs_pos[1] * f))
        # Check if adjusted position is "inside globe"
        screen_pos = self._screen.convert_abs_to_screen(abs_pos)
        if is_in_roi(self._config.ui_roi["mana_globe"], screen_pos) or is_in_roi(self._config.ui_roi["health_globe"], screen_pos):
            # convert any of health or mana roi top coordinate to abs (x-coordinate is just a dummy 0 value)
            new_range_y_bottom = self._screen.convert_screen_to_abs(
                (0, self._config.ui_roi["mana_globe"][1]))[1]
            f = abs(new_range_y_bottom / float(abs_pos[1]))
            abs_pos = (int(abs_pos[0] * f), int(abs_pos[1] * f))
        # Check if clicking on merc img
        screen_pos = self._screen.convert_abs_to_screen(abs_pos)
        if is_in_roi(self._config.ui_roi["merc_icon"], screen_pos):
            width = self._config.ui_roi["merc_icon"][2]
            height = self._config.ui_roi["merc_icon"][3]
            w_abs, h_abs = self._screen.convert_screen_to_abs((width, height))
            fw = abs(w_abs / float(abs_pos[0]))
            fh = abs(h_abs / float(abs_pos[1]))
            f = max(fw, fh)
            abs_pos = (int(abs_pos[0] * f), int(abs_pos[1] * f))
        return abs_pos

    def get_entity_coords_from_str(self, entity_str: str, collection: str="points_of_interest", entrance_in_wall=False) -> tuple[int, int]:
        data = self._api.get_data()
        key_dict = {
            "points_of_interest": "label",
            "objects": "name",
        }
        key = key_dict[collection] if collection in key_dict else None
        if key is None or data is None: return None

        entity = None
        for unit in data[collection]:
            if key in unit and unit[key].lower().startswith(entity_str.lower()):
                entity = unit
                break
        if entity is None: return None

        area_pos = entity["position"]
        if entrance_in_wall:
            if data["map"][area_pos[1] - 1][area_pos[0]] == 1:
                area_pos = [entity["position"][0], entity["position"][1] + 2]
            elif data["map"][area_pos[1] + 1][area_pos[0]] == 1:
                area_pos = [entity["position"][0], entity["position"][1] - 2]
            elif data["map"][area_pos[1]][area_pos[0] - 1] == 1:
                area_pos = [entity["position"][0] + 2, entity["position"][1]]
            elif data["map"][area_pos[1]][area_pos[0] + 1] == 1:
                area_pos = [entity["position"][0] - 2, entity["position"][1]]
        
        while area_pos[0] >= len(data["map"][0]):
            area_pos = area_pos - data["area_origin"]

        return area_pos

    def click_poi(self, poi_label: str, offset=None, time_out=2.5):
        start = time.time()
        data = self._api.data
        is_hovered = False
        if data and not self._should_abort_pathing():
            poi = self._api.find_poi(poi_label)
            is_hovered = poi and poi["is_hovered"]
            while poi and not is_hovered and time.time() - start < time_out:
                self.move_mouse_to_abs_pos(
                    world_to_abs(poi["position"], data["player_pos_world"]),
                    math.dist(data["player_pos_area"], poi["position"] - data["area_origin"]),
                    offset)
                is_hovered = self._api.wait_for_hover(poi, "points_of_interest")
            mouse.click(button="left")
            wait(0.5)
        return is_hovered

    def click_object(self, name: str, offset=None, time_out=2.5):
        start = time.time()
        data = self._api.data
        is_hovered = False
        if data and not self._should_abort_pathing():
            object = self._api.find_object(name)
            is_hovered = object and object["is_hovered"]
            while object and not is_hovered and time.time() - start < time_out:
                self.move_mouse_to_abs_pos(
                    world_to_abs(object["position"], data["player_pos_world"]),
                    math.dist(data["player_pos_area"], object["position"] - data["area_origin"]),
                    offset=offset)
                is_hovered = self._api.wait_for_hover(object, "objects")
                object = self._api.find_object(object["name"])
            Logger.debug(f"    Clicking object, confirmed hover: {is_hovered}")
            mouse.click(button="left")
            wait(0.5)
        return is_hovered
        # data = self._api.data
        # if data and not self._should_abort_pathing():
        #     object = self._api.find_object(name)
        #     if not object:
        #         wait(0.1, 0.2)
        #     self.move_mouse_to_object(object, offset)
        #     wait(0.1, 0.15)
        #     mouse.click(button="left")
        #     wait(0.5)
        # return True

    def move_mouse_to_abs_pos(self, position_abs, dist, offset=None):
        offset_x = offset[0] if offset != None else 0
        offset_y = offset[1] if offset != None else 0
        x = np.clip(position_abs[0], -638, 638)
        y = np.clip(position_abs[1], -350, 225)
        pos_m = self._screen.convert_abs_to_monitor([x, y])
        x_m = pos_m[0] + offset_x
        y_m = pos_m[1] + offset_y
        adjusted_pos_m = [x_m - 9.5, y_m - 39.5] if dist < 25 else [x_m, y_m]
        mouse.move(*adjusted_pos_m, delay_factor=[0.1, 0.2])

    def move_mouse_to_item(self, item, time_out=3.0):
        start = time.time()
        is_hovered = False
        while item and time.time() - start < time_out:
            self.move_mouse_to_abs_pos(item["position_abs"], item["dist"], offset=(5, -9.5))
            wait(0.2)
            item = self._api.find_item(item["id"])
            if item and item["is_hovered"]:
                return True
        return False

    def move_mouse_to_monster(self, monster, offset=None, confirm_hover=False):
        if monster:
            self.move_mouse_to_abs_pos(monster["position_abs"], monster["dist"])
            if confirm_hover:
                return self._api.wait_for_hover(monster)
        return True

    def move_mouse_to_object(self, target: dict, offset=None, confirm_hover=False):
        if type(target) is dict and "position_abs" in target and "dist" in target:
            self.move_mouse_to_abs_pos(target["position_abs"], target["dist"], offset)
            if confirm_hover:
                return self._api.wait_for_hover(target)
        return True

    def teleport_to_position(self, position: tuple[float, float], char):
        if self._api.data:
            data = self._api.data
            pos_world = position + data["area_origin"]
            dist = math.dist(pos_world, data['player_pos_world'])
            pos_abs = world_to_abs(pos_world, data['player_pos_world'])
            self.move_mouse_to_abs_pos(pos_abs, dist)
            char.pre_move()
            mouse.click(button="right")
            wait(char._cast_duration)

    def teleport_to_item(self, item, char):
        # If we failed to pick it up, try to teleport to it
        if item and char.can_tp:
            self.move_mouse_to_abs_pos(item["position_abs"], item["dist"])
            char.pre_move()
            mouse.click(button="right")
            wait(char._cast_duration)
            item = self._api.find_item(item['id'])

    def click_item(self, item: dict, char, time_out: float = 6.0, do_traverse=True, do_teleport=False):
        start = time.time()
        if item and do_teleport:
            item = self.teleport_to_item(item, char)

        if item and item["dist"] > 5.0 and do_traverse:
            Logger.debug(f"    Item {item['name']} (ID: {item['id']}) is {round(item['dist'], 1)}yds away, moving toward it...")
            if item["dist"] > 30 and char.can_tp:
                Logger.debug(f"        Item {item['name']} (ID: {item['id']}) is far away, traversing...")
                self.traverse(item["position_area"], char, dest_distance=4, time_out=time_out / 2)
            else:
                self.walk_to_item(item["id"], 3)
            item = self._api.find_item(item["id"])

        while item and time.time() - start < time_out:
            self.move_mouse_to_item(item)
            wait(0.03, 0.05)
            item = self._api.find_item(item["id"])
            if item:
                confirmed = item["is_hovered"]
                if confirmed or not self._api.data["hovered_unit"]:
                    mouse.click(button="left")
                elif self._api.data["hovered_unit"]:
                    keyboard.send(self._config.char["force_move"])
                wait(0.5)
                if confirmed:
                    inv_item = self._api.find_item(item["id"], "inventory_items")
                    if inv_item:
                        Logger.debug(f"    Clicked item {item['name']} (ID: {item['id']}), confirmed that it is now in inventory")
                        return True
                    else:
                        Logger.debug(f"    Clicked item {item['name']} (ID: {item['id']}), confirmed that it was hovered, but did not find it in inventory")
                item = self._api.find_item(item["id"])
        if item:
            return self.click_item(item, char, 3.0, do_traverse=False, do_teleport=True)
        return False

    def move_to_monster(self, char, monster: dict) -> bool:
        if self._should_abort_pathing(): return False
        monster = self._api.find_monster(monster["id"])
        if monster and type(monster) is dict:
            self.move_mouse_to_abs_pos(monster["position_abs"], monster["dist"])
            if char.can_tp:
                char.pre_move()
                mouse.click(button="right")
                wait(char._cast_duration)
            else:
                keyboard.send(self._config.char["force_move"])
                wait(0.5)
        else:
            return False
        return True

    def walk_to_monster(self, monster_id: int, time_out=10.0, step_size=4):
        dest = self._api.find_monster(monster_id)
        if dest:
            self.walk_to_position(dest["position_area"], time_out, step_size)
            return True
        return False

    def walk_to_item(self, item_id: int, time_out=10.0, step_size=4):
        dest = self._api.find_item(item_id)
        if dest:
            self.walk_to_position(dest["position_area"], time_out, step_size)
            return True
        return False

    def walk_to_object(self, obj_name: str, time_out=10.0, step_size=4):
        Logger.info(f"Walking to object {obj_name}...")
        dest = self._api.find_object(obj_name)
        if dest:
            self.walk_to_position(dest["position_area"], time_out, step_size)
            return True
        Logger.error(f"    No object found named {obj_name}")
        return False

    def walk_to_poi(self, poi_label: str, time_out=10.0, step_size=4):
        Logger.debug(f"Walking to POI {poi_label}")
        dest = self._api.find_poi(poi_label)
        if dest:
            self.walk_to_position(dest["position_area"], time_out, step_size)
            return True
        else:
            Logger.error(f"    POI {poi_label} not found")
        return False

    def walk_to_position(self, dest_area, time_out=15.0, step_size=4, threshold=10) -> bool:
        route = self.make_route_to_position(dest_area)
        return self.walk_route(route, time_out, step_size)

    def make_route_to_position(self, dest_area):
        route = None
        data = self._api.data
        if data:
            pf = PathFinder(self._api)
            dest_area = (int(dest_area[1]), int(dest_area[0]))
            player_area = (int(data["player_pos_area"][1]), int(data["player_pos_area"][0]))
            route = pf.make_path_astar(player_area, dest_area, False)
            self._api._current_path = route
        return route

    def _get_next_node(self, nodes, step_size=4, threshold=10) -> tuple[tuple[float, float], float]:
        if self._api.data and len(nodes) > 0:
            popped = 0
            node = nodes.pop(0)
            dist =  math.dist(node, self._api.data["player_pos_area"])
            while popped < step_size and len(nodes) > 0 and dist <= threshold:
                node = nodes.pop(0)
                dist = cityblock(node, self._api.data["player_pos_area"]) # math.dist(node, self._api.data["player_pos_area"])
                popped += 1
            return (node, dist)
        return (None, 0)

    def walk_route(self, route, time_out=15.0, step_size=4, threshold=10, final=3.0) -> bool:
        Logger.debug(f"Walking along route of length {len(route)} and step size {step_size}...")
        data = self._api.data
        steps = []
        end = route[-1]
        if route != None and len(route) > 0 and data != None:
            self._api._current_path = route
            prev = data["player_pos_area"]
            next, distance = self._get_next_node(route, step_size)
            start = time.time()
            while next != None and time.time() - start < time_out and not self._should_abort_pathing():
                data = self._api.data
                if not data:
                    time.sleep(0.2)
                    continue
                avg = ((next[0] + prev[0]) / 2, (next[1] + prev[1]) / 2) if len(steps) > 0 else next
                move_pos_abs = world_to_abs(avg, data['player_pos_area'] + data['player_offset'])
                move_pos_m = self._screen.convert_abs_to_monitor([move_pos_abs[0], move_pos_abs[1]], clip_input=True)
                mouse.move(*move_pos_m)
                keyboard.send(self._config.char["force_move"], do_release=False)
                steps.append(prev)
                prev = next
                next, distance = self._get_next_node(route, step_size)
                time.sleep(0.1)
            keyboard.release(self._config.char["force_move"])
            Logger.debug(f"    Done walking route, ended {distance} from {end}")
            self._api._current_path = steps
            time.sleep(0.2)
            return True
        return False

    def activate_waypoint(self,
                          obj: Union[tuple[int, int], str],
                          char,
                          entrance_in_wall: bool = True,
                          is_wp: bool = True
                        ) -> bool:
        Logger.info(f"Activating waypoint: {obj}")
        start = time.time()
        wp_menu = None
        data = self._api.data
        while not data:
            wait(0.1)
            data = self._api.data
        while time.time() - start < 20 and not self._should_abort_pathing():
            data = self._api.data
            if data and "map" in data:
                if is_wp:
                    wp_menu = data["waypoint_open"]
                    if wp_menu and is_wp:
                        return True

                pos_monitor = None
                if type(obj) == str:
                    for p in data["points_of_interest"]:
                        if p["label"].startswith(obj):
                            # find the gradient for the grid position and move one back
                            if entrance_in_wall:
                                ap = p["position"] - data["area_origin"]
                                if data["map"][ap[1] - 1][ap[0]] == 1:
                                    ap = [p["position"][0],
                                            p["position"][1] + 2]
                                elif data["map"][ap[1] + 1][ap[0]] == 1:
                                    ap = [p["position"][0],
                                            p["position"][1] - 2]
                                elif data["map"][ap[1]][ap[0] - 1] == 1:
                                    ap = [p["position"][0] +
                                            2, p["position"][1]]
                                elif data["map"][ap[1]][ap[0] + 1] == 1:
                                    ap = [p["position"][0] -
                                            2, p["position"][1]]
                                else:
                                    ap = p["position"]
                            else:
                                ap = p["position"]
                            #pos_monitor = self._api.world_to_abs_screen(ap)
                            # print(pos_monitor)
                            player_p = data['player_pos_area']
                            new_pos_mon = world_to_abs(
                                (ap-data["area_origin"]), player_p + data['player_offset'])
                            pos_monitor = [new_pos_mon[0], new_pos_mon[1]]

                            if -640 < pos_monitor[0] < 640 and -360 < pos_monitor[1] < 360:
                                pos_monitor = self._screen.convert_abs_to_monitor(
                                    pos_monitor)
                            else:
                                pos_monitor = None

                else:
                    player_p = data['player_pos_area']
                    new_pos_mon = world_to_abs((obj-data["area_origin"]), player_p+data['player_offset'])
                    pos_monitor = [new_pos_mon[0], new_pos_mon[1]]

                    if -640 < pos_monitor[0] < 640 and -360 < pos_monitor[1] < 360:
                        pos_monitor = self._screen.convert_abs_to_monitor(pos_monitor)
                    else:
                        pos_monitor = None
                if pos_monitor != None:
                    if is_wp and wp_menu:
                        return True
                    if is_wp and not wp_menu:
                        pos_monitor = [pos_monitor[0] - 9.5, pos_monitor[1] - 39.5]
                        
                        if data != None and data["should_chicken"]:
                            Logger.warning(f"    Aborting activate_waypoint() because chicken life threshold was reached")
                            return False

                        if data["inventory_open"]:
                            Logger.warning(f"    Aborting activate_waypoint(), inventory is open")
                            return False

                        mouse.move(*pos_monitor)
                        time.sleep(0.5)
                        mouse.click("left")
                        time.sleep(1)

                        data = self._api.get_data()
                        wp_menu = data["waypoint_open"]
                        if wp_menu and is_wp:
                            Logger.info("WP menu open!")
                            return True

                    if not is_wp:
                        if data != None and data["should_chicken"]:
                            Logger.warning(f"    Aborting activate_waypoint() because chicken life threshold was reached")
                            return False

                        if data["inventory_open"]:
                            Logger.warning(f"    Aborting activate_waypoint(), inventory is open")
                            return False

                        mouse.move(*pos_monitor)
                        time.sleep(0.25)
                        mouse.click("left")
                        return True

        return False
    
    def activate_poi(self,
                     poi: Union[tuple[int, int], str],
                     end_loc: str,
                     entrance_in_wall: bool = True,
                     collection="points_of_interest",
                     char=None,
                     offset: list = [0, 0]
                    ) -> bool:
        Logger.debug(f"Activating POI: {poi}")
        start = time.time()
        while time.time() - start < 20 and not self._should_abort_pathing():
            data = self._api.data
            if data:
                pos_monitor = None
                if type(poi) == str:
                    for p in data[collection]:
                        if collection == "points_of_interest":
                            ele = p["label"]
                        elif collection == "objects":
                            ele = p["name"]
                        if ele.startswith(poi):
                            obj = p
                            # find the gradient for the grid position and move one back
                            ap = p["position"] - data["area_origin"]
                            if entrance_in_wall:
                                if data["map"][ap[1] - 1][ap[0]] == 1:
                                    ap = [p["position"][0],
                                          p["position"][1] + 2]
                                elif data["map"][ap[1] + 1][ap[0]] == 1:
                                    ap = [p["position"][0],
                                          p["position"][1] - 2]
                                elif data["map"][ap[1]][ap[0] - 1] == 1:
                                    ap = [p["position"][0] +
                                          2, p["position"][1]]
                                elif data["map"][ap[1]][ap[0] + 1] == 1:
                                    ap = [p["position"][0] -
                                          2, p["position"][1]]
                                else:
                                    ap = p["position"]
                            ap = [ap[0] + offset[0], ap[1]+offset[1]]
                            #pos_monitor = self._api.world_to_abs_screen(ap)
                            player_p = data['player_pos_world'] + data['player_offset']
                            pos_monitor = world_to_abs(ap, player_p)
                            if -640 < pos_monitor[0] < 640 and -360 < pos_monitor[1] < 360:
                                pos_monitor = self._screen.convert_abs_to_monitor(
                                    pos_monitor)
                            else:
                                pos_monitor = None
                else:
                    player_p = data['player_pos_area']+data['player_offset']
                    pos_monitor = world_to_abs(poi, player_p)
                    if -640 < pos_monitor[0] < 640 and -360 < pos_monitor[1] < 360:
                        pos_monitor = self._screen.convert_abs_to_monitor(
                            pos_monitor)
                    else:
                        pos_monitor = None
                if pos_monitor != None:
                    if collection == "objects":
                        while (obj["mode"] == 0):

                            stash_menu = data["stash_open"]
                            if stash_menu:
                                Logger.debug('Stash menu opened!')
                                return True

                            player_p = data['player_pos_area'] + \
                                data['player_offset']
                            ap = obj["position"] - data["area_origin"]
                            pos_monitor = world_to_abs(ap, player_p)
                            pos_monitor = self._screen.convert_abs_to_monitor(pos_monitor)
                            if char != None:
                                if collection == "objects":
                                    self.traverse(poi, char, obj=True)
                                else:
                                    self.traverse(poi, char)
                            pos_monitor = [pos_monitor[0] - 9.5, pos_monitor[1]-39.5]

                            if data != None and data["should_chicken"]:
                                Logger.warning(f"    Aborting activate_poi() because chicken life threshold was reached")
                                return False

                            if data["inventory_open"]:
                                Logger.warning(f"    Aborting activate_poi(), inventory is open")
                                return False

                            mouse.move(*pos_monitor)
                            time.sleep(0.75)
                            mouse.click("left")
                            time.sleep(0.75)
                            data = self._api.get_data()
                            for p in data[collection]:
                                if p["name"].startswith(poi):
                                    obj["mode"] = p["mode"]
                    else:
                        pos_monitor = [pos_monitor[0]-9.5, pos_monitor[1]-39.5]
                        mouse.move(*pos_monitor)
                        time.sleep(0.25)
                        mouse.click("left")
                        # we did it!
                    return True
        return False

    def go_to_area(self,
                   poi: Union[tuple[int, int], str],
                   end_loc: str,
                   entrance_in_wall: bool = True,
                   randomize: int = 0,
                   time_out: float = 20.0,
                   char = None,
                   offset: tuple[int, int] = None,
                   ) -> bool:
        Logger.debug(f"Going to area: {poi}, end location: {end_loc}...")
        num_clicks = 0
        start = time.time()
        end_loc = end_loc.replace(" ", "")
        while time.time() - start < time_out and not self._should_abort_pathing():
            data = self._api.data
            if data:
                pos_abs = None
                pos_monitor = None
                if type(poi) == str:
                    for p in data["points_of_interest"]:
                        if p["label"].startswith(poi):
                            # find the gradient for the grid position and move one back
                            if entrance_in_wall:
                                ap = p["position"] - data["area_origin"]
                                if data["map"][ap[1] - 1][ap[0]] == 1:
                                    ap = [p["position"][0], p["position"][1] + 2]
                                elif data["map"][ap[1] + 1][ap[0]] == 1:
                                    ap = [p["position"][0], p["position"][1] - 2]
                                elif data["map"][ap[1]][ap[0] - 1] == 1:
                                    ap = [p["position"][0] + 2, p["position"][1]]
                                elif data["map"][ap[1]][ap[0] + 1] == 1:
                                    ap = [p["position"][0] - 2, p["position"][1]]
                                else:
                                    ap = p["position"]
                            else:
                                ap = p["position"]
                            dist = math.dist(ap, data['player_pos_area'])
                            mult = 1
                            if dist < 40:
                                mult = .5
                            #pos_monitor = self._api.world_to_abs_screen(ap)
                            player_p = data['player_pos_area']
                            pos_abs = world_to_abs(
                                (ap-data["area_origin"]), player_p+data['player_offset'])
                            pos_monitor = [pos_abs[0], pos_abs[1]]
                            if -640 < pos_monitor[0] < 640 and -360 < pos_monitor[1] < 360:
                                pos_monitor = self._screen.convert_abs_to_monitor(pos_monitor*mult)
                            else:
                                pos_monitor = None
                else:
                    player_p = data['player_pos_area']
                    pos_abs = world_to_abs((poi-data["area_origin"]), player_p + data['player_offset'])
                    pos_monitor = [pos_abs[0], pos_abs[1]]
                    if -640 < pos_monitor[0] < 640 and -360 < pos_monitor[1] < 360:
                        pos_monitor = self._screen.convert_abs_to_monitor(pos_monitor)
                    else:
                        pos_monitor = None

                if pos_monitor is not None:
                    random.seed()
                    pos_monitor = (pos_monitor[0] + random.randint(-randomize, +randomize),
                                   pos_monitor[1] + random.randint(-randomize, +randomize))
                    pos_monitor = [pos_monitor[0]-9.5, pos_monitor[1]-39.5]
                    if offset is not None:
                        pos_monitor = [pos_monitor[0] + offset[0], pos_monitor[1] + offset[1]]

                    if data is not None and data["should_chicken"]:
                        Logger.warning(f"    Aborting go_to_area() because chicken life threshold was reached")
                        return False

                    if data["inventory_open"]:
                        Logger.warning(f"    Aborting go_to_area(), inventory is open")
                        return False

                    _mouse.move(*pos_monitor, duration=.07)
                    wait(0.1, 0.15)
                    mouse.press(button="left")
                    wait(0.04, 0.05)
                    mouse.release(button="left")

                    num_clicks += 1
                    wait(0.5, 0.6)
                    if num_clicks == 10 and char is not None:
                        char.pre_move()
                        char.move(pos_monitor, force_tp=True)
                    if num_clicks == 12:
                        randomize += 2
                    if num_clicks == 15 and char is not None:
                        char.reposition(pos_abs)
                    if num_clicks == 17:
                        randomize += 3
                    if num_clicks == 20:
                        char.reposition(pos_abs)
                    if num_clicks == 22:
                        randomize += 4
                    data = self._api.get_data()
                if data["current_area"] == end_loc:
                    Logger.debug(f"Done going to area {end_loc} after {time.time() - start} sec")
                    return True
        Logger.debug(f"Failed to confirm arrival at {end_loc}")
        return False

    def traverse_walking(self,
                         end: Union[str, tuple[int, int]],
                         char,
                         obj: bool = False,
                         x: int = 0,
                         y: int = 0,
                         threshold=4,
                         static_npc=False,
                         end_dist=19,
                         time_out=50.0
                        ):
        """Slightly different traversal for moving in town/walking"""
        Logger.debug(f"Traverse (walking) to: {end}")
        char.pre_move()
        data = None
        sucess = False
        start = time.time()
        rand = [0, 0]
        random_offset = 0
        pf = PathFinder(self._api)

        while (time.time() - start < time_out or not sucess) and not self._should_abort_pathing():
            data = self._api.get_data()
            if data and "map" in data and data["map"] is not None:
                if type(end) is str and obj is False:
                    if static_npc == True:
                        for p in data["static_npcs"]:
                            if p["name"].startswith(end):
                                map_pos = p["position"] - data["area_origin"]
                                x = map_pos[0]
                                y = map_pos[1]
                                break
                    else:
                        for p in data["points_of_interest"]:
                            if p["label"].startswith(end):
                                map_pos = p["position_area"]
                                x = map_pos[0]
                                y = map_pos[1]
                                break
                        for p in data["monsters"]:
                            if p["name"].startswith(end):
                                map_pos = p["position_area"]
                                x = map_pos[0]
                                y = map_pos[1]
                                break
                elif obj is True:
                    for p in data["objects"]:
                        if p["name"].startswith(end):
                            map_pos = p["position_area"]
                            x = map_pos[0]
                            y = map_pos[1]
                            break
                else:
                    x = end[0]
                    y = end[1]

                target_x = x + data["area_origin"][0]
                target_y = y + data["area_origin"][1]
                player_x = data["player_pos_world"][0]
                player_y = data["player_pos_world"][1]

                player_x_area = data["player_pos_area"][0]
                player_y_area = data["player_pos_area"][1]

                odist = math.dist([target_x, target_y],
                                  [player_x, player_y])

                # make paths
                if data['map'] is not None:
                    player_pos_area = (int(player_y_area), int(player_x_area))
                    dest_pos_area = (int(y), int(x))
                    # path_data = make_path_astar(player_local, dest, data["map"])
                    path_data = pf.make_path_astar(player_pos_area, dest_pos_area)
                    self._api._current_path = path_data
                    if path_data:
                        target = path_data
                        end_click_pt = target[-1]
                        random_offset = 0
                    else:
                        random_offset += 1
                        Logger.debug('invalid path increasing search')
                        random.seed(random_offset+123)
                        RX = random.randint(-random_offset, +random_offset)
                        random.seed(random_offset-43)
                        RY = random.randint(-random_offset, +random_offset)
                        rand = np.array([RX, RY])
                        if random_offset > 15:
                            return False
                        continue
                else:
                    continue

                if path_data:
                    keyboard.send(char._char_config["force_move"], do_release=False)

                self._api._current_path = target
                moves = 0
                if target is None:
                    Logger.debug('Invalid path: ' + str(target_x) + ' ' + str(target_y))
                    sucess = True
                    return False
                pp = [0, 0]
                randomize = 0
                prev_p = [0, 0]
                delta_p = 0
                while len(target) > 0 and time.time() - start < time_out:
                    try:
                        data = self._api.get_data()
                    except:
                        pass
                    player_x = data["player_pos_world"][0]
                    player_y = data["player_pos_world"][1]

                    delta_p = math.dist(prev_p, data["player_pos_world"])

                    wp_x = target[0][0] + data["area_origin"][0]
                    wp_y = target[0][1] + data["area_origin"][1]

                    odist = math.dist([wp_x, wp_y], [player_x, player_y])

                    end_x = end_click_pt[0] + data["area_origin"][0]
                    end_y = end_click_pt[1] + data["area_origin"][1]

                    end = math.dist([end_x, end_y], [player_x, player_y])

                    # distance threshold to target
                    if end < end_dist:
                        sucess = True
                        keyboard.send(
                            char._char_config["force_move"], do_press=False)
                        Logger.info('Walked to destination')
                        return True
                        # break

                    # how close to a node before we remove it
                    if odist < threshold:
                        try:
                            target.pop(0)
                        except:
                            pass
                        try:
                            target.pop(0)
                        except:
                            pass

                    # out of paths to traverse
                    if len(target) < 1:
                        keyboard.send(
                            char._char_config["force_move"], do_press=False)
                        return True

                    player_p = data['player_pos_area'] + data['player_offset']

                    player_offset = data['player_offset']

                    new_pos_mon = world_to_abs(
                        [target[0][0], target[0][1]], player_p+data['player_offset'])
                    random.seed()

                    new_pos_mon = (new_pos_mon[0] + random.randint(-randomize, +randomize),
                                    new_pos_mon[1] + random.randint(-randomize, +randomize))
                    if delta_p < 1:
                        # increase random offset to get around stuck
                        randomize += 5
                    else:
                        randomize = 0
                    prev_p = data["player_pos_world"]

                    zero = self._screen.convert_abs_to_monitor(
                        [new_pos_mon[0]-9.5, new_pos_mon[1]-39.5])

                    if moves != 0:
                        # average paths with previous point
                        zero = [(zero[0]+pp[0])/2, (zero[1]+pp[1])/2]
                    else:
                        pp = zero

                    _mouse.move(*zero, duration=.025)

                    pp = zero
                    moves += 1

                    if moves > 530:
                        sucess = True
                        keyboard.send(
                            char._char_config["force_move"], do_press=False)
                        return False

                keyboard.send(
                    char._char_config["force_move"], do_press=False)
                return True
            else:
                wait(0.5)
        keyboard.release(char._char_config["force_move"])
        return True

    def traverse(self,
                 end: Union[str, tuple[int, int]],
                 char,
                 randomize: int = 0,
                 do_pre_move: bool = True,
                 obj: bool = False,
                 force: bool = True,
                 kill: bool = False,
                 pickit=None,
                 verify_location=False,
                 time_out=20.0,
                 dest_distance=15,
                 jump_distance=15,
                ):
        """
        Traverse to another location
        :param end: Either world coordinates as tuple [x, y] or a string e.g. 'Worldstone Keep Level 3'
        :param char
        :return: bool if successfull
        """
        Logger.debug(f"Traversing to {end}")
        if do_pre_move:
            char.pre_move()
        # reduce casting frame duration since we can check for teleport skill used in memory
        tmp_duration = char._cast_duration
        char._cast_duration = max(0.18, char._cast_duration - 0.3)
        last_pos = None
        last_node_pos_abs = None
        repeated_pos_count = 0
        reached_destination = 2
        hard_exit = 0
        start = time.time()
        while time.time() - start < time_out and not self._should_abort_pathing():
            data = self._api.get_data()
            if data is None:
                Logger.warning(f"    Couldnt get API, data retrying...")
                wait(0.1)
                continue
            
            if "map" in data and data["map"] is not None:
                player_pos_area = data["player_pos_area"]
                if data["used_skill"] == "Teleport":
                    time.sleep(0.01)
                    continue

                # Some fail save checking for when we get stuck
                if last_pos is not None and np.array_equal(player_pos_area, last_pos):
                    repeated_pos_count += 1
                    if repeated_pos_count == 2 and last_node_pos_abs is not None:
                        char.reposition(last_node_pos_abs)
                    if repeated_pos_count == 4 and last_node_pos_abs is not None:
                        char.reposition(last_node_pos_abs)
                    if repeated_pos_count == 6 and last_node_pos_abs is not None:
                        char.reposition(last_node_pos_abs)
                    if repeated_pos_count == 8:
                        Logger.debug("Increasing end point reached range")
                        reached_destination += 5
                    elif repeated_pos_count > 18:
                        Logger.warning("Got stuck during pathing")
                        char._cast_duration = tmp_duration
                        return False
                else:
                    repeated_pos_count = 0
                last_pos = player_pos_area

                # Get endpoint
                area_pos = None
                if type(end) is str and obj is False:
                    for poi in data["points_of_interest"]:
                        if poi["label"].startswith(end):
                            area_pos = poi["position"] - data["area_origin"]
                elif type(end) is str and obj is True:
                    for poi in data["objects"]:
                        if poi["name"].startswith(end):
                            area_pos = poi["position"] - data["area_origin"]
                else:
                    area_pos = end
                if area_pos is None:
                    if hard_exit < 10:
                        data = self._api.get_data()
                        hard_exit += 1
                        # seems like the data isnt loading in time here, just try again
                        Logger.warning(f"Couldnt find endpoint: {end} trying one more time...")
                        char._cast_duration = tmp_duration
                        continue
                    Logger.warning(f"Couldnt find endpoint: {end}")
                    char._cast_duration = tmp_duration
                    return False

                # Calc route from player to entrance
                weighted_map = deepcopy(data["map"])
                weighted_map = weighted_map.astype(np.float32)
                weighted_map[weighted_map == 0] = 999999
                weighted_map[weighted_map == 1] = 1
                start_pos = np.array([player_pos_area[1], player_pos_area[0]])
                end_pos = np.array([area_pos[1], area_pos[0]])
                weighted_map[end_pos[0]][end_pos[1]] = 1
                route = pyastar2d.astar_path(weighted_map, start_pos, end_pos, allow_diagonal=False)

                route_list = route.tolist()
                decimation = []

                prev_node = route_list[0]
                for node in route_list:
                    # manhattan distance from our current step to the next node
                    d = cityblock(node, prev_node)
                    if d > jump_distance:
                        # if its greater than how far we can teleport save it
                        decimation.append(node)
                        prev_node = node

                if len(decimation) == 0:
                    decimation.append(end_pos)
                route_list = decimation
                route_list[-1] = end_pos

                self._api._current_path = None
                self._api._astar_current_path = decimation

                for i in range(len(route_list)):
                    node = np.array(route_list[i])
                    node_pos_w = [node[1], node[0]]
                    data = self._api.get_data()
                    player_pos = data['player_pos_area']+data['player_offset']
                    node_pos_abs = last_node_pos_abs = world_to_abs(node_pos_w, player_pos)
                    node_pos_m = self._screen.convert_abs_to_monitor(node_pos_abs, clip_input=True)

                    if math.dist(player_pos, node_pos_w) < 10:
                        continue

                    if self._should_abort_pathing():
                        char._cast_duration = tmp_duration
                        return False

                    char.move((node_pos_m[0], node_pos_m[1]), force_move=force)

                    if i > len(route_list)-4:
                        time.sleep(.4)
                data = self._api.get_data()
                player_pos = data['player_pos_area'] + data['player_offset']
                recalc_dist = math.dist(player_pos, area_pos)
                if recalc_dist < dest_distance and verify_location:
                    Logger.debug(f"Traverse to {end} completed ({round(recalc_dist, 2)} from destination)")
                    char._cast_duration = tmp_duration
                    return True
                elif not verify_location:
                    char._cast_duration = tmp_duration
                    return True
                else:
                    Logger.warning(f"Ended too early, recalculating pathing..." + str(recalc_dist))

            time.sleep(0.02)
            self._api._astar_current_path = None
            char._cast_duration = tmp_duration
        return False

    @staticmethod
    def _closest_node(node, nodes):
        return nodes[cdist([node], nodes).argmin()]

    @staticmethod
    def _find_next_node(route, p):
        for r in route:
            dist = math.dist([r[1], r[0]], p)
            if dist < 29:
                return r
        return None

    def wait_for_location(self, name, time_out: float = 10.0) -> bool:
        start = time.time()
        while time.time() - start < time_out:
            data = self._api.data
            if data and data["current_area"] == name:
                return True
            time.sleep(0.1)
        return False

    def wait_for_town(self, time_out: float = 10.0) -> bool:
        start = time.time()
        while time.time() - start < time_out:
            data = self._api.data
            if data != None:
                if data["in_town"]:
                    return True
            time.sleep(0.1)
        return False
