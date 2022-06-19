from config import Config
from logger import Logger
import numpy as np
import json
import requests

class GenericApi:
    def __init__(self):
        self._config = Config()

    def send_item(self, item: str, image:  np.ndarray, location: str):
        msg = f"Found {item} at {location}"
        url = self._config.general['custom_loot_message_hook']
        self._send(msg, url)
        
    def send_death(self, location: str, image_path: str = None):
        msg = f"You have died at {location}"
        url = self._config.general['custom_error_message_hook']
        self._send(msg, url)
        
    def send_chicken(self, location: str, image_path: str = None):
        msg = f"You have chickened at {location}"
        self._send(msg)
        
    def send_gold(self):
        msg = f"All stash tabs and character are full of gold, turn of gold pickup"
        url = self._config.general['custom_error_message_hook']
        self._send(msg, url)

    def send_stash(self):
        msg = f"All stash is full, quitting"
        url = self._config.general['custom_error_message_hook']
        self._send(msg, url)
    
    def send_wrong_character(self, name):
        msg = f"Wrong character name detected, expected {self._config.advanced_options['expected_character_names']} but got {name}"
        url = self._config.general['custom_error_message_hook']
        self._send(msg, url)

    def send_message(self, msg: str, is_error=False):
        if is_error:
            url = self._config.general['custom_error_message_hook']
        self._send(msg, url)

    def _send(self, msg: str, url: str = None):
        msg = f"{self._config.general['name']}: {msg}"
        
        url = self._config.general['custom_message_hook'] if not url else url
        if not url:
            return

        headers = {}
        if self._config.advanced_options['message_headers']:
            headers = json.loads(self._config.advanced_options['message_headers'])

        data = json.loads(self._config.advanced_options['message_body_template'].format(msg=msg), strict=False)

        try:
            requests.post(url, headers=headers, json=data)
        except BaseException as err:
            Logger.error("Error sending generic message: " + err)
