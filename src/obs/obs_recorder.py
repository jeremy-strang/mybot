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
        self._is_obs_enabled = self._config.advanced_options["obs_recording_enabled"]
        self._cli_path = self._config.advanced_options["obs_cli_path"]
        self._scene_name = self._config.advanced_options["obs_scene_name"]
        self._is_recording_active = False
        if self._is_obs_enabled:
            if os.path.isfile(self._cli_path):
                if len(self._scene_name) > 0:
                    try:
                        if not os.system(f"{self._cli_path} scene current {self._scene_name}"):
                            Logger.error(f"Error selecting OBS scene {self._scene_name}")
                    except BaseException as e:
                        Logger.error("Error initializing OBS scene: " + e)
            else:
                self._is_obs_enabled = False

    def start_recording_if_enabled(self):
        if self._is_obs_enabled:
            if self._is_recording_active:
                self.stop_recording_if_enabled()
            try:
                if os.system(f"{self._cli_path} recording start"):
                    self._is_recording_active = False
                    Logger.error("Error starting OBS recording")
                else:
                    Logger.error("Starting OBS recording")
                    self._is_recording_active = True
            except BaseException as e:
                self._is_recording_active = False
                Logger.error("Error starting OBS recording: " + e)
                traceback.print_exc()
    
    def stop_recording_if_enabled(self):
        if self._is_obs_enabled:
            try:
                if os.system(f"{self._cli_path} recording stop"):
                    Logger.error("Error stopping OBS recording")
                else:
                    self._is_recording_active = False
            except BaseException as e:
                Logger.error("Error stopping OBS recording: " + e)
                traceback.print_exc()

    def start_replaybuffer_if_enabled(self):
        if self._is_obs_enabled:
            try:
                if os.system(f"{self._cli_path} replaybuffer start"):
                    Logger.error("Error starting OBS replaybuffer")
            except BaseException as e:
                Logger.error("Error starting OBS replaybuffer: " + e)
                traceback.print_exc()
    
    def stop_replaybuffer_if_enabled(self):
        if self._is_obs_enabled:
            try:
                if os.system(f"{self._cli_path} replaybuffer stop"):
                    Logger.error("Error stopping OBS replaybuffer")
            except BaseException as e:
                Logger.error("Error stopping OBS replaybuffer: " + e)
                traceback.print_exc()
    
    def save_replay_if_enabled(self):
        if self._is_obs_enabled:
            try:
                if os.system(f"{self._cli_path} replaybuffer save"):
                    Logger.error("Error saving OBS replay")
            except BaseException as e:
                Logger.error("Error saving OBS replay: " + e)
                traceback.print_exc()
