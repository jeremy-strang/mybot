import cv2
from monsters import MonsterRule
from utils.coordinates import world_to_abs
import numpy as np
from copy import deepcopy
import math
from typing import Union
import random
from d2r import D2rApi, D2rMenu
from config import Config
from logger import Logger
import threading
from utils.misc import is_in_roi, kill_thread
from monsters import sort_and_filter_monsters, score_monster
import time
import pprint
pp = pprint.PrettyPrinter(depth=6)

class StateMonitor:
    def __init__(self,
                 names: list,
                 api: D2rApi,
                 super_unique: bool = False,
                 unique_id: int=-1,
                 many=False,
                 do_corpses=False,
                 boundary=None,
                 time_out=60.0
                ):
        self._loop_delay = .08
        self._tracker_thread = None
        self._tracker=None
        self._data=None
        self._dead = 0
        self._status = 'unk'
        self._target = None
        self._targets = []
        self._target_pos = None
        self._area_pos = None
        self._names = names
        self._rules = list(MonsterRule([rule]) if type(rule) is str else rule for rule in names)
        self._ready = False
        self._super_unique = super_unique
        self._player_x = None
        self._player_y = None
        self._dist = 9999
        self._api = api
        self._unique_id = unique_id
        self._many = many
        self._do_corpses = do_corpses
        self._boundary = boundary
        self._time_out = time_out
        self.start()

    def start(self):
        self._started = time.time()
        self._tracker = CombatTracker(self)
        self._tracker_thread = threading.Thread(target=self._tracker.run)
        self._tracker_thread.start()

    def stop(self):
        if self._tracker_thread:
            kill_thread(self._tracker_thread)
            self._tracker_thread = None

class CombatTracker:
    def __init__(self, state: StateMonitor):
        self._api = state._api
        self._sm = state

    def run(self):
        start = time.time()
        time_out = 9000
        while time.time() - start < time_out:
            self._sm._data = self._api.data
            self._update_status()
            time.sleep(.02)

    def _update_status(self):
        if time.time() - self._sm._started > self._sm._time_out:
            Logger.warning("State monitor was not stopped before time out, stopping it")
            self._sm.stop()
            return

        data = self._sm._api.data
        if data is not None:
            monsters = sort_and_filter_monsters(data, self._sm._rules, boundary=self._sm._boundary)
            self._sm._targets = list(filter(lambda x: x["mode"] != 12, monsters))
            if len(monsters) == 0: self._sm._dead = 1
            # print(f"State monitor targeting {len(monsters)} monsters")
            for m in monsters:
                proceed = True
                correct_id = False
                if self._sm._super_unique:
                    if 'Unique' in m['type']:
                        proceed = score_monster(m, self._sm._rules) > 0 if len(self._sm._rules) > 0 else True

                if self._sm._do_corpses and not m["is_targetable_corpse"]:
                    proceed = False

                #check if it has a valid id and the name is correct
                if self._sm._unique_id == -1 and proceed:
                    #assign id to target
                    self._sm._unique_id = m['id']

                if m["id"] == self._sm._unique_id:
                    correct_id=True

                if correct_id:
                    self._sm._target = m
                    area_pos = m["position"] - data["area_origin"]
                    self._sm._area_pos = area_pos
                    player_pos = data["player_pos_area"]
                    player_x =player_pos[0]
                    player_y =player_pos[1]
                    self._sm._player_x=player_x
                    self._sm._player_y=player_y

                    #update target monster position
                    target_pos = world_to_abs(m["position"], data["player_pos_world"])

                    self._sm._target_pos = target_pos
                    self._sm._dist = math.dist(player_pos, area_pos)
                    m["dist"] = self._sm._dist
                    
                    if m['mode'] == 12 and self._sm._dead == 0 and 'unk' in self._sm._status and not self._sm._do_corpses:
                        # check for any more...
                        #time.sleep(.25)
                        if self._sm._many is False:
                            self._sm._dead = 1
                            self._sm._status = "Monsters are dead"
                            Logger.debug(self._sm._status)

                        else:
                            data = self._sm._api.get_data()
                            more = -1
                            for l in sort_and_filter_monsters(data, self._sm._rules, boundary=self._sm._boundary):
                                # If we are targeting corpses, make sure it's dead, otherwise make sure it's alive
                                is_correct_mode = (self._sm._do_corpses and l["is_targetable_corpse"]) or (not self._sm._do_corpses and l["mode"] != 12)
                                if score_monster(l, self._sm._rules) > 0 and is_correct_mode:
                                    more += 1

                            if more < 0:
                                self._sm._dead = 1
                                self._sm._status = "Monsters are dead"
                                Logger.debug(self._sm._status)
                            else:
                                self._sm._unique_id = -1
                    self._sm._ready = True

