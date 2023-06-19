"""Managing the configuration for the randomizer."""
#  Copyright 2020-2023 Capypara and the SkyTemple Contributors
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
import json
import os
import sys
import time
from enum import Enum
from numbers import Number
from typing import TypedDict, Optional, List, Dict

import pkg_resources
from jsonschema import validate
from range_typed_integers import u16, u8, u32

from skytemple_files.common.util import open_utf8
from skytemple_files.patch.handler.disarm_one_room_mh import DisarmOneRoomMHPatchHandler
from skytemple_files.patch.handler.fix_memory_softlock import FixMemorySoftlockPatchHandler
from skytemple_files.patch.handler.move_shortcuts import MoveShortcutsPatch
from skytemple_files.patch.handler.unused_dungeon_chance import UnusedDungeonChancePatch

from skytemple_randomizer.lists import DEFAULTMONSTERPOOL

CLASSREF = '__classref'

class Global:
    main_builder = None


class IntRange:
    """Represents a config integer with a minimum and maximum value (defined in the UI)"""
    value: int

    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return f"{self.value}"


class StartersNpcsConfig(TypedDict):
    starters: bool
    npcs: bool  # and bosses
    topmenu_music: bool
    overworld_music: bool
    explorer_rank_unlocks: bool
    explorer_rank_rewards: bool
    native_file_handlers: bool


class StartersNpcsConfigDoc:
    starters = \
        """If enabled, starter and partner choices are randomized between all available Pokémon."""
    npcs = \
        """If enabled all NPCs are randomized and all mentions of them in the script*. 
        Additionally the following things are also randomized with these new NPCs:
          - Boss fights
          - Guest Pokémon
          - Special Episode Player Characters
        
        *: Some additional text in the game may also be affected (eg. some item names)."""
    topmenu_music = \
        """If enabled, the music that plays on the titlescreen is randomized."""
    overworld_music = \
        """If enabled, the music that plays outside of dungeons is randomized (for the most part)."""
    explorer_rank_unlocks = \
        """If enabled, Explorer Rank Levels are randomly unlocked. The cap for Master Rank unlock is max. 200000 points."""
    explorer_rank_rewards = \
        """If enabled, Explorer Ranks give random items as rewards upon unlocking a new level."""
    native_file_handlers = \
        """If enabled, the randomizer uses faster implementations to manipulate the files in the ROM. 
        This can affect the random values rolled during the randomization. 
        
        This should only be disabled if you run into issues."""


class DungeonModeConfig(Enum):
    FULLY_RANDOM = 0
    GROUPED_BY_DUNGEON = 1


class DungeonSettingsConfig(TypedDict):
    randomize: bool
    unlock: bool
    randomize_weather: bool
    monster_houses: bool
    enemy_iq: bool


class DungeonsConfig(TypedDict):
    mode: DungeonModeConfig
    layouts: bool
    weather: bool
    items: bool
    pokemon: bool
    traps: bool
    min_floor_change_percent: IntRange
    max_floor_change_percent: IntRange
    fixed_rooms: bool
    max_sticky_chance: IntRange
    max_mh_chance: IntRange
    max_hs_chance: IntRange
    max_ks_chance: IntRange
    random_weather_chance: IntRange
    settings: Dict[int, DungeonSettingsConfig]
    items_enabled: List[int]


class DungeonsConfigDoc:
    mode = \
        """Specify if you want to randomize dungeon floors fully random or if you want to have some aspects of floors in a dungeon the same.\n
        If you choose "Keep floors in a dungeon similar" aspects like the music and tileset will be the same for all floors of a dungeon."""
    layouts = \
        """Whether or not to randomize general aspects of the dungeon's layout. This also includes tileset and music and most general settings."""
    weather = \
        """Whether or not to randomize weather."""
    items = \
        """Whether or not to randomize items on the floor, in shops, in monster houses and buried."""
    pokemon = \
        """Whether or not to randomize Pokémon spawns. 
        Levels of Pokémon on a floor are randomized to be -/+3 of the original game's weakest/strongest Pokémon on the floor."""
    traps = \
        """Whether or not to randomize traps and Wonder Tile spawn chances."""
    min_floor_change_percent = \
        """Maximum amount of change in floor count in the lower direction 
        (eg. if this is 10%, a dungeon can have up to 10% less floors). 
        A dungeon will never have less than 1 floor.
        This setting has no effect if layouts are not randomized."""
    max_floor_change_percent = \
        """Maximum amount of change in floor count in the upper direction 
        (eg. if this is 10%, a dungeon can have up to 10% more floors). 
        A dungeon will never have more than 99 floors.
        This setting has no effect if layouts are not randomized."""
    fixed_rooms = \
        """Whether or not to replace all boss fight rooms with randomly generated room layouts.
        
        THIS MAY BE UNBALANCED OR UNSTABLE."""
    max_sticky_chance = \
        """Sticky item chance will be randomized between 0% and this value (inclusive)."""
    max_mh_chance = \
        """Monster house chance will be randomized between 0% and this value (inclusive)."""
    max_hs_chance = \
        """Hidden stairs chance will be randomized between 0% and this value (inclusive)."""
    max_ks_chance = \
        """Kecleon shop chance will be randomized between 0% and this value (inclusive)."""
    random_weather_chance = \
        """Chance of applying a random weather that isn't "clear" to each floor. If the chance doesn't pass, "clear" weather will be used instead."""
    settings = \
        """Here you can decide which dungeons you want to have affected by the randomization and whether or randomize weather or not.
        You can also disable Monster Houses for dungeons (recommended for early game). Additionally you can force dungeons to be unlocked. 
        Please note that entering story dungeons prematurely can mess with the game's story progression."""
    items_enabled = \
        """Only these items will spawn on dungeon floors."""


class ImprovementsConfig(TypedDict):
    download_portraits: bool
    patch_moveshortcuts: bool
    patch_unuseddungeonchance: bool
    patch_totalteamcontrol: bool
    patch_disarm_monster_houses: bool
    patch_fixmemorysoftlock: bool


class ImprovementsConfigDoc:
    download_portraits = \
        """If enabled existing Pokémon portraits for starters and NPCs will be downloaded from https://sprites.pmdcollab.org.
        Additionally missing sprites for starters are downloaded."""
    patch_moveshortcuts = \
        f"""Installs the patch '{MoveShortcutsPatch().name}' by {MoveShortcutsPatch().author}: 
        {MoveShortcutsPatch().description}"""
    patch_unuseddungeonchance = \
        f"""Installs the patch '{UnusedDungeonChancePatch().name}' by {UnusedDungeonChancePatch().author}: 
        {UnusedDungeonChancePatch().description}"""
    patch_disarm_monster_houses = \
        f"""Installs the patch '{DisarmOneRoomMHPatchHandler().name}' by {DisarmOneRoomMHPatchHandler().author}: 
        {DisarmOneRoomMHPatchHandler().description}"""
    patch_totalteamcontrol = \
        f"""Installs patches that allow you to control your team members manually in dungeons. Press Start to toggle.
        Patch by Cipnit."""
    patch_fixmemorysoftlock = \
        f"""Installs the patch '{FixMemorySoftlockPatchHandler().name}' by {FixMemorySoftlockPatchHandler().author}: 
        {FixMemorySoftlockPatchHandler().description}"""


class QuizMode(Enum):
    TEST = 0
    TEST_AND_ASK = 1
    ASK = 2


QUIZ_QUESTIONS_JSON_SCHEMA = {
  "$schema": "http://json-schema.org/draft-07/schema",
  "type": "array",
  "items": {
    "type": "object",
    "required": [
      "question",
      "answers"
    ],
    "additionalProperties": False,
    "properties": {
      "question": {
        "type": "string"
      },
      "answers": {
        "minItems": 2,
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    }
  }
}


class QuizQuestion(TypedDict):
    question: str
    answers: List[str]


class QuizConfig(TypedDict):
    mode: QuizMode
    randomize: bool
    include_vanilla_questions: bool
    questions: List[QuizQuestion]


class QuizConfigDoc:
    mode = \
        f"""Change the behaviour of the hero starter selection in the personality test, using patches by an anonymous contributor. 
        You can select to have the test for selecting your starter (game default) or have an option to be able to select another starter after that or remove the test entirely. 
        Please note that if you selected any but the default option, you may not be able to remove it again if you randomize the ROM again."""
    randomize = \
        f"""If enabled, the personality quiz questions will be randomized using the qustions below. 
        Enter them as a list of YAML objects (see the examples). You need to define at least two answers, 2-4 answers will be randomly picked.
        If you pick "Select Manually" above, this is irrelevant as no quiz will be used.
        """
    include_vanilla_questions = \
        f"""If enabled, the questions from the base game will also be included in the pool of possible questions."""


class MovesetConfig(Enum):
    NO = 0
    FULLY_RANDOM = 1
    FIRST_DAMAGE = 2
    FIRST_STAB = 3


class MonsterConfig(TypedDict):
    iq_groups: bool
    abilities: bool
    typings: bool
    movesets: MovesetConfig
    tm_hm_movesets: bool
    tms_hms: bool
    abilities_enabled: List[int]
    monsters_enabled: List[u16]
    starters_enabled: List[u16]
    moves_enabled: List[u16]


class MonsterConfigDoc:
    iq_groups = \
        """Assigns all Pokémon in the game a random IQ group."""
    abilities = \
        """Assigns all Pokémon in the game a random ability from the "Random Abilities Pool"."""
    typings = \
        """Assigns all Pokémon one to two random types."""
    movesets = \
        """If enabled, assignes all Pokémon random level up movesets. You can control the properties of the starting move."""
    tm_hm_movesets = \
        """If enabled, assignes all Pokémon random TM/HM movesets."""
    tms_hms = \
        """If enabled, randomizes which moves TMs and HMs contain."""
    abilities_enabled = \
        """Only these abilities will be chosen, if abilities are randomized."""
    monsters_enabled = \
        """Only these Pokémon will be used for ANY randomization options in this randomizer."""
    starters_enabled = \
        """Only these Pokémon will be used for starter randomization options in this randomizer."""
    moves_enabled = \
        """Only these moves will be chosen, if moves are randomized."""


class LocationsConfig(TypedDict):
    randomize: bool
    first: str
    second: str


class LocationsConfigDoc:
    randomize = \
        """Replaces the names of the locations in the game with random combinations of words from "First Word" and "Second Word"."""


class ChaptersConfig(TypedDict):
    randomize: bool
    text: str


class ChaptersConfigDoc:
    randomize = \
        """Replaces the names of the chapters with random names from this list."""


class TextConfig(TypedDict):
    main: bool
    story: bool
    instant: bool


class TextConfigDoc:
    main = \
        """Randomize the game's main text file. This contains everything except for most of the overworld dialogue.
        The randomization is done in a way that (in most cases) similar categories of texts are shuffled, meaning for example, that Pokémon types and names are shuffled.
        
        THIS IS POTENTIALLY UNSTABLE AND COULD LEAD TO GAME CRASHES."""
    story = \
        """Randomize the game's overworld scene text. ALL overworld text is shuffled.
        
        THIS IS POTENTIALLY UNSTABLE AND COULD LEAD TO GAME CRASHES."""
    instant = \
        """If enabled, text will be displayed instantly."""


class IqConfig(TypedDict):
    randomize_tactics: bool
    randomize_iq_gain: bool
    randomize_iq_skills: bool
    randomize_iq_groups: bool
    keep_universal_skills: bool


class IqConfigDoc:
    randomize_tactics = \
        """If enabled, tactics are fully unlocked at random levels. One random tactic is available from the beginning."""
    randomize_iq_gain = \
        """If enabled, the amount of belly the gummies fill and the amount of IQ they give are fully random for each type."""
    randomize_iq_skills = \
        """If enabled, IQ skills are unlocked at random IQ amounts. Item Master is always unlocked."""
    randomize_iq_groups = \
        """If enabled, IQ skills are assigned to random IQ groups (but at least one). Item Master is always in all groups."""
    keep_universal_skills = \
        """If enabled, all skills that are included in all groups in the base game will also be added to all groups when randomizing\n.
        On top of that, even if "randomize IQ skill unlocks" is enabled, Course Checker, Item Catcher, Item Master, and Exclusive Move-User will always be unlocked from the start.
        However, Status Checker, Nontraitor, and Lava Evader will still have randomized IQ values."""


class ItemAlgorithm(Enum):
    BALANCED = 0
    CLASSIC = 1


class ItemConfig(TypedDict):
    algorithm: ItemAlgorithm
    global_items: bool
    weights: Dict[int, Number]


class ItemConfigDoc:
    algorithm = \
        """Controls how item lists are randomly filled.
        
        Balanced: Tries to make it equally likely to find any item in the game, 
        the only exception being Poké which is boosted.
        
        Classic: Algorithm that was used in the Randomizer prior to version 1.4.
        It doesn't attempt to balance out the different item categories, making items
        from categories with fewer total items easier to find.
        """
    global_items = \
        """If enabled, the Treasure Town shop item list, the dungeon reward item lists and all other global item lists are randomized."""
    weights = \
        """Controls weight biases when randomizing items. 
        A higher multiplier compared to other categories means that items from that category are more likely to spawn than others.
        
        This only applies to the 'Balanced' item algorithm!"""


class RandomizerConfig(TypedDict):
    """Configuration for the randomizer."""
    starters_npcs: StartersNpcsConfig
    dungeons: DungeonsConfig
    improvements: ImprovementsConfig
    pokemon: MonsterConfig
    locations: LocationsConfig
    chapters: ChaptersConfig
    text: TextConfig
    iq: IqConfig
    quiz: QuizConfig
    item: ItemConfig
    seed: str  # see get_effective_seed


class RandomizerConfigDoc:
    seed = \
        """This value is used to initialize the randomizer.
        If you use the same settings, seed and version of the randomizer you will get the same result.
        Leave empty for auto-generating seed."""


def get_effective_seed(seed: Optional[str]):
    """If the seed is empty, returns system time, otherwise tries to
    convert it into a number or returns it"""
    if seed is not None:
        seed = seed.strip()
    if seed is None or seed == "":
        return round(time.time())
    else:
        try:
            return int(seed)
        except ValueError:
            return seed


def is_int(typ):
    return typ == int or typ == u8 or typ == u16 or typ == u32


class ConfigFileLoader:
    """Loads configuration from JSON files. The JSON should have a structure equivalent of RandomizerConfig.
    Unknown fields are ignored, numbers converted into Enums."""
    @classmethod
    def load(cls, fn: str) -> RandomizerConfig:
        with open_utf8(fn) as f:
            return cls.load_from_dict(json.loads(f.read()))

    @classmethod
    def load_from_dict(cls, config: dict) -> RandomizerConfig:
        return cls._handle(config, RandomizerConfig)

    @classmethod
    def _handle(cls, target, typ: type):
        if hasattr(typ, '__bases__') and dict in typ.__bases__ and len(typ.__annotations__) > 0:
            if not isinstance(target, dict):
                raise ValueError(f"Value in JSON must be an object for {typ}.")
            kwargs = {}
            for field, field_type in typ.__annotations__.items():
                # Compatibility:
                if field in target:
                    if field == 'weather' and type(target[field]) == int:
                        target[field] = bool(target[field])
                else:
                    if field == 'overworld_music' and field_type == bool:
                        target[field] = True
                    elif field == 'patch_disarm_monster_houses' and field_type == bool:
                        target[field] = True
                    elif field == 'patch_totalteamcontrol' and field_type == bool:
                        target[field] = False
                    elif field == 'explorer_rank_unlocks' and field_type == bool:
                        target[field] = False
                    elif field == 'explorer_rank_rewards' and field_type == bool:
                        target[field] = True
                    elif field == 'randomize_tactics' and field_type == bool:
                        target[field] = False
                    elif field == 'randomize_iq_gain' and field_type == bool:
                        target[field] = False
                    elif field == 'randomize_iq_skills' and field_type == bool:
                        target[field] = False
                    elif field == 'randomize_iq_groups' and field_type == bool:
                        target[field] = False
                    elif field == 'patch_fixmemorysoftlock' and field_type == bool:
                        target[field] = True
                    elif field == 'tm_hm_movesets' and field_type == bool:
                        target[field] = True
                    elif field == 'tms_hms' and field_type == bool:
                        target[field] = True
                    elif field == 'max_sticky_chance':
                        target[field] = 10
                    elif field == 'max_mh_chance':
                        target[field] = 6
                    elif field == 'max_hs_chance':
                        target[field] = 10
                    elif field == 'max_ks_chance':
                        target[field] = 10
                    elif field == 'random_weather_chance':
                        target[field] = 33
                    elif field == 'min_floor_change_percent':
                        target[field] = 0
                    elif field == 'max_floor_change_percent':
                        target[field] = 0
                    elif field == 'instant':
                        target[field] = False
                    elif field == 'topmenu_music':
                        target[field] = True
                    elif field == 'items_enabled':
                        target[field] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 167, 168, 169, 170, 171, 172, 173, 174, 178, 179, 180, 182, 183, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 199, 200, 201, 202, 203, 204, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 220, 221, 222, 223, 225, 227, 228, 229, 230, 231, 232, 233, 234, 235, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 340, 341, 342, 343, 344, 346, 347, 348, 350, 351, 352, 354, 355, 356, 357, 358, 359, 362, 363]
                    elif field == 'moves_enabled':
                        target[field] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 360, 394, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541]
                    elif field == 'monsters_enabled':
                        target[field] = DEFAULTMONSTERPOOL
                    elif field == 'starters_enabled':
                        target[field] = DEFAULTMONSTERPOOL
                    elif field == 'quiz' and field_type == QuizConfig:
                        target[field] = {'mode': 1, 'randomize': False, 'questions': []}
                    elif field == 'native_file_handlers':
                        target[field] = 1
                    elif field == 'iq' and field_type == IqConfig:
                        target[field] = {
                            'randomize_tactics': False,
                            'randomize_iq_gain': False,
                            'randomize_iq_skills': False,
                            'randomize_iq_groups': False,
                            'keep_universal_skills': False
                        }
                    elif field == 'item' and field_type == ItemConfig:
                        target[field] = {
                            'algorithm': 0,
                            'global_items': True,
                            'weights': {
                                '0': 1,
                                '1': 1,
                                '2': 1,
                                '3': 2,
                                '4': 1,
                                '5': 0.3,
                                '6': 3,
                                '8': 1,
                                '9': 1,
                                '10': 1
                            }
                        }
                    elif field == 'include_vanilla_questions':
                        target[field] = False
                    else:
                        raise KeyError(f"Configuration '{field_type}' missing for {typ} ({field})).")
                kwargs[field] = cls._handle(target[field], field_type)
            v = typ(**kwargs)
            v[CLASSREF] = typ
            return v
        elif hasattr(typ, '__bases__') and Enum in typ.__bases__:
            if isinstance(target, str):
                try:
                    target = int(target)
                except ValueError:
                    pass
            if not isinstance(target, int):
                raise ValueError(f"Value in JSON must be an integer for {typ}.")
            return typ(target)
        elif typ == bool:
            if not isinstance(target, bool):
                raise ValueError(f"Expected a boolean for a field, but got {target.__class__.__name__}")
            return target
        elif is_int(typ):
            if not isinstance(target, int):
                raise ValueError(f"Expected an integer for a field, but got {target.__class__.__name__}")
            return target
        elif typ == IntRange:
            if not isinstance(target, int):
                raise ValueError(f"Expected an IntRange for a field, but got {target.__class__.__name__}")
            return typ(target)
        elif typ == str:
            if not isinstance(target, str):
                raise ValueError(f"Expected a string for a field, but got {target.__class__.__name__}")
            return target
        elif typ == Dict[int, DungeonSettingsConfig]:
            if not isinstance(target, dict):
                raise ValueError(f"Value in JSON must be an object for {typ}.")
            d = {}
            for idx, conf in target.items():
                d[int(idx)] = cls._handle(conf, DungeonSettingsConfig)
            return d
        elif typ == Dict[int, Number]:
            if not isinstance(target, dict):
                raise ValueError(f"Value in JSON must be an object for {typ}.")
            d = {}
            for idx, conf in target.items():
                d[int(idx)] = conf
            return d
        elif typ.__name__.lower() == "list" and is_int(typ.__args__[0]):  # type: ignore
            if not isinstance(target, list) or not all(isinstance(x, int) for x in target):
                raise ValueError(f"Value in JSON must be a list of integers for {typ}.")
            return target
        elif typ == List[QuizQuestion]:
            validate(target, QUIZ_QUESTIONS_JSON_SCHEMA)
            return target
        else:
            raise TypeError(f"Unknown type for {cls.__name__}: {typ}")


class EnumJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, IntRange):
            return obj.value
        return json.JSONEncoder.default(self, obj)


def version():
    try:
        return pkg_resources.get_distribution("skytemple-randomizer").version.strip()
    except pkg_resources.DistributionNotFound:
        # Try reading from a VERISON file instead
        version_file = os.path.join(data_dir(), 'VERSION')
        if os.path.exists(version_file):
            with open(version_file) as f:
                return f.read().strip()
        return 'unknown'


def data_dir():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'data')
    return os.path.join(os.path.dirname(__file__), 'data')
