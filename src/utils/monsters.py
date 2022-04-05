import json
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
        min_score = 100 * len(priority_rules)
        for rule in priority_rules:
            score += rule.evaluate_monster(monster, min_score)
            min_score -= 100
            if score > 0: break
    monster["score"] = score
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
        if boundary and not is_in_roi(boundary, m["position"] - data["area_origin"]):
            return False
        if rules and len(rules) > 0 and score_monster(m, rules) <= min_score:
            return False
        if ignore and len(ignore) > 0 and score_monster(m, ignore) > 0:
            return False
        return True

    if data is not None:
        monsters = list(filter(_filter_check, data["monsters"]))
        if rules and len(rules) > 0:
            monsters.sort(key=lambda m: score_monster(m, rules))
    return monsters

def find_monster(id: int, api: MapAssistApi) -> dict:
    data = api.get_data()
    if data is not None and "monsters" in data and type(data["monsters"]) is list:
        for m in data["monsters"]:
            if m["id"] == id:
                return m
    return None

def find_npc(npc: Npc, api: MapAssistApi):
    data = api.get_data()
    for m in data["monsters"]:
        name = m["name"]
        if name.lower() == npc.lower():
            return m
    return None

def find_poi(poi: str, api: MapAssistApi):
    data = api.get_data()
    for p in data["points_of_interest"]:
        label = p["label"]
        if label.lower().startswith(poi.lower()):
            return p
    return None

def find_object(name: str, api: MapAssistApi):
    data = api.get_data()
    for obj in data["object"]:
        if obj["name"].lower().startswith(name.lower()):
            return obj
    return None

def find_item(id: int, api: MapAssistApi) -> dict:
    data = api.get_data()
    if data is not None and "items" in data and type(data["items"]) is list:
        for item in data["items"]:
            if item["id"] == id:
                return item
    return None

def find_object(object: str, api: MapAssistApi):
    data = api.get_data()
    for o in data["objects"]:
        name = o["name"]
        if name.lower().startswith(object.lower()):
            return o
    return None

def get_unlooted_monsters(api: MapAssistApi, rules: list[MonsterRule], looted_monsters: set, boundary=None, max_distance=100) -> list[dict]:
    data = api.get_data()
    if data is not None and "monsters" in data:
        monsters = sort_and_filter_monsters(data, rules, None, boundary)
        return list(filter(lambda m: m["mode"] == 12 and m["id"] not in looted_monsters and m["dist"] < max_distance, monsters))
    return []
