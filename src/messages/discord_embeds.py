from .generic_api import GenericApi
from config import Config
from logger import Logger
import cv2
import datetime
import traceback
import discord
from version import __version__
import numpy as np
from discord import Webhook, RequestsWebhookAdapter, Color, InvalidArgument

class DiscordEmbeds(GenericApi):
    def __init__(self):
        self._config = Config()
        self._file = None
        self._psnURL = "https://i.psnprofiles.com/games/3bffee/trophies/"
        self._webhook = None
        self._loot_webhook = None
        self._error_webhook = None
        try:
            self._webhook = Webhook.from_url(self._config.general['custom_message_hook'], adapter=RequestsWebhookAdapter(), )
            loot_url = self._config.general['custom_loot_message_hook']
            self._loot_webhook = Webhook.from_url(loot_url, adapter=RequestsWebhookAdapter(), ) if loot_url else self._webhook
            error_url = self._config.general['custom_error_message_hook']
            self._error_webhook = Webhook.from_url(error_url, adapter=RequestsWebhookAdapter(), ) if error_url else self._webhook
        except InvalidArgument:
            Logger.warning(f"Your custom_message_hook URL {self._config.general['custom_message_hook']} is invalid, Discord updates will not be sent")
    
    def send_discarded_item(self, item_description: str):
        player_summary = self._config.general['player_summary']
        msg = f"{player_summary}: Discarded an item that didn't meet requirements: {item_description}"
        self.send_message(msg, self._webhook)

    def send_item(self, item: str, image:  np.ndarray, location: str):
        d = datetime.datetime.now(datetime.timezone.utc)
        ts = d.strftime("%Y-%m-%d-%H%M%S")
        imgName = f"{item.replace(' ', '-')}-{ts}"
        _, w, _ = image.shape
        image = image[:, (w//2):,:]
        cv2.imwrite(f"./loot_screenshots/{imgName}.png", image)
        file = self._add_file(f"./loot_screenshots/{imgName}.png", f"{imgName}.png")
        e = discord.Embed(
            title="Item Stashed!",
            description=f"{item}",
            color=self._get_Item_Color(item),
        )
        e.set_image(url=f"attachment://{imgName}.png")
        self._send_embed(e, file, self._loot_webhook)

    def send_death(self, location, image_path):
        file = self._add_file(image_path, "death.png")
        e = discord.Embed(title=f"{self._config.general['name']} has died at {location}", color=Color.dark_red())
        e.title=(f"{self._config.general['name']} died")
        e.description=(f"Died at {location}")
        e.set_thumbnail(url=f"{self._psnURL}33L5e3600.png")
        e.set_image(url="attachment://death.png")
        self._send_embed(e, file, self._webhook)

    def send_chicken(self, location, image_path):
        file = self._add_file(image_path, "chicken.png")
        e = discord.Embed(title=f"{self._config.general['name']} has chickened at {location}", color=Color.dark_grey())
        e.title=(f"{self._config.general['name']} ran away")
        e.description=(f"chickened at {location}")
        e.set_thumbnail(url=f"{self._psnURL}39Ldf113b.png")
        e.set_image(url="attachment://chicken.png")
        self._send_embed(e, file, self._webhook)

    def send_stash(self):
        e = discord.Embed(title=f"{self._config.general['name']} has a full stash!", color=Color.dark_grey())
        e.title=(f"{self._config.general['name']} has a full stash!")
        e.description=(f"{self._config.general['name']} has to quit. \n They cannot store anymore items!")
        e.set_thumbnail(url=f"{self._psnURL}35L63a9df.png")
        self._send_embed(e, self._webhook)

    def send_gold(self):
        e = discord.Embed(title=f"{self._config.general['name']} is rich!", color=Color.dark_grey())
        e.title=(f"{self._config.general['name']} is Rich!")
        e.description=(f"{self._config.general['name']} can't store any more money!\n turning off gold pickup.")
        e.set_thumbnail(url=f"{self._psnURL}6L341955.png")
        self._send_embed(e, self._webhook)

    def send_message(self, msg: str, no_thumbnail=False):
        player_summary = self._config.general['player_summary']
        msg = f"{player_summary} {msg}" if player_summary is not None else msg
        e = discord.Embed(title=self._config.general['name'], description=f"```{msg}```", color=Color.dark_teal())
        if not no_thumbnail and not self._config.general['discord_status_condensed']:
            e.set_thumbnail(url=f"{self._psnURL}36L4a4994.png")
        self._send_embed(e, self._webhook)

    def _send_embed(self, e, webhook, file = None):
        if self._config.active_branch:
            e.set_footer(text=f'MyBot, branch: {self._config.active_branch}, commit: {self._config.latest_commit_sha[:7]}')
        else:
            e.set_footer(text=f'MyBot, v{__version__}')
        e.timestamp=datetime.datetime.now(datetime.timezone.utc)
        try:
            webhook.send(embed=e, file=file, username=self._config.general['name'])
        except BaseException as err:
            Logger.error("Error sending Discord embed: " + str(err))

    def _get_Item_Color(self, item):
        if "magic_" in item:
            return Color.blue()
        elif "set_" in item:
            return Color.green()
        elif "rune_" in item:
            return Color.dark_gold()
        elif "uniq_" in item or "rare" in item:
            return Color.gold()
        elif "gray_" in item:
            return Color.darker_grey()
        else:
            return Color.blue()

    def _add_file(self, image_path, image_name):
        try: 
            return discord.File(image_path, filename=image_name)
        except:
            traceback.print_exc()
            return discord.File("./assets/error/image_not_found.png", filename=image_name)
