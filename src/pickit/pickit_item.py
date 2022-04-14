from typing import Any
from pickit.item_types import ITEM_CLASSES, Action, Item, Quality, ItemMode, ItemClass, InventoryPage, BodyLoc, SkillTree, StashType, Flag, Stat

class PickitItem:
    def __init__(self, item: dict, action: Action = Action.DontKeep):
        self._raw_item = item
        self.stats = {}
        self.id = self.stats["id"] = item["id"]
        self.type = self.stats["type"] = item["type"]
        self.name = self.stats["name"] = item["name"]
        # self.base_name = self.stats["base_name"] = item["base_name"]
        # self.hash_str = self.stats["hash_str"] = item["hash_str"]
        self.inventory_page = self.stats["inventory_page"] = item["inventory_page"]
        self.is_hovered = self.stats["is_hovered"] = item["is_hovered"]
        self.is_identified = self.stats["is_identified"] = item["is_identified"]
        self.mode = self.stats["mode"] = item["mode"]
        self.mode_mapped = self.stats["mode_mapped"] = item["mode_mapped"]
        self.sockets = self.stats["sockets"] = item["sockets"]
        self.position = self.stats["position"] = item["position"]
        self.quality = self.stats["quality"] = Quality(item["quality"])
        self.tier = self.stats["tier"] = item["tier"]
        self.unique_name = self.stats["unique_name"] = item["unique_name"] if self.quality == Quality.Unique else ""
        self.set_name = self.stats["set_name"] = item["set_name"] if self.quality == Quality.Set else ""
        self._raw_flags = self.stats["_raw_flags"] = item["flags"]
        self.flags = self.stats["flags"] = ", ".split(self._raw_flags) if self._raw_flags and self._raw_flags != "0" else []
        self._raw_stats = self.stats["_raw_stats"] = item["stats"]
        self.is_ethereal = self.stats["is_ethereal"] = Flag.Ethereal in item["flags"]
        self.action = Action(action)
        self.item_class = self.stats["item_class"] = ITEM_CLASSES[self.type] if self.type in ITEM_CLASSES else None

        if item["stats"]:
            fr = 0
            cr = 0
            lr = 0
            pr = 0
            for entry in item["stats"]:
                key = entry["key"]
                val = entry["value"]
                self.stats[key] = val
                if key == Stat.FireResist: fr = val
                elif key == Stat.ColdResist: cr = val
                elif key == Stat.LightningResist: lr = val
                elif key == Stat.PoisonResist: pr = val
            # Compute all res stat
            if fr > 0 and cr > 0 and lr > 0 and pr > 0:
                self.stats[Stat.AllResist] = min(fr, cr, lr, pr)

            # Determine unique amulet/ring name
            if self.quality == Quality.Unique and self.type == Item.Ring:
                if self.check(Stat.AllSkills, ">=", 1) and self.check(Stat.MaxMana, ">=", 20):
                    self.unique_name = "Stone of Jordan"
                elif self.check(Stat.AllSkills, ">=", 1) and self.check(Stat.LifeSteal, ">=", 3):
                    self.unique_name = "Bul-Kathos' Wedding Band"
                elif self.check(Stat.AbsorbLightningPercent, ">=", 10):
                    self.unique_name = "Wisp Projector"
                elif self.check(Stat.Dexterity, ">=", 15) and self.check(Stat.AttackRating, ">=", 150):
                    self.unique_name = "Raven Frost"
                elif self.check(Stat.MagicDamageReduction, ">=", 12):
                    self.unique_name = "Dwarf Star"
                elif self.check(Stat.MagicFind, ">=", 15) and self.check(Stat.AttackRating, ">=", 50):
                    self.unique_name = "Nagelring"
                self.name = self.unique_name + " Ring"
            elif self.quality == Quality.Unique and self.type == Item.Amulet:
                if self.check(Stat.AllSkills, ">=", 2) and self.check(Stat.AllResist, ">=", 20):
                    self.unique_name = "Mara's Kaleidoscope"
                elif self.check(Stat.AllSkills, ">=", 2) and self.check(Stat.LightningResist, ">=", 25):
                    self.unique_name = "Highlord's Wrath"
                elif self.check(Stat.LightRadius, ">=", 3):
                    self.unique_name = "Atma's Scarab"
                elif self.check(SkillTree.PaladinDefensiveAuras, ">=", 1):
                    self.unique_name = "Seraph's Hymn"
                self.name = self.unique_name + " Amulet"
    
    def get_summary(self) -> str:
        result = f"{self.name}"
        if type(self._raw_stats) is dict:
            stat_list = []
            for entry in self._raw_stats:
                key = entry["key"]
                val = entry["value"]
                stat_list.append(f"{key}: {val}")
            result += f" ({', '.join(stat_list)})"
        return result

    def check(self, stat: Stat, operator: str, value):
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
        return result
