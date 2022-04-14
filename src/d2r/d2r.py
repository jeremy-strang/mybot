
class D2rMenu:
    Inventory = "inventory"
    Character = "character"
    SkillSelect = "skill_select"
    SkillTree = "skill_tree"
    Chat = "chat"
    NpcInteract = "npc_interact"
    EscMenu = "esc_menu"
    Map = "map"
    NpcShop = "npc_shop"
    QuestLog = "quest_log"
    Waypoint = "waypoint"
    Party = "party"
    Stash = "stash"
    Cube = "cube"
    PotionBelt = "potion_belt"
    MercenaryInventory = "mercenary_inventory"

class D2rArea:
    Harrogath = "Harrogath"
    ThePandemoniumFortress = "ThePandemoniumFortress"
    KurastDocks = "KurastDocks"
    LutGholein = "LutGholein"
    RogueEncampment = "RogueEncampment"

TOWNS = set([
    D2rArea.RogueEncampment,
    D2rArea.LutGholein,
    D2rArea.KurastDocks,
    D2rArea.ThePandemoniumFortress,
    D2rArea.Harrogath])
