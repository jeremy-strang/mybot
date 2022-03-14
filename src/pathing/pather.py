from ast import Tuple
import cv2
from mas import world_to_abs
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

    def activate_waypoint(self, obj: Union[tuple[int, int], str], char, entrance_in_wall: bool = True, is_wp: bool = True) -> bool:
        start = time.time()
        wp_menu = None
        data = None
        while data is None:
            data = self._api.get_data()

        while time.time() - start < 20:
            data = self._api.get_data()
            if data is not None:
                if data is not None and "map" in data and data["map"] is not None:
                    if is_wp:
                        wp_menu = data['menus']['Waypoint']
                        if wp_menu and is_wp:
                            return True

                    pos_monitor = None
                    if type(obj) == str:
                        for p in data["poi"]:
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
                                    (ap-data["area_origin"]), player_p+data['player_offset'])
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
                    if pos_monitor is not None:
                        if is_wp and wp_menu:
                            return True
                        if is_wp and not wp_menu:
                            pos_monitor = [pos_monitor[0] - 9.5, pos_monitor[1]-39.5]
                            mouse.move(*pos_monitor)
                            time.sleep(0.5)
                            mouse.click("left")

                            time.sleep(1)

                            data = self._api.get_data()
                            wp_menu = data['menus']['Waypoint']
                            if wp_menu and is_wp:
                                Logger.info('WP menu open!')
                                return True

                        if not is_wp:
                            mouse.move(*pos_monitor)
                            time.sleep(0.25)
                            mouse.click("left")
                            return True

        return False

    def activate_poi(self, poi: Union[tuple[int, int], str], end_loc: str, entrance_in_wall: bool = True, typ="poi", char=None, offset: list = [0, 0]) -> bool:
        start = time.time()
        while time.time() - start < 20:
            data = self._api.get_data()
            if data is not None:
                pos_monitor = None
                if type(poi) == str:
                    for p in data[typ]:
                        if typ == "poi":
                            ele = p["label"]
                        elif typ == "objects":
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
                            player_p = data['player_pos_world'] + \
                                data['player_offset']
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
                if pos_monitor is not None:
                    if typ == "objects":
                        counter = 0
                        while (obj["mode"] == 0):

                            stash_menu = data['menus']['Stash']
                            if stash_menu:
                                Logger.debug('Stash menu opened!')
                                return True

                            player_p = data['player_pos_area'] + \
                                data['player_offset']
                            ap = obj["position"] - data["area_origin"]
                            pos_monitor = world_to_abs(ap, player_p)
                            pos_monitor = self._screen.convert_abs_to_monitor(
                                pos_monitor)
                            if char is not None:
                                if typ == "objects":
                                    self.traverse(poi, char, obj=True)
                                else:
                                    self.traverse(poi, char)
                            pos_monitor = [pos_monitor[0] -
                                           9.5, pos_monitor[1]-39.5]
                            mouse.move(*pos_monitor)
                            time.sleep(0.75)
                            mouse.click("left")
                            time.sleep(0.75)
                            if counter == 2:
                                if char is not None:
                                    monster = char.kill_around(self._api, 1, 5, True)
                                    if type(monster) == dict:
                                        char.kill_uniques(monster)
                            elif counter > 5:
                                return False
                            data = self._api.get_data()
                            for p in data[typ]:
                                if p["name"].startswith(poi):
                                    obj["mode"] = p["mode"]

                            counter += 1
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
                   char = None
                   ) -> bool:
        Logger.debug(f"Going to area: {poi}, location: {end_loc}...")
        num_clicks = 0
        start = time.time()
        while time.time() - start < time_out:
            data = self._api.get_data()
            if data is not None:
                pos_monitor = None
                if type(poi) == str:
                    for p in data["poi"]:
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
                            new_pos_mon = world_to_abs(
                                (ap-data["area_origin"]), player_p+data['player_offset'])
                            pos_monitor = [new_pos_mon[0], new_pos_mon[1]]
                            if -640 < pos_monitor[0] < 640 and -360 < pos_monitor[1] < 360:
                                pos_monitor = self._screen.convert_abs_to_monitor(pos_monitor*mult)
                            else:
                                pos_monitor = None
                else:
                    player_p = data['player_pos_area']
                    new_pos_mon = world_to_abs((poi-data["area_origin"]), player_p + data['player_offset'])
                    pos_monitor = [new_pos_mon[0], new_pos_mon[1]]
                    if -640 < pos_monitor[0] < 640 and -360 < pos_monitor[1] < 360:
                        pos_monitor = self._screen.convert_abs_to_monitor(pos_monitor)
                    else:
                        pos_monitor = None

                if pos_monitor is not None:
                    random.seed()
                    pos_monitor = (pos_monitor[0] + random.randint(-randomize, +randomize),
                                   pos_monitor[1] + random.randint(-randomize, +randomize))
                    pos_monitor = [pos_monitor[0], pos_monitor[1]]
                    _mouse.move(*pos_monitor, duration=.025)
                    time.sleep(0.1)
                    mouse.press(button="left")
                    time.sleep(.1)
                    mouse.release(button="left")
                    num_clicks += 1
                    if num_clicks == 10: randomize += 1
                    if num_clicks == 15: randomize += 2
                    if num_clicks == 20: randomize += 3
                if data["current_area"] == end_loc:
                    Logger.debug(f"Done going to area {end_loc} after {time.time() - start} sec")
                    return True
        Logger.debug(f"Failed to confirm arrival at {end_loc}")
        return False

    def move_mouse_to_abs_pos(self, abs_screen_position, dist):
        x = np.clip(abs_screen_position[0], -638, 638)
        y = np.clip(abs_screen_position[1], -350, 225)
        pos_m = self._screen.convert_abs_to_monitor([x, y])
        x_m = pos_m[0]
        y_m = pos_m[1]
        adjusted_pos_m = [x_m - 5, y_m - 35] if dist < 25 else [x_m, y_m]
        mouse.move(*adjusted_pos_m, delay_factor=[0.1, 0.2])

    def move_mouse_to_monster(self, monster):
        self.move_mouse_to_abs_pos(monster["abs_screen_position"], monster["dist"])

    def move_to_monster(self, char, monster: dict) -> bool:
        if monster is not None and type(monster) is dict:
            self.move_mouse_to_abs_pos(monster["abs_screen_position"], monster["dist"])
            if char.capabilities.can_teleport_natively:
                char.pre_move()
                mouse.click(button="right")
                wait(char._cast_duration)
            else:
                mouse.click(button="left")
                wait(0.7)
        else:
            return False
        return True

    def traverse_route(self, route, char, time_out=10):
        if route is not None:
            dist = 0
            next = route.pop(0)
            start = time.time()
            while len(route) > 0 and time.time() - start < time_out:
                data = self._api.get_data()
                wp_x = next[0] + data["area_origin"][0]
                wp_y = next[1] + data["area_origin"][1]
                player_pos_world = data["player_pos_world"]
                dist = math.dist(
                    [wp_x, wp_y], [player_pos_world[0], player_pos_world[1]])
                move_pos_abs = world_to_abs(
                    next, data['player_pos_area'] + data['player_offset'])
                move_pos_m = self._screen.convert_abs_to_monitor(
                    [move_pos_abs[0], move_pos_abs[1]])
                mouse.move(*move_pos_m)
                keyboard.send(self._config.char["force_move"])
                wait(0.5)
                data = self._api.get_data()
                dist = math.dist(
                    [wp_x, wp_y], [player_pos_world[0], player_pos_world[1]])
                if dist < 25:
                    next = route.pop(0)

    def traverse_walking(self, end: Union[str, tuple[int, int]], char, obj: bool = False, x: int = 0, y: int = 0, threshold=4, static_npc=False, end_dist=19):
        """slightly different traversal for moving in town/walking"""
        char.pre_move()
        data = None
        sucess = False
        start = time.time()
        rand = [0, 0]
        random_offset = 0

        while time.time() - start < 50 or sucess is False:
            data = self._api.get_data()
            if data is not None:
                if data is not None and "map" in data and data["map"] is not None:
                    if type(end) is str and obj is False:
                        if static_npc == True:
                            for p in data["static_npcs"]:
                                if p["name"].startswith(end):
                                    map_pos = p["position"] - data["area_origin"]
                                    x = map_pos[0]
                                    y = map_pos[1]
                                    break
                        else:
                            for p in data["poi"]:
                                if p["label"].startswith(end):
                                    map_pos = p["position"] - data["area_origin"]
                                    x = map_pos[0]
                                    y = map_pos[1]
                                    break
                            for p in data["monsters"]:
                                if p["name"].startswith(end):
                                    map_pos = p["position"] - data["area_origin"]
                                    x = map_pos[0]
                                    y = map_pos[1]
                                    break
                    elif obj is True:
                        for p in data["objects"]:
                            if p["name"].startswith(end):
                                map_pos = p["position"] - data["area_origin"]
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

                    player_x_local = player_x - data["area_origin"][0]
                    player_y_local = player_y - data["area_origin"][1]

                    odist = math.dist([target_x, target_y],
                                      [player_x, player_y])

                    # make paths
                    if data['map'] is not None:
                        player_local = (int(player_y_local), int(player_x_local))
                        dest = (int(y), int(x))
                        # path_data = make_path_astar(player_local, dest, data["map"])
                        pf = PathFinder(self._api)
                        path_data = pf.make_path_astar(player_local, dest)
                        self._api._current_path = path_data
                        if path_data is not None:
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

                    if path_data is not None:
                        keyboard.send(
                            char._char_config["force_move"], do_release=False)

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
                    while len(target) > 0:
                        try:
                            data = self._api.get_data()
                        except:
                            pass
                        player_x = data["player_pos_world"][0]
                        player_y = data["player_pos_world"][1]

                        delta_p = math.dist(prev_p, data["player_pos_world"])

                        wp_x = target[0][0]+data["area_origin"][0]
                        wp_y = target[0][1]+data["area_origin"][1]

                        odist = math.dist([wp_x, wp_y], [player_x, player_y])

                        end_x = end_click_pt[0]+data["area_origin"][0]
                        end_y = end_click_pt[1]+data["area_origin"][1]

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

        keyboard.send(char._char_config["force_move"], do_press=False)
        return True

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
                 dest_distance=15
                 ):
        """
        Traverse to another location
        :param end: Either world coordinates as tuple [x, y] or a string e.g. 'Worldstone Keep Level 3'
        :param char
        :return: bool if successfull
        """
        print(f"Traversing to {end}...")
        # Logger.debug(f"Traverse to {end}")
        if do_pre_move:
            char.pre_move()
        # reduce casting frame duration since we can check for teleport skill used in memory
        tmp_duration = char._cast_duration
        char._cast_duration = max(0.18, char._cast_duration - 0.3)
        last_pos = None
        repeated_pos_count = 0
        reached_destination = 2
        hard_exit = 0
        start = time.time()
        while time.time() - start < time_out:
            data = self._api.get_data()
            if data is None:
                Logger.warning(f"Couldnt get api data retrying")
                continue
            if data is not None and "map" in data and data["map"] is not None:
                player_pos_area = data["player_pos_area"]
                if data["used_skill"] == "SKILL_TELEPORT":
                    Logger.debug("Used teleport")
                    time.sleep(0.18)
                    continue

                # Some fail save checking for when we get stuck
                if last_pos is not None and np.array_equal(player_pos_area, last_pos):
                    repeated_pos_count += 1
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
                map_pos = None
                if type(end) is str and obj is False:
                    for p in data["poi"]:
                        if p["label"].startswith(end):
                            map_pos = p["position"] - data["area_origin"]
                elif type(end) is str and obj is True:
                    for p in data["objects"]:
                        if p["name"].startswith(end):
                            map_pos = p["position"] - data["area_origin"]
                else:
                    map_pos = end
                if map_pos is None:
                    if hard_exit < 10:
                        data = self._api.get_data()
                        hard_exit += 1
                        # seems like the data isnt loading in time here, just try again
                        Logger.warning(
                            f"Couldnt find endpoint: {end} trying one more time...")
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
                end_pos = np.array([map_pos[1], map_pos[0]])
                weighted_map[end_pos[0]][end_pos[1]] = 1
                route = pyastar2d.astar_path(weighted_map, start_pos, end_pos, allow_diagonal=False)

                route_list = route.tolist()
                decimation = []

                jump_dist = 15
                prev_node = route_list[0]
                for node in route_list:
                    # manhattan distance from our current step to the next node
                    d = cityblock(node, prev_node)
                    if d > jump_dist:
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
                    # this is our new route node
                    node = np.array(route_list[i])
                    node_pos_w = [node[1], node[0]]
                    data = self._api.get_data()
                    player_pos = data['player_pos_area']+data['player_offset']
                    node_pos_abs = world_to_abs(node_pos_w, player_pos)
                    node_pos_m = self._screen.convert_abs_to_monitor(node_pos_abs, clip_input=True)

                    if math.dist(player_pos, node_pos_w) < 10:
                        continue
                    char.move((node_pos_m[0], node_pos_m[1]), force_move=force)
                    if i > len(route_list)-4:
                        # slow down on the last few jumps for accuracy, there might be a better way but ???
                        time.sleep(.4)
                    if kill:
                        density = self._config.char["density"]
                        area = self._config.char["area"]
                        monster = char.kill_around(
                            self._api, density, area, True)
                        if monster:
                            return monster
                        if do_pre_move:
                            char.pre_move()
                data = self._api.get_data()
                player_pos = data['player_pos_area'] + data['player_offset']
                recalc_dist = math.dist(player_pos, map_pos)
                if recalc_dist < dest_distance and verify_location:
                    Logger.debug(f"Traverse to {end} completed ({round(recalc_dist, 2)} from destination)")
                    return True
                elif verify_location is False:
                    Logger.debug(f"Traverse completed without verification ({round(recalc_dist, 2)} from destination)")
                    return True
                else:
                    Logger.warning(f"Ended too early, recalculating pathing..." + str(recalc_dist))

            time.sleep(0.02)
            self._api._astar_current_path = None
        return False

    def wait_for_location(self, name) -> bool:
        start = time.time()
        while time.time() - start < 20:
            data = self._api.get_data()
            if data is not None and data["current_area"] == name:
                return True
            time.sleep(0.2)
        return False


if __name__ == "__main__":
    import keyboard
    import os
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from bot import Bot
    from config import Config
    from game_stats import GameStats
    config = Config()
    screen = Screen(config.general["monitor"])
    game_stats = GameStats()
    bot = Bot(screen, game_stats)

    api = MapAssistApi()
    pather = Pather(screen, api)
    pather.traverse("Worldstone Keep Level 3", bot._char)
    # print(pather.wait_for_location("TheWorldStoneKeepLevel2"))