
def get_pickit_priority(item: dict):
    if item and type(item) is dict:
        name = "" + str(item["name"])
        for rune in ["Zod", "Cham", "Jah", "Ber", "Sur", "Lo", "Ohm", "Vex", "Gul", "Ist", "Mal", "Um", "Pul"]:
            rune_full = rune + " Rune"
            if name == rune_full or name.lower().replace(" ", "").startswith(rune_full.lower().replace(" ", "")):
                return 2
        if name == "Topaz" or name.lower().replace(" ", "") == "topaz":
            return 1
        if name == "Amethyst" or name.lower().replace(" ", "") == "amethyst":
            return 1
    return 0
