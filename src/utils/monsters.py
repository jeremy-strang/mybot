from api import MapAssistApi
from npc_manager import Npc
    
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
