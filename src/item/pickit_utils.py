RUNES = [
    "Zod Rune",
    "Cham Rune",
    "Jah Rune",
    "Ber Rune",
    "Sur Rune",
    "Lo Rune",
    "Ohm Rune",
    "Vex Rune",
    "Gul Rune",
    "Ist Rune",
    "Mal Rune",
    "Um Rune",
    "Pul Rune",
    "Lem Rune"
]

EXACT_NAMES = [
    "Token of Absolution",
    "Topaz",
    "Amethyst",
]

UNIQUES = [
    ()
]

def get_pickit_priority(item: dict):
    result = 0
    if item and type(item) is dict:
        name = "" + str(item["name"])
        if name == "ItemNotFound" and item["hash_str"]:
            name = item["hash_str"][0:item["hash_str"].find("/")]
        for rune in RUNES:
            if name == rune or name.lower().replace(" ", "").startswith(rune.lower().replace(" ", "")):
                result = 2
                break
        for n in EXACT_NAMES:
            if name == n or name.lower().replace(" ", "") == n.lower().replace(" ", ""):
                result = 1
                break
    return result
