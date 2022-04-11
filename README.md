# <img src="assets/docs/header.png" width="370">

MyBot is memory-reading bot for Diablo 2 Resurrected. This is was originally built by integrating MapAssist with Botty, however most of the original pixel-based Botty code has been removed/rewritten, or is in the process of being removed.

[CHANGELOG.md](CHANGELOG.md) 

| Run | Status | Builds (\* Requires Enigma) |
| ------------------ | ------------------ |----------------------------------------------------------------------------|
| Countess | Good | Hammerdin\*, Zerker Barb\*
| Pit | Good (only champs/uniques) | Hammerdin\*, Zerker Barb\*
| Andariel | Good | Hammerdin\*, Zerker Barb\*
| Summoner | Good | Hammerdin\*, Zerker Barb\*
| Travincal | Good | Hammerdin, Zerker Barb\*
| Mephisto | Good | Hammerdin\*, Zerker Barb\*
| Diablo | Broken (being rewritten) |
| Eldritch | Good | Hammerdin, Zerker Barb
| Shenk | Good | Hammerdin, Zerker Barb\*
| Pindleskin | Good | Hammerdin, Zerker Barb
| Nihlathak | Good | Hammerdin\*, Zerker Barb\*
| Baal | Good | Hammerdin\*, Zerker Barb\*



| [general]                | Descriptions              |
| --------------------     | --------------------------|
| name                     | Name used in terminal and discord messages |
| custom_message_hook      | Add your own message hook here to get messages about drops and MyBot status updates, discord webhook is default  |
| logger_lvl               | Can be any of [info, debug] and determines how much output you see on the command line |
| max_game_length_s        | MyBot will attempt to stop whatever its doing and try to restart a new game. Note if this fails, MyBot will attempt to shut down D2R and Bnet     |
| max_consecutive_fails    | MyBot will stop making games if the number of consecutive fails reaches this max value     |
| randomize_runs           | 0: the order will be as seen in the params.ini. 1: the order will be random |
| difficulty               | Set to `normal` `nightmare` or `hell` for game difficulty |
| message_api_type         | Which api to use to send MyBot messages.  Supports "generic_api" (basic discord), or "discord" (discord embeds with images).
| discord_status_count     | Number of games between discord status messges being sent. Leave empty for no status reports.
| discord_status_condensed | Toggles condensed view of Discord status messages. 0 Full text, 1 Condensed text.
| discord_experience_report | If 1, your character experience report will be included in your Discord status messages
| info_screenshots         | If 1, the bot takes a screenshot with timestamp on every stuck / chicken / timeout / inventory full event. This is 1 by Default, so remember to clean up the folder every once in a while |
| loot_screenshots         | If 1, the bot takes a screenshot with timestamp everytime he presses show_items button and saves it to loot_screenshots folder. Remember to clear them once in a while... |
| saved_games_folder       | Optional folder path of Diablo 2 : Ressurrected saved games that will be used to overwrite when running the "auto settings" |
| d2r_path                 | Optional path to find the d2r.exe, if not set will be default to "C:\Program Files (x86)\Diablo II Resurrected\D2R.exe" when attempting to restart |
| restart_d2r_when_stuck   | Set to `1` and MyBot will attempt to restart d2r in the case that MyBot is unable to recover its state (e.g: game crash) |

| [routes]     | Descriptions                                                             |
| ------------ | ------------------------------------------------------------------------ |
| run_travincal     | Run Trav in each new game. Select "1" to run it "0" to leave it out. Specific trav gear is suggested |
| run_pindleskin   | Run Pindle in each new game. Select "1" to run it "0" to leave it out.   |
| run_eldritch | Run Eldritch in each new game. Select "1" to run it "0" to leave it out. |
| run_shenk    | Run shenk in each new game. Select "1" to run it "0" to leave it out.    |
| run_nihlathak | Run Nihlathak in each new game. Select "1" to run it "0" to leave it out. (Teleport required) |
| run_summoner   | Run Arcane Sanctuary in each new game. Select "1" to run it "0" to leave it out. (Teleport required) |
| run_diablo   | Run Diablo (just the Boss, not the trashmobs) in each new game. Select "1" to run it "0" to leave it out. (Teleport required) |

| [char]             | Descriptions |
| ------------------ | -------------------------------------------------------------------------------------------------|
| type               | Build type. Currently only "sorceress" or "hammerdin" is supported |
| casting_frames     | Depending on your char and fcr you will have a specific casting frame count. Check it here: https://diablo2.diablowiki.net/Breakpoints and fill in the right number. Determines how much delay there is after each teleport for example. If your system has some delay e.g. on vms, you might have to increase this value above the suggest value in the table! |
| num_loot_columns   | Number of columns in inventory used for loot (from left!). Remaining space can be used for charms |
| show_items         | Hotkey for "show items" |
| inventory_screen   | Hotkey to open inventory |
| force_move         | Hotkey for "force move" |
| stand_still        | Hotkey for "stand still". Note this can not be the default shift key as it would interfere with the merc healing routine |
| tp                 | Hotkey for using a town |
| belt_rows          | Integer value of how many rows the char's belt has |
| show_belt          | Hotkey for "show belt" |
| potion1            | Hotkey to take potion in slot 1 |
| potion2            | Hotkey to take potion in slot 2 |
| potion3            | Hotkey to take potion in slot 3 |
| potion4            | Hotkey to take potion in slot 4 |
| cta_available      | 0: no cta available, 1: cta is available and should be used during prebuff |
| weapon_switch      | Hotkey for "weapon switch" (only needed if cta_available=1) |
| battle_order       | Hotkey for battle order from cta (only needed if cta_available=1) |
| battle_command     | Hotkey for battle command from cta (only needed if cta_available=1) |
| stash_gold         | Bool value to stash gold each time when stashing items |
| start_gold_pickup_below | Start gold pickup below a certain amount (personal stash + inventory) (set to 0 to always use your pickit setting) |
| stop_gold_pickup_above | Stop gold pickup above a certain amount (personal stash + inventory) (set to 0 to always use your pickit setting) |
| gold_trav_only     | Hacky config that will restrict gold pickup to trav only. misc_gold must be set to 1 for this to have any effect |
| use_merc           | Set to 1 for using merc. Set to 0 for not using merc (will not revive merc when dead), default = 1 |
| atk_len_arc        | Attack length for hdin/sorc fighting arcane  |
| atk_len_trav       | Attack length for hdin fighting trav (note this atk length will be applied in 4 different spots each) |
| atk_len_pindle     | Attack length for hdin or number of attack sequences for sorc when fighting pindle |
| atk_len_eldritch   | Attack length for hdin or number of attack sequences for sorc when fighting eldritch |
| atk_len_shenk      | Attack length for hdin or number of attack sequences for sorc when fighting shenk |
| atk_len_nihlathak   | Attack length for hdin or number of attack sequences for sorc when fighting nihlathak |
| atk_len_cs_trashmobs   | Attack length for hdin or number of attack sequences when fighting Trash Mobs in Chaos Sanctuary (Diablo) |
| atk_len_diablo_vizier   | Attack length for hdin or number of attack sequences when fighting Sealboss A "Vizier of Chaos" in Chaos Sanctuary (Diablo) |
| atk_len_diablo_deseis   | Attack length for hdin or number of attack sequences when fighting Sealboss B "Lord De Seis" in Chaos Sanctuary (Diablo) |
| atk_len_diablo_infector   | Attack length for hdin or number of attack sequences when fighting Sealboss C "Infector of Souls" in Chaos Sanctuary (Diablo) |
| atk_len_diablo_infector   | Attack length for hdin or number of attack sequences when fighting Diablo in Chaos Sanctuary |
| cs_clear_trash   | If 1, most Trash mob packs from Chaos Sancturay Entrance to Pentagram and Seals A, B, C are cleared (NOT YET IMPLEMENTED). If 0, the run starts at Pentagram and just kills Sealbosses & Diablo |
| take_health_potion | Health percentage when healing potion will be used. e.g. 0.6 = 60% helath |
| take_mana_potion   | Mana percentage when mana potion will be used |
| take_rejuv_potion_health | Health percentag when rejuv potion will be used |
| take_rejuv_potion_mana   | Mana percentag when rejuv potion will be used |
| heal_merc          | Merc health percentage when giving healing potion to merc |
| heal_rejuv_merc    | Merc health percentage when giving rejuv potion to merc |
| chicken            | Will chicken (leave game) when player health percentage drops below set value, range 0 to 1. Set to 0 to not chicken. |
| merc_chicken       | Will chicken (leave game) when merc health percentage drops below set value, range 0 to 1. Set to 0 to not chicken. |
| belt_rejuv_columns | Number of belt columns for rejuv potions |
| belt_hp_columns    | Number of belt columns for healing potions |
| belt_mp_columns    | Number of belt columns for mana potions |
| pre_buff_every_run | 0: Will only prebuff on first run, 1: Will prebuff after each run/boss |
| runs_per_repair    | 0: Will only repair when needed, 1+: Will repair after # of runs set here |
| id_items           | Will identify items at cain before stashing them. Cain must be rescued for this to work.|
| open_chests        | Open up chests in some places. E.g. on dead ends of arcane. Note: currently bad runtime. |
| fill_shared_stash_first | Fill stash tabs starting from right to left, filling personal stash last |
| gamble_items       | List of items to gamble when stash fills with gold. Leave blank to disable. Supported items currently include circlet, ring, coronet, talon, amulet

| [transmute]             | Descriptions |
| ------------------ | -------------------------------------------------------------------------------------------------|
| transmute_every_x_game               | How often to run transmute routine (currently transmutes flawless gems into perfect gems). Transmute routine depends on stashing routine it will only start after items stashing is done. E.g. so it could take more than X games to perform transmutes if there were no items to stash at the time. Default: 20  |
| stash_destination | Stash tabs by priority to place the results of the transmute. Default: 3,2,1,0. (It means the result will be first placed in stash 3 untils it's full, then to stash 2, etc. 0 - personal tab)
=======
| chicken_nihlathak_conviction | Chicken if Nihlathak has conviction |
| chicken_if_dolls | Chicken if dolls are detected in the Throne of Destruction |
| chicken_if_souls | Chicken if souls are detected in the Throne of Destruction |
| send_throne_leecher_tp | Will put a TP in the corner of the Throne of Destruction for leechers |

### Builds
| [sorceress]   | Descriptions                                                                  |
| ------------- | ----------------------------------------------------------------------------- |
| teleport      | Required Hotkey for teleport                                                  |
| frozen_armor  | Optional Hotkey for frozen armor (or any of the other armors)                 |
| energy_shield | Optional Hotkey for energy shield                                             |
| thunder_storm | Optional Hotkey for thunder storm                                             |

| [light_sorc]  | Descriptions                                                                  |
| ------------- | ----------------------------------------------------------------------------- |
| chain_lightning | Optional Hotkey for chain_lightning (must be bound to left skill)           |
| lightning     | Required Hotkey for lightning (must be bound to right skill)                  |

| [blizz_sorc]  | Descriptions                                                                  |
| ------------- | ----------------------------------------------------------------------------- |
| ice_blast     | Optional Hotkey for ice_blast (must be bound to left skill)                   |
| blizzard      | Required Hotkey for Blizzard (must be bound to right skill)                   |

| [nova_sorc]   | Descriptions                                                                  |
| ------------- | ----------------------------------------------------------------------------- |
| nova          | Required Hotkey for Nova (must be bound to right skill)                       |

| [hammerdin]    | Descriptions                                                                        |
| -------------- | ----------------------------------------------------------------------------------- |
| teleport       | Optional Hotkey for teleport. If left empty hammerdin will run instead of teleport. |
| concentration  | Required Hotkey for Concentration                                                   |
| holy_shield    | Required Hotkey for Holy Shield                                                     |
| blessed_hammer | Required Hotkey for Blessed Hammer. (must be bound to left skill!)                  |
| redemption     | Optional Hotkey for Redemption                                                      |
| vigor          | Optional Hotkey for Vigor                                                           |
| cleansing      | Optional Hotkey for Cleansing                                                       |

| [trapsin]    | Descriptions                                                                          |
| -------------- | ----------------------------------------------------------------------------------- |
| teleport       | Optional Hotkey for teleport. If left empty trapsin will run instead of teleport.   |
| skill_left     | Optional Hotkey for Left Skill                                                      |
| burst_of_speed | Optional Hotkey for Burst of Speed                                                  |
| fade           | Optional Hotkey for Fade                                                            |
| shadow_warrior | Optional Hotkey for Shadow Warrior                                                  |
| lightning_sentry | Required Hotkey for Lightning Sentry                                              |
| death_sentry   | Required Hotkey for Death Sentry                                                    |

| [barbarian]    | Descriptions                                                                        |
| -------------- | ----------------------------------------------------------------------------------- |
| teleport       | Optional Hotkey for teleport. If left empty barb will run instead of teleport.      |
| leap           | Required Hotkey for Leap                                                            |
| shout          | Required Hotkey for Shout                                                           |
| war_cry        | Required Hotkey for War Cry                                                         |
| find_item      | Optional Hotkey for Find Item                                                       |
| cry_frequency  | Time in seconds between each cast of war_cry. Set to 0.0 if max fcr should be used  |

| [Necro]        | Descriptions                                                                        |
| -------------- | ----------------------------------------------------------------------------------- |
| teleport       | leave this blank for now, teleport/static pathing is currently not supported        |
| skill_left     | Required Hotkey for attack (bonespear/teeth)                                        |
| bone_armor     | Required Hotkey for Bone Armor                                                      |
| clay_golem     | Required Hotkey for Clay Golem                                                      |
| raise_skeleton | Required Hotkey for Raise Skeleton                                                  |
| amp_dmg        | Required Hotkey for Amplify Damage                                                  |
| corpse_explosion | Required Hotkey Corpse Explosion                                                  |
| raise_revive   | Required Hotkey revive                                                              |
| clear_pindle_packs | clears mobs before pindle                                                       |

| [dclone]             | Descriptions                                                          |
| -------------------- | --------------------------------------------------------------------- |
| region_ips           | Start of the region ip you want to filter for. e.g. EU Server = 37.244.11, 37.244.48 |
| dclone_hotip         | Hot ip you are looking for. MyBot will stay in game and message you if a message_hook is set |

| [advanced_options]   | Descriptions                                                          |
| -------------------- | --------------------------------------------------------------------- |
| pathing_delay_factor | A linear scaling factor, between 1 and 10, applied to pathing delays. |
| message_headers      | Headers that are sent with each messages                              |
| message_body_template | Message body of the post message sent                                |
| obs_replay_recording_enabled | Set to 1 to enable recording during runs with [OBS] (requires [OBS](https://obsproject.com/) runnig w/ [obs-websocket](https://github.com/obsproject/obs-websocket) plugin, and [obs-cli](https://github.com/muesli/obs-cli) installed. |
| obs_debug_replays_enabled | Set to 1 to enable saving video replays for failed runs and other errors [OBS] (requires [OBS](https://obsproject.com/) runnig w/ [obs-websocket](https://github.com/obsproject/obs-websocket) plugin, and [obs-cli](https://github.com/muesli/obs-cli) installed. |
| obs_cli_path          | Required if either obs_run_recording_enabled or obs_replay_recording_enabled are 1, this is the path to obs-cli.exe () |

## Support this project

Support it by contributing in any technical way, giving feedback, bug reports or submitting PRs.
