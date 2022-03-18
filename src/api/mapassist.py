import traceback
import numpy as np
from mas import MAS
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
        self.data=None
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
        Logger.debug("Updated data {0} times in {1} sec ({2} per sec)".format(n, elapsed, n_per_sec))
        return (elapsed, n, n_per_sec)

    def write_data_to_file(self):
        current_area = self.data["current_area"]
        with open(f"../botty_data_{current_area}.json", "w") as f:
            f.write(json.dumps(json.loads(self._raw_data_str), indent=4, sort_keys=True))
            f.close()

    def get_data(self):
        return self.data

    def _on_data(self, data_str: str):
        try:
            data_obj = json.loads(data_str)
            self._raw_data_str = data_str
            if data_obj["success"]:
                self.data = self._mas.get_data(data_obj)
                if self.data["map"] is not None:
                    self._map = self.data["map"]
                elif self._map is not None:
                    self.data["map"] = self._map
                self._errors = 0
                self._num_updates += 1
                self._player_pos = self.data['player_pos_world']
                events.emit("data", self.data)
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
