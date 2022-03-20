

from api.mapassist import MapAssistApi
from .monster_rule import MonsterRule
from .monster_type import MonsterType

class Monster:
    def __init__(self, data: dict):
        self.id = data["id"]
        self.mob_number = data["mob_number"]
        self.type = data["type"]
        self.id = data["id"]
        self.id = data["id"]

class MonsterTracker:
    def __init__(self, api: MapAssistApi, rules: MonsterRule=None):
        self._api = api
        self._rules: list[MonsterRule] = rules
        self._monsters: list[Monster] = None

    @staticmethod
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


