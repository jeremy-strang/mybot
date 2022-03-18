from api import MapAssistApi
from npc_manager import Npc
from state_monitor import MonsterType, MonsterPriorityRule, sort_and_filter_monsters
    
CHAMPS_UNIQUES = [
    MonsterPriorityRule(monster_types = [MonsterType.SUPER_UNIQUE]),
    MonsterPriorityRule(monster_types = [MonsterType.UNIQUE]),
    MonsterPriorityRule(monster_types = [MonsterType.CHAMPION, MonsterType.GHOSTLY, MonsterType.POSSESSED]),
]

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

def get_unlooted_monsters(api: MapAssistApi, rules: list[MonsterPriorityRule], looted_monsters: set, boundary=None, max_distance=100) -> list[dict]:
    data = api.get_data()
    if data is not None and "monsters" in data:
        monsters = sort_and_filter_monsters(data, rules, boundary)
        return list(filter(lambda m: m["mode"] == 12 and m["id"] not in looted_monsters and m["dist"] < max_distance, monsters))
    return []







