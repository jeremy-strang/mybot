import cv2
from mas import world_to_abs
import numpy as np
from copy import deepcopy
import math
import time
from typing import Union
import random
from api import MapAssistApi
from config import Config
from logger import Logger
import threading
from utils.misc import is_in_roi, kill_thread
import time

class MonsterType:
    NONE = "None"
    SUPER_UNIQUE = "SuperUnique"
    UNIQUE = "Unique"
    CHAMPION = "Champion"
    POSSESSED = "Possessed"
    GHOSTLY = "Ghostly"
    MINION = "Minion"
    OTHER = "Other"

class MonsterPriorityRule:
    names: list[str] = None
    monster_types: list[str] = None
    auras: list[str] = None
    boss_id: int = None

    def __init__(self, names = None, monster_types = None, auras = None):
        self.names = names
        self.monster_types = monster_types
        self.auras = auras
    
    def evaluate_rules(self, monster: dict, min_score: int = 0) -> int:
        rules_met = 0
        if monster is not None and type(monster) is dict:
            m_types = monster["type"].split(", ") if type(monster["type"]) is str else []
            if self.names is not None and any(monster["name"].startswith(startstr) for startstr in self.names):
                rules_met += 1
            if self.monster_types is not None:
                for monster_type in self.monster_types:
                    if any(monster_type == mtype for mtype in m_types):
                        rules_met += 1
            if self.auras is not None:
                for aura in self.auras:
                    if any(aura in state for state in monster["state_strings"]):
                        rules_met += 1
            if self.boss_id is not None and "boss_id" in monster and self.boss_id == monster["boss_id"]:
                rules_met += 1
        score = rules_met + min_score if rules_met > 0 else 0
        return score

def sort_and_filter_monsters(data, rules, boundary=None, min_score=0):
    monsters = []
    if data is not None:
        monsters = data["monsters"]
        if boundary is not None:
            monsters = list(filter(lambda m: is_in_roi(boundary, m["position"] - data["area_origin"]), monsters))
        if len(rules) > 0:
            monsters.sort(key=lambda m: monster_score(m, rules))
            monsters = list(filter(lambda m: m["score"] > min_score, monsters))
    return monsters
    
def monster_score(monster: dict, priority_rules: list[MonsterPriorityRule]):
    score = 0
    if monster is not None and type(monster) is dict and type(priority_rules) is list:
        min_score = 100 * len(priority_rules)
        for rule in priority_rules:
            score += rule.evaluate_rules(monster, min_score)
            min_score -= 100
            if score > 0: break
    monster["score"] = score
    return score

class StateMonitor:
    def __init__(self, names: list, api: MapAssistApi, super_unique: bool = False, unique_id: int=-1, many=False, do_corpses=False, boundary=None):
        self._loop_delay = .08
        self._game_thread = None
        self._game=None
        self._data=None
        self._dead = 0
        self._status = 'unk'
        self._target = None
        self._target_pos = None
        self._area_pos = None
        self._names = names
        self._rules = list(MonsterPriorityRule([rule]) if type(rule) is str else rule for rule in names)
        self._ready = False
        self._super_unique=super_unique
        self._player_x=None
        self._player_y=None
        self._dist = 9999
        self._api = api
        self._unique_id = unique_id
        self._many = many
        self._do_corpses = do_corpses
        self._boundary = boundary
        #print(self._names)
        self.start()

    def start(self):
        Logger.debug("Start game monitoring thread...")
        self._game = ApiThread(self)
        self._game_thread = threading.Thread(target=self._game.get_data)
        #self._game_thread.daemon = False
        self._game_thread.start()

    def stop(self):
        Logger.debug("Game monitoring thread shutdown...")
        if self._game_thread: kill_thread(self._game_thread)
        #self._game_thread.join()
        Logger.debug("Game monitoring thread shutdown...")

class ApiThread:
    def __init__(self, state: StateMonitor):
        self._api = state._api
        self._sm = state
        Logger.debug("Opened API thread...")

    def _update_status(self):
        '''
            gets status of current target position
        '''
        data = self._sm._api.get_data()
        if data is not None:
            monsters = sort_and_filter_monsters(data, self._sm._rules, self._sm._boundary)
            # print(f"State monitor targeting {len(monsters)} monsters")
            for m in monsters:
                proceed = True
                correct_id = False
                if self._sm._super_unique:
                    if 'Unique' in m['type']:
                        proceed = monster_score(l, self._sm._rules) > 0 if len(self._sm._rules > 0) else True

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
                            for l in sort_and_filter_monsters(data, self._sm._rules, self._sm._boundary):
                                # If we are targeting corpses, make sure it's dead, otherwise make sure it's alive
                                is_correct_mode = (self._sm._do_corpses and l["is_targetable_corpse"]) or (not self._sm._do_corpses and l["mode"] != 12)
                                if monster_score(l, self._sm._rules) > 0 and is_correct_mode:
                                    more += 1

                            if more < 0:
                                self._sm._dead = 1
                                self._sm._status = "Monsters are dead"
                                Logger.debug(self._sm._status)
                            else:
                                self._sm._unique_id = -1
                    self._sm._ready = True

    def get_data(self):
        #print("get api data")
        start = time.time()
        time_out = 9000
        while time.time() - start < time_out:
            self._sm._data = self._api.get_data()
            self._update_status()
            time.sleep(.01)
            #print("updating...")