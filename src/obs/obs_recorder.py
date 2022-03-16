import time
import os
import traceback

from config import Config
from logger import Logger

class ObsRecorder:
    """
    Allows recording with OBS. This requires:
    OBS running with the correct scene selected (https://obsproject.com/)
    obs-websocket OBS plugin (https://github.com/obsproject/obs-websocket),
    obs-cli (https://github.com/muesli/obs-cli)
    """

    def __init__(self, config: Config):
        self._config = config
        self._is_replay_enabled = self._config.advanced_options["obs_debug_replays_enabled"]
        self._is_recording_enabled = self._config.advanced_options["obs_run_recording_enabled"]
        self._cli_path = self._config.advanced_options["obs_cli_path"]
        self._is_recording_active = False
        if self._is_replay_enabled or self._is_recording_enabled:
            if not os.path.isfile(self._cli_path):
                Logger.error(f"Error initializing OBS recorder, invalid OBS CLI path: {self._cli_path}")
                self._is_replay_enabled = False
                self._is_recording_enabled = False

    def start_recording_if_enabled(self):
        if self._is_recording_enabled:
            if self._is_recording_active:
                self.stop_recording_if_enabled()
            try:
                if os.system(f"{self._cli_path} recording start"):
                    # Logger.error("Error starting OBS recording")
                    self._is_recording_active = False
                else:
                    # Logger.error("Starting OBS recording")
                    self._is_recording_active = True
            except BaseException as e:
                # Logger.error("Error starting OBS recording: " + e)
                # traceback.print_exc()
                self._is_recording_active = False
    
    def stop_recording_if_enabled(self):
        if self._is_recording_enabled:
            try:
                if os.system(f"{self._cli_path} recording stop"):
                    # Logger.error("Error stopping OBS recording")
                    pass
            except BaseException as e:
                # Logger.error("Error stopping OBS recording: " + e)
                # traceback.print_exc()
                pass
            self._is_recording_active = False

    def start_replaybuffer_if_enabled(self):
        if self._is_replay_enabled:
            try:
                if os.system(f"{self._cli_path} replaybuffer start"):
                    # Logger.error("Error starting OBS replaybuffer")
                    pass
            except BaseException as e:
                # Logger.error("Error starting OBS replaybuffer: " + e)
                # traceback.print_exc()
                pass
    
    def stop_replaybuffer_if_enabled(self):
        if self._is_replay_enabled:
            try:
                if os.system(f"{self._cli_path} replaybuffer stop"):
                    # Logger.error("Error stopping OBS replaybuffer")
                    pass
            except BaseException as e:
                # Logger.error("Error stopping OBS replaybuffer: " + e)
                # traceback.print_exc()
                pass
    
    def save_replay_if_enabled(self):
        if self._is_replay_enabled:
            try:
                if os.system(f"{self._cli_path} replaybuffer save"):
                    # Logger.error("Error saving OBS replay")
                    pass
            except BaseException as e:
                # Logger.error("Error saving OBS replay: " + e)
                # traceback.print_exc()
                pass
