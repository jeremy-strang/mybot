import os, sys, threading, ast, configparser, numpy as np
from re import I
from dataclasses import dataclass
from logger import Logger
from git import Repo
# from pickit.pickit_config import PickitConfig, pickit_config

sys.path.insert(0, "./config")
from pickit_default import PickitConfig, pickit_config

config_lock = threading.Lock()

def _default_iff(value, iff, default = None):
    return default if value == iff else value

@dataclass
class ItemProps:
    pickit_type: int = 0
    include: list[str] = None
    exclude: list[str] = None
    include_type: str = "OR"
    exclude_type: str = "OR"

class Config:
    data_loaded = False
    # all configparser objects
    _config = None
    _game_config = None
    _pickit_config = None
    _shop_config = None
    _transmute_config = None
    _custom = None
    _custom_pickit_config = None
    # config data
    general = {}
    advanced_options = {}
    gamble = {}
    ui_roi = {}
    ui_pos = {}
    dclone = {}
    routes = {}
    routes_order = []
    char = {}
    items = {}
    colors = {}
    shop = {}
    path = {}
    blizz_sorc = {}
    light_sorc = {}
    nova_sorc = {}
    hammerdin = {}
    trapsin = {}
    barbarian = {}
    necro = {}
    zerker_barb = {}
    singer_barb = {}
    basic = {}
    basic_ranged = {}
    active_branch = ""
    latest_commit_sha = ""
    custom_files = []
    pickit_config: PickitConfig = pickit_config

    def __init__(self):
        with config_lock:
            if not Config.data_loaded:
                Config.data_loaded = True
                Config.load_data()

    @staticmethod
    def _select_val(section: str, key: str = None):
        if section in Config._custom and key in Config._custom[section]:
            return Config._custom[section][key]
        elif section in Config._config:
            return Config._config[section][key]
        elif section in Config._custom_pickit_config and key in Config._custom_pickit_config[section]:
            return Config._custom_pickit_config[section][key]
        elif section in Config._pickit_config:
            return Config._pickit_config[section][key]
        elif section in Config._shop_config:
            return Config._shop_config[section][key]
        else:
            return Config._game_config[section][key]

    @staticmethod
    def parse_item_config_string(key: str = None) -> ItemProps:
        string = Config._select_val("items", key).upper()
        return Config.string_to_item_prop(string)

    @staticmethod
    def string_to_item_prop(string: str) -> ItemProps:
        item_props = ItemProps()
        brk_on = 0
        brk_off = 0
        section = 0
        counter = 0
        start_section = 0
        start_item = 0
        include_list = []
        exclude_list = []
        for char in string:
            new_section = False
            counter+=1
            if char == "(":
                brk_on +=1
            elif char == ")":
                brk_off += 1
            if ((char == "," and brk_on==brk_off)):
                new_section = True
                if  (counter == len (string)):
                    string_section = string [start_section:counter]
                else:
                    string_section = string [start_section:counter-1]
                if section == 0:
                    item_props.pickit_type = int (string_section)
                section +=1
                start_section = counter
            if ((char == "," and (brk_on==brk_off+1)) or new_section or counter == len (string)):
                if new_section:
                    section -=1
                if start_item ==0:
                    start_item = start_section
                if  (counter == len (string)):
                    item = string [start_item:counter]
                else:
                    item = string [start_item:counter-1]
                if section == 0 and counter == len (string):
                    item_props.pickit_type = int (item)
                    pass
                if section ==1:
                    include_list.append (item)
                    start_item = counter +1
                elif section ==2:
                    exclude_list.append (item)
                    start_item = counter +1
                if new_section:
                    section +=1
        if (len (include_list)>0 and (len (include_list[0]) >=6)):
            if ("AND" in include_list[0][0: 6] and not ")" in include_list[0]):
                item_props.include_type = "AND"
            else:
                item_props.include_type = "OR"
        if (len (exclude_list)>0 and (len (exclude_list[0]) >=6)):
            if ("AND" in exclude_list[0][0:6] and not ")" in include_list[0]):
                item_props.exclude_type = "AND"
            else:
                item_props.exclude_type = "OR"
        for i in range (len(include_list)):
            include_list[i]  = include_list[i].replace (" ","").replace ("OR(","").replace ("AND(", "").replace ("(", "").replace (")","")
            include_list[i]  = include_list[i].split (",")
        for l in range (len (exclude_list)):
            exclude_list[l] = exclude_list[l].replace (" ","").replace ("OR(","").replace ("AND(", "").replace ("(", "").replace (")","")
            exclude_list[l] = exclude_list[l].split (",")
        item_props.include = include_list
        item_props.exclude = exclude_list
        return item_props

    @staticmethod
    def turn_off_goldpickup():
        with config_lock:
            Config.char["stash_gold"] = False
            Config.items["misc_gold"].pickit_type = 0

    @staticmethod
    def turn_on_goldpickup():
        with config_lock:
            Config.char["stash_gold"] = True
            Config.items["misc_gold"].pickit_type = 1

    @staticmethod
    def get_latest_commit_sha() -> str:
        try:
            repo = Repo(search_parent_directories=True)
            if repo is not None: return repo.head.object.hexsha
        except:
            Logger.debug("current source isn't on git or based on detached head")
        return ""

    @staticmethod
    def get_active_branch() -> str:
        try:
            repo = Repo(search_parent_directories=True)
            if repo is not None: return repo.active_branch
        except:
            Logger.debug("current source isn't on git or based on detached head")
        return ""
    
    @staticmethod
    def load_data():
        Logger.info("Loading config data")
        is_test_env = os.environ.get('RUN_ENV') == "test"
        Config._config = configparser.ConfigParser()
        Config._config.read('config/params.ini')
        Config._game_config = configparser.ConfigParser()
        Config._game_config.read('config/game.ini')
        Config._pickit_config = configparser.ConfigParser()
        Config._pickit_config.read('config/pickit.ini')
        Config._shop_config = configparser.ConfigParser()
        Config._shop_config.read('config/shop.ini')
        Config._custom = configparser.ConfigParser()
        Config._custom_pickit_config = configparser.ConfigParser()

        if os.path.exists('config/pickit.custom.ini'):
            Config._custom_pickit_config.read('config/pickit.custom.ini')
            Config.custom_files.append('./config/pickit.custom.ini')
        
        if os.path.exists('config/pickit_custom.py'):
            from pickit_custom import pickit_config
            if pickit_config is not None:
                id_rules = pickit_config.IdentifiedItems
                if id_rules is not None and type(id_rules) is dict:
                    Config.pickit_config.IdentifiedItems = id_rules
                    Logger.debug(f"Loaded {len(id_rules)} custom pickit rules for identifying items")
                
                unid_rules = pickit_config.UnidentifiedItems
                if unid_rules is not None and type(unid_rules) is dict:
                    Config.pickit_config.UnidentifiedItems = unid_rules
                    Logger.debug(f"Loaded {len(unid_rules)} custom pickit rules for identifying items")
                
                pot_rules = pickit_config.ConsumableItems
                if pot_rules is not None and type(id_rules):
                    Config.pickit_config.ConsumableItems = pot_rules
                    Logger.debug(f"Loaded {len(pot_rules)} custom pickit rules for consumable items")
                
                basic_rules = pickit_config.BasicItems
                if basic_rules is not None and type(id_rules):
                    Config.pickit_config.BasicItems = basic_rules
                    Logger.debug(f"Loaded {len(basic_rules)} custom pickit rules for basic items")
                
                normal_rules = pickit_config.NormalItems
                if normal_rules is not None and type(id_rules):
                    Config.pickit_config.NormalItems = normal_rules
                    Logger.debug(f"Loaded {len(normal_rules)} custom pickit rules for normal items")
            else:
                Logger.warning(f"Founding a custom pickit file but failed to parse it")

        if not is_test_env:
            if os.path.exists(f'config/custom.ini'):
                Logger.debug(f"Loading custom config")
                Config._custom.read(f'config/custom.ini')
                Config.custom_files.append('./config/custom.ini')

            char_type = Config._select_val("char", "type")
            if os.path.exists(f'config/{char_type}.custom.ini'):
                Logger.debug(f"Loading custom config for build {char_type}")
                Config._custom.read(f'config/{char_type}.custom.ini')
                Config.custom_files.append(f'./config/{char_type}.custom.ini')

        Config.general = {
            "saved_games_folder": Config._select_val("general", "saved_games_folder"),
            "name": Config._select_val("general", "name"),
            "summary": None,
            "max_game_length_s": float(Config._select_val("general", "max_game_length_s")),
            "max_consecutive_fails": int(Config._select_val("general", "max_consecutive_fails")),
            "max_runtime_before_break_m": float(_default_iff(Config._select_val("general", "max_runtime_before_break_m"), '', 0)),
            "break_length_m": float(_default_iff(Config._select_val("general", "break_length_m"), '', 0)),
            "randomize_runs": bool(int(Config._select_val("general", "randomize_runs"))),
            "difficulty": Config._select_val("general", "difficulty"),
            "message_api_type": Config._select_val("general", "message_api_type"),
            "custom_message_hook": Config._select_val("general", "custom_message_hook"),
            "custom_loot_message_hook": Config._select_val("general", "custom_loot_message_hook"),
            "custom_error_message_hook": Config._select_val("general", "custom_error_message_hook"),
            "discord_status_count": False if not Config._select_val("general", "discord_status_count") else int(Config._select_val("general", "discord_status_count")),
            "discord_status_condensed": bool(int(Config._select_val("general", "discord_status_condensed"))),
            "discord_experience_report": bool(int(Config._select_val("general", "discord_experience_report"))),
            "info_screenshots": bool(int(Config._select_val("general", "info_screenshots"))),
            "loot_screenshots": bool(int(Config._select_val("general", "loot_screenshots"))),
            "games_via_lobby": bool(int(Config._select_val("general", "games_via_lobby"))),
            "d2r_path": Config._select_val("general", "d2r_path"),
            "restart_d2r_when_stuck": bool(int(Config._select_val("general", "restart_d2r_when_stuck"))),
            "kill_d2r_on_bot_exception": bool(int(Config._select_val("general", "kill_d2r_on_bot_exception"))),
        }

        # Added for dclone ip hunting
        Config.dclone = {
            "region_ips": Config._select_val("dclone", "region_ips"),
            "dclone_hotip": Config._select_val("dclone", "dclone_hotip"),
        }

        Config.routes = {}
        order_str = Config._select_val("routes", "order").replace("run_eldritch", "run_shenk")
        Config.routes_order = [x.strip() for x in order_str.split(",")]
        del Config._config["routes"]["order"]
        for key in Config._config["routes"]:
            Config.routes[key] = bool(int(Config._select_val("routes", key)))

        Config.char = {
            "type": Config._select_val("char", "type"),
            "show_items": Config._select_val("char", "show_items"),
            "inventory_screen": Config._select_val("char", "inventory_screen"),
            "stand_still": Config._select_val("char", "stand_still"),
            "force_move": Config._select_val("char", "force_move"),
            "num_loot_columns": int(Config._select_val("char", "num_loot_columns")),
            "take_health_potion": float(Config._select_val("char", "take_health_potion")),
            "take_mana_potion": float(Config._select_val("char", "take_mana_potion")),
            "take_rejuv_potion_health": float(Config._select_val("char", "take_rejuv_potion_health")),
            "take_rejuv_potion_mana": float(Config._select_val("char", "take_rejuv_potion_mana")),
            "heal_merc": float(Config._select_val("char", "heal_merc")),
            "heal_rejuv_merc": float(Config._select_val("char", "heal_rejuv_merc")),
            "chicken": float(Config._select_val("char", "chicken")),
            "merc_chicken": float(Config._select_val("char", "merc_chicken")),
            "tp": Config._select_val("char", "tp"),
            "belt_rows": int(Config._select_val("char", "belt_rows")),
            "show_belt": Config._select_val("char", "show_belt"),
            "potion1": Config._select_val("char", "potion1"),
            "potion2": Config._select_val("char", "potion2"),
            "potion3": Config._select_val("char", "potion3"),
            "potion4": Config._select_val("char", "potion4"),
            "belt_rejuv_columns": int(Config._select_val("char", "belt_rejuv_columns")),
            "belt_hp_columns": int(Config._select_val("char", "belt_hp_columns")),
            "belt_mp_columns": int(Config._select_val("char", "belt_mp_columns")),
            "stash_gold": bool(int(Config._select_val("char", "stash_gold"))),
            "stop_gold_pickup_above": int(Config._select_val("char", "stop_gold_pickup_above")),
            "start_gold_pickup_below": int(Config._select_val("char", "start_gold_pickup_below")),
            "gold_trav_only": bool(int(Config._select_val("char", "gold_trav_only"))),
            "use_merc": bool(int(Config._select_val("char", "use_merc"))),
            "id_items": bool(int(Config._select_val("char", "id_items"))),
            "open_chests": bool(int(Config._select_val("char", "open_chests"))),
            "fill_shared_stash_first": bool(int(Config._select_val("char", "fill_shared_stash_first"))),
            "pre_buff_every_run": bool(int(Config._select_val("char", "pre_buff_every_run"))),
            "cta_available": bool(int(Config._select_val("char", "cta_available"))),
            "barb_pre_buff_weapon_swap": bool(int(Config._select_val("char", "barb_pre_buff_weapon_swap"))),
            "barb_pre_hork_weapon_swap": bool(int(Config._select_val("char", "barb_pre_hork_weapon_swap"))),
            "teleport_weapon_swap": bool(int(Config._select_val("char", "teleport_weapon_swap"))),
            "weapon_switch": Config._select_val("char", "weapon_switch"),
            "battle_orders": Config._select_val("char", "battle_orders"),
            "battle_command": Config._select_val("char", "battle_command"),
            "casting_frames": int(Config._select_val("char", "casting_frames")),
            "atk_len_arc": float(Config._select_val("char", "atk_len_arc")),
            "atk_len_trav": float(Config._select_val("char", "atk_len_trav")),
            "atk_len_pindle": float(Config._select_val("char", "atk_len_pindle")),
            "atk_len_eldritch": float(Config._select_val("char", "atk_len_eldritch")),
            "atk_len_shenk": float(Config._select_val("char", "atk_len_shenk")),
            "atk_len_nihlathak": float(Config._select_val("char", "atk_len_nihlathak")),
            "atk_len_diablo_vizier": float(Config._select_val("char", "atk_len_diablo_vizier")),
            "atk_len_diablo_deseis": float(Config._select_val("char", "atk_len_diablo_deseis")),
            "atk_len_diablo_infector": float(Config._select_val("char", "atk_len_diablo_infector")),
            "atk_len_diablo": float(Config._select_val("char", "atk_len_diablo")),
            "atk_len_cs_trashmobs": float(Config._select_val("char", "atk_len_cs_trashmobs")),
            "kill_cs_trash": float(Config._select_val("char", "kill_cs_trash")),
            "runs_per_repair": False if not Config._select_val("char", "runs_per_repair") else int(Config._select_val("char", "runs_per_repair")),
            "gamble_items": False if not Config._select_val("char", "gamble_items") else Config._select_val("char", "gamble_items").replace(" ","").split(","),
            "chicken_if_dolls": bool(int(Config._select_val("char", "chicken_if_dolls"))),
            "chicken_if_souls": bool(int(Config._select_val("char", "chicken_if_souls"))),
            "chicken_nihlathak_conviction": bool(int(Config._select_val("char", "chicken_nihlathak_conviction"))),
            "send_throne_leecher_tp": bool(int(Config._select_val("char", "send_throne_leecher_tp"))),
            "density": ast.literal_eval (Config._select_val("char", "density")),
            "area": ast.literal_eval (Config._select_val("char", "area")),
        }

        # Sorc base config
        sorc_base_cfg = dict(Config._config["sorceress"])
        if "sorceress" in Config._custom:
            sorc_base_cfg.update(dict(Config._custom["sorceress"]))
        # blizz sorc
        Config.blizz_sorc = dict(Config._config["blizz_sorc"])
        if "blizz_sorc" in Config._custom:
            Config.blizz_sorc.update(dict(Config._custom["blizz_sorc"]))
        Config.blizz_sorc.update(sorc_base_cfg)
        # light sorc
        Config.light_sorc = dict(Config._config["light_sorc"])
        if "light_sorc" in Config._custom:
            Config.light_sorc.update(dict(Config._custom["light_sorc"]))
        Config.light_sorc.update(sorc_base_cfg)
        # nova sorc
        Config.nova_sorc = dict(Config._config["nova_sorc"])
        if "nova_sorc" in Config._custom:
            Config.nova_sorc.update(dict(Config._custom["nova_sorc"]))
        Config.nova_sorc.update(sorc_base_cfg)

        # Palandin config
        Config.hammerdin = Config._config["hammerdin"]
        if "hammerdin" in Config._custom:
            Config.hammerdin.update(Config._custom["hammerdin"])

        # Assasin config
        Config.trapsin = Config._config["trapsin"]
        if "trapsin" in Config._custom:
            Config.trapsin.update(Config._custom["trapsin"])

        # Singer Barb config
        Config.singer_barb = Config._config["singer_barb"]
        if "singer_barb" in Config._custom:
            Config.singer_barb.update(Config._custom["singer_barb"])
        Config.singer_barb = dict(Config.singer_barb)
        Config.singer_barb["cry_frequency"] = float(Config.singer_barb["cry_frequency"])

        # Zerker Barb config
        Config.zerker_barb = Config._config["zerker_barb"]
        if "zerker_barb" in Config._custom:
            Config.zerker_barb.update(Config._custom["zerker_barb"])
        Config.zerker_barb = dict(Config.zerker_barb)

        # Basic config
        Config.basic = Config._config["basic"]
        if "basic" in Config._custom:
            Config.basic.update(Config._custom["basic"])

        # Basic Ranged config
        Config.basic_ranged = Config._config["basic_ranged"]
        if "basic_ranged" in Config._custom:
            Config.basic_ranged.update(Config._custom["basic_ranged"])

        # Necro config
        Config.necro = Config._config["necro"]
        if "necro" in Config._custom:
            Config.necro.update(Config._custom["necro"])

        Config.advanced_options = {
            "pathing_delay_factor": min(max(int(Config._select_val("advanced_options", "pathing_delay_factor")), 1), 10),
            "message_headers": Config._select_val("advanced_options", "message_headers"),
            "message_body_template": Config._select_val("advanced_options", "message_body_template"),
            "graphic_debugger_layer_creator": bool(int(Config._select_val("advanced_options", "graphic_debugger_layer_creator"))),
            "logg_lvl": Config._select_val("advanced_options", "logg_lvl"),
            "exit_key": Config._select_val("advanced_options", "exit_key"),
            "resume_key": Config._select_val("advanced_options", "resume_key"),
            "auto_settings_key": Config._select_val("advanced_options", "auto_settings_key"),
            "restore_settings_from_backup_key": Config._select_val("advanced_options", "restore_settings_from_backup_key"),
            "settings_backup_key": Config._select_val("advanced_options", "settings_backup_key"),
            "graphic_debugger_key": Config._select_val("advanced_options", "graphic_debugger_key"),
            "save_d2r_data_to_file_key": Config._select_val("advanced_options", "save_d2r_data_to_file_key"),
            'debug_overlay': bool(int(Config._select_val("advanced_options", "debug_overlay"))),
            'obs_run_recording_enabled':bool(int(Config._select_val("advanced_options", "obs_run_recording_enabled"))),
            'obs_debug_replays_enabled':bool(int(Config._select_val("advanced_options", "obs_debug_replays_enabled"))),
            "obs_cli_path": Config._select_val("advanced_options", "obs_cli_path"),
            "obs_scene_name": Config._select_val("advanced_options", "obs_scene_name"),
            "dump_data_to_pickle_for_debugging": bool(Config._select_val("advanced_options", "dump_data_to_pickle_for_debugging")),
        }

        Config.items = {}
        for key in Config._pickit_config["items"]:
            try:
                Config.items[key] = Config.parse_item_config_string(key)
                if Config.items[key].pickit_type and not os.path.exists(f"./assets/items/{key}.png"):
                    print(f"Warning: You activated {key} in pickit, but there is no img available in assets/items")
            except ValueError as e:
                print(f"Error with pickit config: {key} ({e})")

        if "items" in Config._custom_pickit_config:
            for key in Config._custom_pickit_config["items"]:
                try:
                    Config.items[key] = Config.parse_item_config_string(key)
                    if Config.items[key].pickit_type and not os.path.exists(f"./assets/items/{key}.png"):
                        print(f"Warning: You activated {key} in pickit, but there is no img available in assets/items")
                except ValueError as e:
                    print(f"Error with pickit config: {key} ({e})")

        Config.colors = {}
        for key in Config._game_config["colors"]:
            Config.colors[key] = np.split(np.array([int(x) for x in Config._select_val("colors", key).split(",")]), 2)

        Config.ui_pos = {}
        for key in Config._game_config["ui_pos"]:
            Config.ui_pos[key] = int(Config._select_val("ui_pos", key))

        Config.ui_roi = {}
        for key in Config._game_config["ui_roi"]:
            Config.ui_roi[key] = np.array([int(x) for x in Config._select_val("ui_roi", key).split(",")])

        Config.path = {}
        for key in Config._game_config["path"]:
            Config.path[key] = np.reshape(np.array([int(x) for x in Config._select_val("path", key).split(",")]), (-1, 2))

        Config.shop = {
            "shop_trap_claws": bool(int(Config._select_val("claws", "shop_trap_claws"))),
            "shop_melee_claws": bool(int(Config._select_val("claws", "shop_melee_claws"))),
            "shop_3_skills_ias_gloves": bool(int(Config._select_val("gloves", "shop_3_skills_ias_gloves"))),
            "shop_2_skills_ias_gloves": bool(int(Config._select_val("gloves", "shop_2_skills_ias_gloves"))),
            "trap_min_score": int(Config._select_val("claws", "trap_min_score")),
            "melee_min_score": int(Config._select_val("claws", "melee_min_score")),
            "shop_hammerdin_scepters": bool(int(Config._select_val("scepters", "shop_hammerdin_scepters"))),
            "speed_factor": float(Config._select_val("scepters", "speed_factor")),
            "apply_pather_adjustment": bool(int(Config._select_val("scepters", "apply_pather_adjustment"))),
        }
        stash_destination_str = Config._select_val("transmute","stash_destination")
        Config._transmute_config = {
            "stash_destination": [int(x.strip()) for x in stash_destination_str.split(",")],
            "transmute_every_x_game": Config._select_val("transmute","transmute_every_x_game"),
        }

        Config.active_branch = Config.get_active_branch()
        Config.latest_commit_sha = Config.get_latest_commit_sha()
