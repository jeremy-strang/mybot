import math
from .monster_type import MonsterType
from utils.misc import is_in_roi

class MonsterRule:

    def __init__(self,
                 names:         list[str] = None,
                 monster_types: list[MonsterType] = None,
                 auras:         list[str] = None,
                 boss_id:       int = None,
                 mob_number:    int = None,
                 time_out:      float = 6.0,
                 max_distance:  float = None,
                 area_tether:   tuple[float, float] = None,
                 boundary:      list[int] = None,
                ):
        self.names = names
        self.monster_types = monster_types
        self.auras = auras
        self.boss_id = boss_id
        self.mob_number = mob_number
        self.time_out = time_out
        self.max_distance = max_distance
        self.area_tether = area_tether
        self.boundary = boundary
    
    def evaluate_monster(self, monster: dict, min_score: int = 0) -> int:
        rules_met = 0
        if monster is not None and type(monster) is dict:
            m_types = monster["type"].split(", ") if type(monster["type"]) is str else []
            if self.names is not None and any(monster["name"].startswith(startstr) for startstr in self.names):
                rules_met += 1
            if self.monster_types is not None:
                for monster_type in self.monster_types:
                    if any(monster_type == mtype for mtype in m_types):
                        rules_met += 1
                        break
            # Not working corectly at the moment, only use for conviction
            if self.auras is not None:
                for aura in self.auras:
                    if any(aura in state for state in monster["state_strings"]):
                        rules_met += 1
                        break
            if self.boss_id is not None and "boss_id" in monster and self.boss_id == monster["boss_id"]:
                rules_met += 1
            if self.mob_number is not None and "mob_number" in monster and self.mob_number == monster["mob_number"]:
                rules_met += 1
            if self.max_distance is not None:
                if self.area_tether is not None:
                    if math.dist(self.area_tether, monster["position_area"]) > self.max_distance:
                        return 0
                elif monster["dist"] > self.max_distance:
                    return 0
        score = rules_met + min_score if rules_met > 0 else 0
        return score
        