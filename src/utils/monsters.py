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

def sort_and_filter_monsters(data, rules, boundary=None, min_score=0):
    monsters = []
    if data is not None:
        monsters = data["monsters"]
        if boundary is not None:
            monsters = list(filter(lambda m: is_in_roi(boundary, m["position"] - data["area_origin"]), monsters))
        if len(rules) > 0:
            monsters.sort(key=lambda m: score_monster(m, rules))
            monsters = list(filter(lambda m: m["score"] > min_score, monsters))
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
    for poi in data["points_of_interest"]:
        label = poi["label"]
        if label.lower().startswith(poi.lower()):
            return poi
    return None

def find_object(object: str, api: MapAssistApi):
    data = api.get_data()
    for object in data["objects"]:
        name = object["name"]
        if name.lower().startswith(object.lower()):
            return object
    return None

def get_unlooted_monsters(api: MapAssistApi, rules: list[MonsterRule], looted_monsters: set, boundary=None, max_distance=100) -> list[dict]:
    data = api.get_data()
    if data is not None and "monsters" in data:
        monsters = sort_and_filter_monsters(data, rules, boundary)
        return list(filter(lambda m: m["mode"] == 12 and m["id"] not in looted_monsters and m["dist"] < max_distance, monsters))
    return []







