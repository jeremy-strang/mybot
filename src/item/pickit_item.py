from item.types import ItemType, ItemQuality, ItemMode, InventoryPage, BodyLoc, StashType, ItemFlag, Stat

import pprint
pp = pprint.PrettyPrinter(depth=6)

class PickitItem:
    def __init__(self, item: dict):
        pp.pprint(item)
        self._raw_item = item
        self.id = item["id"]
        self.type = item["type"]
        self.name = item["name"]
        self.base_name = item["base_name"]
        self.hash_str = item["hash_str"]
        self.id = item["id"]
        self.inventory_page = item["inventory_page"]
        self.is_hovered = item["is_hovered"]
        self.is_identified = item["is_identified"]
        self.item_mode = item["item_mode"]
        self.item_mode_mapped = item["item_mode_mapped"]
        self.name = item["name"]
        self.num_sockets = item["num_sockets"]
        self.position = item["position"]
        self.quality = item["quality"]
        self.tier = item["tier"]
        self.unique_name = item["unique_name"] if self.quality == ItemQuality.Unique else ""
        self.set_name = item["set_name"] if self.quality == ItemQuality.Set else ""
        self._raw_flags = item["flags"]
        self.flags = ", ".split(self._raw_flags) if self._raw_flags and self._raw_flags != "0" else []
        self._raw_stats = item["stats"]
        self.stats = {}
        if item["stats"]:
            for entry in item["stats"]:
                self.stats[entry["key"]] = entry["value"]

    def check(self, stat: Stat, operator: str, value):
        print(f"Checking item {self.name}: {stat} {operator} {value}:")
        result = False
        if stat in self.stats:
            val = self.stats[stat]

            if val is None:
                result = False
            elif operator == "==":
                result = val == value
            elif operator == "!=":
                result = val != value
            elif operator == ">=":
                result = val >= value
            elif operator == ">":
                result = val > value
            elif operator == "<=":
                result = val <= value
            elif operator == "<":
                result = val < value
            print(f"    {stat} {operator} {val}: {result}")
        else:
            print(f"    {stat} was not in self.stats: {self.stats}")
        return result
