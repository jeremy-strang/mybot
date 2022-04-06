import json

from numpy import str0
from api import MapAssistApi
from npc_manager import Npc
from monsters import MonsterType, MonsterRule
from utils.misc import is_in_roi
    
CHAMPS_UNIQUES = [
    MonsterRule(monster_types = [MonsterType.SUPER_UNIQUE]),
    MonsterRule(monster_types = [MonsterType.UNIQUE]),
    MonsterRule(monster_types = [MonsterType.CHAMPION, MonsterType.GHOSTLY, MonsterType.POSSESSED]),
]

def score_monster(monster: dict, priority_rules: list[MonsterRule]):
    score = 0
    if monster is not None and type(monster) is dict and type(priority_rules) is list:
        min_score = 100 * (len(priority_rules) - 1)
        for rule in priority_rules:
            score += rule.evaluate_monster(monster, min_score)
            min_score -= 100
            if score > 0: break
    return score

def sort_and_filter_monsters(data,
                             rules: list[MonsterRule],
                             ignore: list[MonsterRule] = None,
                             boundary = None,
                             min_score = 0,
                             ignore_dead = False
                            ):
    monsters = []
    def _filter_check(m):
        if ignore_dead and m["mode"] == 12:
            return False
        if boundary is not None and not is_in_roi(boundary, m["position"] - data["area_origin"]):
            return False
        if rules is not None and len(rules) > 0 and score_monster(m, rules) <= min_score:
            return False
        if ignore is not None and len(ignore) > 0 and score_monster(m, ignore) > 0:
            return False
        return True

    if data is not None:
        m0 = len(data["monsters"])
        monsters = list(filter(_filter_check, data["monsters"]))
        if rules and len(rules) > 0:
            monsters.sort(key=lambda m: score_monster(m, rules), reverse=True)
        print(f"    Filtered monsters from {m0} to {len(monsters)}")
    return monsters

def get_unlooted_monsters(api: MapAssistApi, rules: list[MonsterRule], looted_monsters: set, boundary=None, max_distance=100) -> list[dict]:
    data = api.data
    if data and "monsters" in data:
        monsters = sort_and_filter_monsters(data, rules, None, boundary)
        return list(filter(lambda m: m["mode"] == 12 and m["id"] not in looted_monsters and m["dist"] < max_distance, monsters))
    return []
