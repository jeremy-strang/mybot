import traceback
import os
import numpy as np
from .mas import MAS
import math
import time
import threading
import json
import time
from logger import Logger
from event import events

def sleep(duration, get_now=time.perf_counter):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()

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
