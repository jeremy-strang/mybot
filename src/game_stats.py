import numpy as np
import time
import threading
import inspect
from beautifultable import BeautifulTable

from logger import Logger
from config import Config
from messages import Messenger
from utils.misc import hms
from version import __version__


class GameStats:
    filtered_items = set(["Potion", "Gold", "Chipped Diamond", "Flawed Diamond", "Diamond", "Flawless Diamond", "Chipped Skull", "Flawed Skull", "Skull", "Flawless Skull", "_potion", "misc_gold", "_amethyst", "_ruby", "misc_chipped_diamond", "misc_flawed_diamond", "misc_diamond", "misc_flawless_diamond", "_topaz", "_emerald", "_sapphire", "misc_chipped_skull", "misc_flawed_skull", "misc_skull", "misc_flawless_skull"])

    def __init__(self):
        self._config = Config()
        self._messenger = Messenger()
        self._start_time = time.time()
        self._timer = None
        self._timepaused = None
        self._paused = False
        self._game_counter = 0
        self._chicken_counter = 0
        self._death_counter = 0
        self._merc_death_counter = 0
        self._runs_failed = 0
        self._run_counter = 1
        self._consecutive_runs_failed = 0
        self._failed_game_time = 0
        self._location = None
        self._location_stats = {}
        self._location_stats["totals"] = { "items": 0, "discarded": 0, "deaths": 0, "chickens": 0, "merc_deaths": 0, "failed_runs": 0 }
        self._stats_filename = f'stats_{time.strftime("%Y%m%d_%H%M%S")}.log'
        self._nopickup_active = False
        self._did_chicken_last_run = False
        

    def update_location(self, loc: str):
        if self._location != loc:
            self._location = str(loc)
            self.populate_location_stat()

    def populate_location_stat(self):
        if self._location not in self._location_stats:
            self._location_stats[self._location] = { "items": [], "discarded": [], "deaths": 0, "chickens": 0, "merc_deaths": 0, "failed_runs": 0 }

    def log_item_discard(self, item_desc: str, send_message: bool):
        Logger.info(f"Discarded an item that didn't meet requirements: {item_desc}")
        if self._location is not None and not any(substring in item_desc for substring in self.filtered_items):
            self._location_stats[self._location]["discarded"].append(item_desc)
            self._location_stats["totals"]["discarded"] += 1

    def log_item_keep(self, item_name: str, send_message: bool, img: np.ndarray):
        Logger.info(f"Stashed and logged: {item_name}, send message: {send_message}")
        
        if self._location is not None and not any(substring in item_name for substring in self.filtered_items):
            self._location_stats[self._location]["items"].append(item_name)
            self._location_stats["totals"]["items"] += 1
        if send_message:
            self._messenger.send_item(item_name, img, self._location)

    def log_death(self, img: str):
        self._death_counter += 1
        if self._location is not None:
            self._location_stats[self._location]["deaths"] += 1
            self._location_stats["totals"]["deaths"] += 1

        self._messenger.send_death(self._location, img)

    def log_chicken(self, img: str):
        self._chicken_counter += 1
        if self._location is not None:
            self._location_stats[self._location]["chickens"] += 1
            self._location_stats["totals"]["chickens"] += 1
        self._messenger.send_chicken(self._location, img)
        self._did_chicken_last_run = True

    def log_merc_death(self):
        self._merc_death_counter += 1
        if self._location is not None:
            self._location_stats[self._location]["merc_deaths"] += 1
            self._location_stats["totals"]["merc_deaths"] += 1

    def log_start_game(self):
        if self._game_counter > 0:
            self._save_stats_to_file()
            if self._config.general["discord_status_count"] and self._game_counter % self._config.general["discord_status_count"] == 0:
                # every discord_status_count game send a message update about current status
                self._send_status_update()
        self._game_counter += 1
        self._timer = time.time()
        print("="*80)
        Logger.info(f"Starting game #{self._game_counter}")
        items = self._location_stats["totals"]["items"]
        discarded = self._location_stats["totals"]["discarded"]
        chickens = self._location_stats["totals"]["chickens"]
        failed_runs = self._location_stats["totals"]["failed_runs"]
        Logger.info(f"Items: {items}, discarded: {discarded}, chickens: {chickens}, fails: {failed_runs}")
        print("="*80)

    def log_end_game(self, failed: bool = False):
        elapsed_time = 0
        if self._timer is not None:
            elapsed_time = time.time() - self._timer
        self._timer = None
        if failed:
            self._runs_failed += 1
            self._consecutive_runs_failed += 1
            if self._location is not None:
                self._location_stats[self._location]["failed_runs"] += 1
                self._location_stats["totals"]["failed_runs"] += 1
            self._failed_game_time += elapsed_time
            Logger.warning(f"End failed game: Elapsed time: {elapsed_time:.2f}s Fails: {self._consecutive_runs_failed}")
        else:
            self._consecutive_runs_failed = 0
            Logger.info(f"End game. Elapsed time: {elapsed_time:.2f}s")

    def pause_timer(self):
        if self._timer is None or self._paused:
            return
        self._timepaused = time.time()
        self._paused = True

    def resume_timer(self):
        if self._timer is None or not self._paused:
            return
        pausetime = time.time() - self._timepaused
        self._timer = self._timer + pausetime
        self._paused = False

    def get_current_game_length(self):
        if self._timer is None:
            return 0
        if self._paused:
            return self._timepaused - self._timer
        else:
            return time.time() - self._timer

    def get_consecutive_runs_failed(self):
        return self._consecutive_runs_failed

    def _create_msg(self):
        elapsed_time = time.time() - self._start_time
        elapsed_time_str = hms(elapsed_time)
        avg_length_str = "n/a"
        good_games_count = self._game_counter - self._runs_failed
        if good_games_count > 0:
            good_games_time = elapsed_time - self._failed_game_time
            avg_length = good_games_time / float(good_games_count)
            avg_length_str = hms(avg_length)

        msg = f'\nSession length: {elapsed_time_str}\nGames: {self._game_counter}\nAvg Game Length: {avg_length_str}'

        table = BeautifulTable()
        table.set_style(BeautifulTable.STYLE_BOX_ROUNDED)
        for location in self._location_stats:
            if location == "totals":
                continue
            stats = self._location_stats[location]
            table.rows.append([location, len(stats["items"]), len(stats["discarded"]), stats["chickens"], stats["deaths"], stats["merc_deaths"], stats["failed_runs"]])

        table.rows.append([
            "T" if self._config.general['discord_status_condensed'] else "Total",
            self._location_stats["totals"]["items"],
            self._location_stats["totals"]["discarded"],
            self._location_stats["totals"]["chickens"],
            self._location_stats["totals"]["deaths"],
            self._location_stats["totals"]["merc_deaths"],
            self._location_stats["totals"]["failed_runs"]
        ])

        if self._config.general['discord_status_condensed']:
            table.columns.header = ["Run", "I", "J", "C", "D", "MD", "F"]
        else:
            table.columns.header = ["Run", "Items", "Junk", "Chicken", "Death", "Merc Death", "Failed Runs"]

        msg += f"\n{str(table)}\n"
        return msg

    def _send_status_update(self):
        msg = f"{self._create_msg()}"
        self._messenger.send_message(msg)

    def _save_stats_to_file(self):
        msg = self._create_msg()
        msg += "\nItems:"
        for location in self._location_stats:
            if location == "totals":
                continue
            stats = self._location_stats[location]
            msg += f"\n  {location}:"
            for item_name in stats["items"]:
                msg += f"\n    {item_name}"
        msg += "\nDiscarded:"
        for location in self._location_stats:
            if location == "totals":
                continue
            stats = self._location_stats[location]
            msg += f"\n  {location}:"
            for item_desc in stats["discarded"]:
                msg += f"\n    {item_desc}"
            

        with open(file=f"stats/{self._stats_filename}", mode="w+", encoding="utf-8") as f:
            f.write(msg)
