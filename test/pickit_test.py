import json, pprint, sys, os

sys.path.insert(0, "./config")
sys.path.insert(0, "./src")
dir_path = os.path.dirname(os.path.realpath(__file__))

from game_stats import GameStats
from logger import Logger
from pickit.pickit_utils import get_pickit_action
from pickit_config import pickit_config, PickitConfig
from pickit.types import *


pp = pprint.PrettyPrinter(indent=4)


def load_json(path: str):
    data = None
    with open(path) as f:
        data_json = f.read()
        data = json.loads(data_json)
        f.close()
    return data

def pickit_test():
    game_stats = GameStats()
    data = load_json(os.path.join(dir_path, "mocks", "town_data.json"))
    items = list(filter(lambda item: item["type"] == Item.GrandCharm, data["inventory_items"]))
    print(len(items))
    for item in items:
        action = get_pickit_action(item, pickit_config, { "health": 0, "mana": 2, "rejuv": 1 }, )
        print(f"\n\n{'-' * 80}\n{action}{'-' }")
        pp.pprint(item)

if __name__ == "__main__":
    pickit_test()
