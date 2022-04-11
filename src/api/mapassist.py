import traceback
import os
import numpy as np

from npc_manager import Npc

from .mas import MAS
import math
import time
import threading
import json
import time
from logger import Logger
from event import events

class MapAssistApi:
    def __init__(self, custom_files=[]):
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
        self._custom_files = custom_files
        self._map = None
        self._mas = None

    def start_timer(self):
        self._num_updates = 0
        self._initial_time = time.time()

    def get_metrics(self):
        elapsed = time.time() - self._initial_time
        n = self._num_updates
        n_per_sec = n / float(elapsed) if elapsed != 0 else 0
        Logger.debug(f"Updated data {n} times in {round(elapsed, 2)} sec ({round(n_per_sec, 2)} per sec)")
        return (elapsed, n, n_per_sec)

    def write_data_to_file(self, file_path=None):
        if file_path is None:
            current_area = self.data["current_area"]
            file_path = f"./stats/mybot_data_{current_area}_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(file_path, "w") as f:
            f.write(json.dumps(json.loads(self._raw_data_str), indent=4, sort_keys=True))
            f.close()
        Logger.info(f"Saved D2R memory snapshot to {os.path.normpath(file_path)}")

    def get_data(self):
        return self.data

    def _on_data(self, data_str: str):
        try:
            data_obj = json.loads(data_str)
            self._raw_data_str = data_str
            if data_obj["success"]:
                data = self._mas.get_data(data_obj)
                if data["map"] is not None:
                    self._map = data["map"]
                elif self._map is not None:
                    data["map"] = self._map
                self._errors = 0
                self._num_updates += 1
                self._player_pos = data["player_pos_world"]
                
                self.in_game = data["in_game"]
                self.player_health = data["player_health"]
                self.player_max_health = data["player_max_health"]
                self.player_mana = data["player_mana"]
                self.player_max_mana = data["player_max_mana"]
                self.player_health_pct = data["player_health_pct"]
                self.player_mana_pct = data["player_mana_pct"]
                self.merc_alive = data["merc_alive"]
                self.merc_health_pct = data["merc_health_pct"]
                self.should_chicken = data["should_chicken"]

                if data["current_area"] != self.current_area:
                    Logger.info(f"Location changed from {self.current_area} to {data['current_area']} (map height: {data['map_height']}, map width: {data['map_width']})")
                self.current_area = data["current_area"]

                if self._mas.player_summary is not None:
                    self.player_summary = self._mas.player_summary
                    self.player_name = self._mas.player_name

                # We only want to change should_chicken if it goes from False to True, once it's triggered we will just leave

                self.data = data
                events.emit("data", data)
            else:
                self._errors += 1                
        except BaseException as e:
            traceback.print_exc()
            self._errors += 1
        if self._errors > 270:
            #try and restart 
            self._errors = 0
            self.stop()
            self.start()
    
    def start(self):
        Logger.info("Starting MAS api")
        self._mas = MAS(self._on_data, self._custom_files)
        self._mas.start()

    def stop(self):
        Logger.info("Stopping MAS api")
        self._mas.cancel()
    
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
                name = name.lower().replace(" ", "")
            for m in data["monsters"]:
                m_name = m["name"].lower().replace(" ", "") if m["name"] and not exact else m["name"]
                if m_name == name:
                    return m
        return None

    def find_npc(self, npc: Npc):
        if self.data:
            for m in self.data["monsters"]:
                name = m["name"]
                if name.lower() == npc.lower().replace(" ", ""):
                    return m
        return None

    def find_poi(self, poi: str):
        if self.data:
            for p in self.data["points_of_interest"]:
                label = p["label"]
                if label.lower().startswith(poi.lower()):
                    return p
        return None

    def find_object(self, name: str):
        if self.data:
            for obj in self.data["object"]:
                if obj["name"].lower().startswith(name.lower()):
                    return obj
        return None

    def find_item(self, id: int, list_name: str = "items") -> dict:
        if self.data and list_name in self.data and type(self.data[list_name]) is list:
            for item in self.data[list_name]:
                if item["id"] == id:
                    return item
        return None

    def find_items_by_name(self, name: str, list_name: str = "inventory_items") -> dict:
        results = None
        if self.data and list_name in self.data and type(self.data[list_name]) is list:
            results = []
            for item in self.data[list_name]:
                if item["name"] == name:
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

    def find_object(self, object: str):
        if self.data:
            for o in self.data["objects"]:
                name = o["name"]
                if name.lower().startswith(object.lower()):
                    return o
        return None
    
    def wait_for_menu(self, menu: str, time_out=3.0):
        key = f"{menu}_open"
        start = time.time()
        is_open = lambda data: data != None and key in data and data[key]
        while not (is_open(self.data)) and time.time() - start < time_out:
            time.sleep(0.1)
        return is_open(self.data)

    def wait_for_hover(self, target: dict, list_name: str, time_out=0.3):
        while target and not target["is_hovered"]:
            time.sleep(0.1)
            if list_name == "objects":
                target = self.find_object(target["name"])
            elif list_name == "points_of_interest":
                target = self.find_poi(target["label"])
            elif list_name == "monsters":
                target = self.find_monster(target["name"])
            elif "_items" in list_name:
                target = self.find_item(target["id"], list_name)
        return target and target["is_hovered"]

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
