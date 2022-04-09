from typing import Any
from item.types import ItemType, ItemQuality, ItemMode, InventoryPage, BodyLoc, SkillTree, StashType, ItemFlag, Stat

class PickitItem:
    def __init__(self, item: dict):
        self._raw_item = item
        self.stats = {}
        self.id = self.stats["id"] = item["id"]
        self.type = self.stats["type"] = item["type"]
        self.name = self.stats["name"] = item["name"]
        self.base_name = self.stats["base_name"] = item["base_name"]
        self.hash_str = self.stats["hash_str"] = item["hash_str"]
        self.inventory_page = self.stats["inventory_page"] = item["inventory_page"]
        self.is_hovered = self.stats["is_hovered"] = item["is_hovered"]
        self.is_identified = self.stats["is_identified"] = item["is_identified"]
        self.item_mode = self.stats["item_mode"] = item["item_mode"]
        self.item_mode_mapped = self.stats["item_mode_mapped"] = item["item_mode_mapped"]
        self.name = self.stats["name"] = item["name"]
        self.sockets = self.stats["sockets"] = item["sockets"]
        self.position = self.stats["position"] = item["position"]
        self.quality = self.stats["quality"] = item["quality"]
        self.tier = self.stats["tier"] = item["tier"]
        self.unique_name = self.stats["unique_name"] = item["unique_name"] if self.quality == ItemQuality.Unique else ""
        self.set_name = self.stats["set_name"] = item["set_name"] if self.quality == ItemQuality.Set else ""
        self._raw_flags = self.stats["_raw_flags"] = item["flags"]
        self.flags = self.stats["flags"] = ", ".split(self._raw_flags) if self._raw_flags and self._raw_flags != "0" else []
        self._raw_stats = self.stats["_raw_stats"] = item["stats"]
        self.is_ethereal = self.stats["is_ethereal"] = ItemFlag.Ethereal in item["flags"]
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
            if self.quality == ItemQuality.Unique and self.type == ItemType.Ring:
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
            elif self.quality == ItemQuality.Unique and self.type == ItemType.Amulet:
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
