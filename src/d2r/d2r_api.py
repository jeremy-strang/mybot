from lib2to3.pytree import Base
import pickle
from tkinter import N
import traceback
import os
from typing import Union
import numpy as np
from d2r.d2r import D2rArea, TOWNS
from utils.misc import normalize_text

from npc_manager import Npc
from .d2r_loader import D2rLoader
import math
import time
import threading
import json
import time
from logger import Logger
from event import events

class D2rApi:
    def __init__(self, custom_files=[]):
        self.data = None
        self.should_chicken = False
        self.in_game = False
        self.in_town = False
        self.player_health = 0
        self.player_max_health = 0
        self.player_mana = 0
        self.player_max_mana = 0
        self.player_health_pct = 0
        self.player_mana_pct = 0
        self.player_summary = None
        self.player_name = None
        self.player_experience = 0
        self.player_level_progress = 0
        self.merc_alive = False
        self.merc_health_pct = 0
        self.current_area = None
        self.player_stats_dict = {}
        # self.player_velocity = None

        self._current_path = []
        self._astar_current_path = []
        self._player_pos = None
        self._num_updates = 0
        self._initial_time = 0
        self._errors = 0
        self._raw_data_str = "{}"
        self._custom_files = custom_files
        self._map = None
        self._loader = None
        self._last_print = time.time()
        self._num_prints = 0
        self._last_err = ""
        self._last_success = time.time()

    def start_timer(self):
        self._num_updates = 0
        self._initial_time = time.time()

    def get_metrics(self):
        elapsed = time.time() - self._initial_time
        n = self._num_updates
        n_per_sec = n / float(elapsed) if elapsed != 0 else 0
        Logger.debug(f"Updated data {n} times in {round(elapsed, 2)} sec ({round(n_per_sec, 2)} per sec)")
        return (elapsed, n, n_per_sec)

    def write_data_to_file(self, file_path=None, pickle: bool = False, file_prefix: str = "") -> str:
        if pickle:
            return self.write_data_to_pickle(file_path)
        else:
            try:
                if file_path is None:
                    current_area = self.data["current_area"]
                    file_path = f"./stats/{file_prefix if file_prefix is not None else 'mybot_data'}_{current_area}_{time.strftime('%Y%m%d_%H%M%S')}.json"
                with open(file_path, "w") as f:
                    f.write(json.dumps(json.loads(self._raw_data_str), indent=4, sort_keys=True))
                    f.close()
                Logger.info(f"Saved D2R memory snapshot to {os.path.normpath(file_path)}")
                return file_path
            except BaseException as e:
                Logger.error(f"Error dumping JSON data: {e}")
        return None

    def write_data_to_pickle(self, file_path=None, file_prefix: str = "") -> str:
        try:
            if file_path is None:
                current_area = self.data["current_area"]
                file_path = f"./pickles/{file_prefix if file_prefix is not None else 'mybot_data'}_{current_area}_{time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(file_path, "wb") as f:
                pickle.dump(self.data, f)
                f.close()
            Logger.info(f"Pickled D2R memory snapshot to {os.path.normpath(file_path)}")
            return file_path
        except BaseException as e:
            Logger.error(f"Error pickling data: {e}")
        return None

    def get_data(self):
        return self.data

    def _on_data(self, data_str: str):
        last_spot = 0
        try:
            data_obj = json.loads(data_str)
            if data_obj["success"]:
                last_spot = 1
                self._raw_data_str = data_str
                data = self._loader.load_data(data_obj)
                last_spot = 2
                if data["map"] is not None:
                    self._map = data["map"]
                    last_spot = 3
                elif self._map is not None:
                    data["map"] = self._map
                    last_spot = 4
                self._errors = 0
                self._num_updates += 1
                self._player_pos = data["player_pos_world"]
                last_spot = 5
                
                self.in_game = data["in_game"]
                self.in_town = data["in_town"] == True
                last_spot = 6
                self.player_health = data["player_health"]
                self.player_max_health = data["player_max_health"]
                self.player_mana = data["player_mana"]
                self.player_max_mana = data["player_max_mana"]
                last_spot = 7
                self.player_health_pct = data["player_health_pct"]
                self.player_mana_pct = data["player_mana_pct"]
                last_spot = 8
                self.merc_alive = data["merc_alive"]
                self.merc_health_pct = data["merc_health_pct"]
                self.should_chicken = data["should_chicken"]
                last_spot = 9

                pstats = {}
                if data["player_stats"] is not None:
                    for kv in data["player_stats"]:
                        pstats[kv["key"]] = kv["value"]
                self.player_stats_dict = pstats

                # if "VelocityPercent" in self.player_stats_dict:
                #     velocity = self.player_stats_dict["VelocityPercent"]
                #     if velocity != self.player_velocity:
                #         Logger.debug(f"\nPlayer velocity changed from {self.player_velocity} to {velocity}")
                #     self.player_velocity = velocity

                if data["current_area"] != self.current_area:
                    last_spot = 10
                    Logger.info(f"Location changed from {self.current_area} to {data['current_area']} (map height: {data['map_height']}, map width: {data['map_width']})")
                self.current_area = data["current_area"]
                
                last_spot = 11
                self.data = data
                events.emit("data", data)
                self._errors = 0

                last_spot = 12
                if self._loader.player_summary is not None:
                    self.player_summary = self._loader.player_summary
                    self.player_name = self._loader.player_name
                self.player_experience = self._loader.player_experience
                self.player_level_progress = self._loader.player_level_progress
                self.player_level = self._loader.player_level
                last_spot = 13
                
                self._last_success = time.time()
                # We only want to change should_chicken if it goes from False to True, once it's triggered we will just leave
            else:
                last_spot = 14
                self._errors += 1
                delta_t = time.time() - self._last_print
                err = data_obj['error']
                last_spot = 15
                if err and len(err) > 0 and (delta_t >= 5 or (self._num_prints < 3 and err != self._last_err)):
                    self._last_print = time.time()
                    self._num_prints += 1
                    self._last_err = err
                    Logger.error(f"\n.NET Exception:\n    Err: '{err}'")
                    Logger.error(f"\n    Stack Trace:\n{data_obj['error_trace']}")
                    self._num_prints = 0
        except BaseException as e:
            traceback.print_exc()
            self._errors += 1
            delta_t = time.time() - self._last_print
            err = str(e)
            last_spot = 16
            if err and len(err) > 0 and (delta_t >= 5 or (self._num_prints < 3 and err != self._last_err)):
                self._last_print = time.time()
                self._num_prints += 1
                self._last_err = err
                Logger.error(f"\nPython Exception:\n    Err: '{err}'")
                Logger.error(f"\n    Stack Trace:")
                traceback.print_exc()
        
        # If we haven't successfully loaded data in 30 minutes, try to restart the API
        if self._errors > 1000 and time.time() - self._last_success >= 1800:
            Logger.error(f"Errors reached {self._errors}, will attempt restart Map Assist API, last spot: {last_spot}")
            #try and restart 
            self._errors = 0
            self.stop()
            self.start()
    
    def start(self):
        Logger.info("Starting Map Assist API")
        self._loader = D2rLoader(self._on_data, self._custom_files)
        self._loader.start()

    def stop(self):
        Logger.info("Stopping Map Assist API")
        self.data = None
        self.should_chicken = False
        self.in_game = False
        self.player_health = 0
        self.player_max_health = 0
        self.player_mana = 0
        self.player_max_mana = 0
        self.player_health_pct = 0
        self.player_mana_pct = 0
        self.player_summary = None
        self.player_name = None
        self.merc_alive = False
        self.merc_health_pct = 0
        self.current_area = None

        self._current_path = []
        self._astar_current_path = []
        self._player_pos = None
        self._num_updates = 0
        self._initial_time = 0
        self._errors = 0
        self._raw_data_str = "{}"
        self._map = None
        self._loader.cancel()
        self._loader = None
    
    def confirm_boss_death(self, name: str, exact=False):
        corpse = self.find_monster_by_name(name, exact)
        if corpse:
            if corpse["mode"] == 12:
                Logger.info(f"Confirmed that {name} is dead")
                return True
            else:
                Logger.info(f"Ended combat with {name} still alive")
                return False
        Logger.warning(f"Ended combat, but {name}'s corpse was not found")

    def find_monster(self, id: int) -> dict:
        data = self.data
        if data and "monsters" in data and type(data["monsters"]) is list:
            for m in data["monsters"]:
                if m["id"] == id:
                    return m
        return None

    def find_monster_by_name(self, name: str, exact=False) -> dict:
        data = self.data
        if data and "monsters" in data and type(data["monsters"]) is list:
            if name and not exact:
                name = normalize_text(name)
            for m in data["monsters"]:
                m_name = normalize_text(m["name"]) if not exact else m["name"]
                if not exact and name in m_name:
                    return m
                elif m_name == name:
                    return m
        return None

    def find_monsters_by_type(self, monster_type: str) -> dict:
        results = []
        data = self.data
        if data and "monsters" in data and type(data["monsters"]) is list:
            for m in data["monsters"]:
                if monster_type in m["type"]:
                    results.append(m)
        return results

    def find_npc(self, npc: Npc):
        npc_str = normalize_text(npc)
        if self.data:
            for m in self.data["monsters"]:
                name = normalize_text(m["name"])
                if npc_str in name:
                    return m
            for m in self.data["static_npcs"]:
                name = normalize_text(m["name"])
                if npc_str in name:
                    return m
        return None

    def find_poi(self, poi_label: str):
        poi_str = normalize_text(poi_label)
        if self.data:
            for p in self.data["points_of_interest"]:
                label = normalize_text(p["label"])
                if poi_str in label:
                    return p
        return None

    def find_object(self, obj_name: str):
        name_str = normalize_text(obj_name)
        if self.data:
            for obj in self.data["object"]:
                if name_str in normalize_text(obj["name"]):
                    return obj
        return None

    def find_item(self, id: int, list_name: str = "items") -> dict:
        if self.data and list_name in self.data and type(self.data[list_name]) is list:
            for item in self.data[list_name]:
                if item["id"] == id:
                    return item
        return None

    def find_items_by_name(self, name: str, list_name: str = "inventory_items", exact: bool = False) -> dict:
        results = None
        if self.data and list_name in self.data and type(self.data[list_name]) is list:
            results = []
            for item in self.data[list_name]:
                if (exact and item["name"] == name) or (not exact and normalize_text(name) == normalize_text(item["name"])):
                    results.append(item)
        return results
    
    def find_items_by_roi(self, roi, list_name: str = "inventory_items") -> list:
        results = None
        if self.data and list_name in self.data and type(self.data[list_name]) is list:
            results = []
            for item in self.data[list_name]:
                x = item["position"][0]
                y = item["position"][1]
                if x >= roi[0] and x < roi[2] and y >= roi[1] and y < roi[3]:
                    results.append(item)
        return results
    
    def find_looted_items(self, num_loot_columns: int):
        return self.find_items_by_roi([0, 0, num_loot_columns, 4])

    def find_items_by_position(self, pos: tuple[int, int], list_name: str = "inventory_items", max_x: int = 10, max_y = 4) -> list:
        results = []
        if self.data and list_name in self.data and type(self.data[list_name]) is list:
            for i, item in enumerate(self.data[list_name]):
                item_x = item["position"][0]
                item_y = item["position"][1]
                if item_x == pos[0] and item_y == pos[1] and item_x < max_x and item_y < max_y:
                    results.append(item)
        return results

    def find_object(self, obj_name: str, exact: bool = False):
        obj_name = obj_name if exact else normalize_text(obj_name)
        if self.data:
            for o in self.data["objects"]:
                name = o["name"] if exact else normalize_text(o["name"])
                if obj_name in name:
                    return o
        return None
    
    def get_hovered_unit(self):
        if self.data:
            hovered_unit = self.data["hovered_unit"]
            hovered_unit_type = self.data["hovered_unit_type"]
            return (hovered_unit, hovered_unit_type)
        return (None, None)

    def wait_for_menu(self, menu: str, time_out=1) -> bool:
        key = f"{menu}_open"
        start = time.time()
        is_open = lambda data: data != None and key in data and data[key]
        while not (is_open(self.data)) and time.time() - start < time_out:
            time.sleep(0.1)
        return is_open(self.data)

    def wait_for_monster(self, name: str, time_out=1.0, exact: bool=False):
        start = time.time()
        monster = self.find_monster_by_name(name, exact=exact)
        while monster is None and time.time() - start < time_out:
            time.sleep(0.1)
            monster = self.find_monster_by_name(name, exact=exact)
        return monster

    def wait_for_object(self, name: str, time_out=1.0, exact: bool=False):
        start = time.time()
        object = self.find_object(name, exact=exact)
        while object is None and time.time() - start < time_out:
            time.sleep(0.1)
            object = self.find_object(name, exact=exact)
        return object

    def wait_for_poi(self, poi: str, time_out=1.0):
        start = time.time()
        poi = self.find_poi(poi)
        while poi is None and time.time() - start < time_out:
            time.sleep(0.1)
            poi = self.find_poi(poi)
        return poi

    def wait_for_area(self, area: str, time_out=5.0):
        start = time.time()
        area = normalize_text(area)
        area_detected = self.data is not None and area in normalize_text(self.data["current_area"])
        while not area_detected and time.time() - start < time_out:
            time.sleep(0.1)
            area_detected = self.data is not None and area in normalize_text(self.data["current_area"])
        return area_detected

    def wait_for_town(self, time_out=10.0):
        start = time.time()
        area_detected = self.data is not None and self.data["current_area"] in TOWNS
        while not area_detected and time.time() - start < time_out:
            time.sleep(0.1)
            area_detected = self.data is not None and self.data["current_area"] in TOWNS
        return area_detected

    def wait_for_hover(self, target: dict, list_name: str, time_out=0.33) -> bool:
        result = (False, None, None)
        updated = target
        if target:
            start = time.time()
            
            while updated and not updated["is_hovered"] and time.time() - start < time_out:
                time.sleep(0.1)
                hovered_unit, hovered_unit_type = self.get_hovered_unit()
                if hovered_unit and hovered_unit["id"] != target["id"]:
                    Logger.debug(f"Wrong unit is hovered, hovered unit: {hovered_unit['id']}, type: {hovered_unit_type}")
                    result = (False, hovered_unit, hovered_unit_type)
                if list_name == "objects":
                    updated = self.find_object(target["name"])
                elif list_name == "points_of_interest":
                    updated = self.find_poi(target["label"])
                elif list_name == "monsters":
                    updated = self.find_monster(target["name"])
                elif "_items" in list_name:
                    updated = self.find_item(target["id"], list_name)
        if updated and updated["is_hovered"]:
            result = (True, updated, list_name)
        return result

    def wait_for_item_stats(self, item: dict, time_out: float = 4.0, list_name = None) -> bool:
        start = time.time()
        stats_loaded = False
        if item:
            stats_loaded = "stats" in item and item["stats"] != None and len(item["stats"]) > 0
            item_id = item["id"]
            while not stats_loaded and time.time() - start < time_out:
                time.sleep(0.1)
                if list_name != None:
                    item = self.find_item(item_id, list_name)
                else:
                    item = self.find_item(item_id, "inventory_items")
                    if not item:
                        item = self.find_item(item_id, "stash_items")
                    if not item:
                        item = self.find_item(item_id, "equipped_items")
                    if not item:
                        item = self.find_item(item_id, "items")
                stats_loaded = item and "stats" in item and item["stats"] != None and len(item["stats"]) > 0
            Logger.debug(f"Waited {round(time.time() - start, 2)}sec to load {len(item['stats']) if stats_loaded else 0} stats from {str(item['quality'])} {item['name']} with id {item_id}")
        else:
            Logger.warning("Failed to wait for item stats to load, the given item was None")
        return item if stats_loaded else False

    def get_player_stat(self, stat_key: str):
        if self.player_stats_dict and stat_key in self.player_stats_dict:
            return self.player_stats_dict[stat_key]
        return None

    def wait_for_data(self, time_out: float = 4.0):
        start = time.time()
        data = self.data
        while not data and time.time() - start < time_out:
            time.sleep(0.1)
            data = self.data
        return data
    
