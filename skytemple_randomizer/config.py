"""Managing the configuration for the randomizer."""
#  Copyright 2020-2021 Parakoopa and the SkyTemple Contributors
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
from typing import TypedDict, Optional, List, Dict

import pkg_resources

from skytemple_files.common.util import open_utf8
from skytemple_files.patch.handler.move_shortcuts import MoveShortcutsPatch
from skytemple_files.patch.handler.unused_dungeon_chance import UnusedDungeonChancePatch

CLASSREF = '__classref'


class Global:
    main_builder = None


class StartersNpcsConfig(TypedDict):
    starters: bool
    npcs: bool  # and bosses
    global_items: bool
    overworld_music: bool


class StartersNpcsConfigDoc:
    starters = \
        """If enabled, starter and partner choices are randomized between all available Pokémon."""
    npcs = \
        """If enabled all NPCs are randomized and all mentions of them in the script*. Additionally boss fights are also changed to use these new NPCs.
        
        *: Some additional text in the game may also be affected (eg. some item names)."""
    global_items = \
        """If enabled, the Treasure Town shop item list, the dungeon reward item lists and all other global item lists are randomized."""
    overworld_music = \
        """If enabled, the music that plays outside of dungeons is randomized (for the most part)."""


class DungeonModeConfig(Enum):
    FULLY_RANDOM = 0
    GROUPED_BY_DUNGEON = 1


class DungeonWeatherConfig(Enum):
    NO_RANDOMIZE = 0
    ONLY_RANDOM = 1
    SHUFFLED = 2
    SHUFFLED_LOWER_BAD_CHANCE = 3


class DungeonSettingsConfig(TypedDict):
    randomize: bool
    unlock: bool
    randomize_weather: bool
    monster_houses: bool
    enemy_iq: bool


class DungeonsConfig(TypedDict):
    mode: DungeonModeConfig
    layouts: bool
    weather: DungeonWeatherConfig
    items: bool
    pokemon: bool
    traps: bool
    fixed_rooms: bool
    settings: Dict[int, DungeonSettingsConfig]


class DungeonsConfigDoc:
    mode = \
        """Specify if you want to randomize dungeon floors fully random or if you want to have some aspects of floors in a dungeon the same.\n
        If you choose "Keep floors in a dungeon similar" aspects like the music and tileset will be the same for all floors of a dungeon."""
    layouts = \
        """Whether or not to randomize general aspects of the dungeon's layout. This also includes tileset and music and most general settings."""
    weather = \
        """Whether or not to randomize weather. You can choose to have harmful weather less option and you can also choose to have the game roll random weather, every time a floor is entered."""
    items = \
        """Whether or not to randomize items on the floor, in shops, in monster houses and buried."""
    pokemon = \
        """Whether or not to randomize Pokémon spawns. 
        Levels of Pokémon on a floor are randomized to be -/+3 of the original game's weakest/strongest Pokémon on the floor."""
    traps = \
        """Whether or not to randomize traps and Wonder Tile spawn chances."""
    fixed_rooms = \
        """Whether or not to replace all boss fight rooms with randomly generated room layouts.
        
        THIS MAY BE UNBALANCED OR UNSTABLE."""
    settings = \
        """Here you can decide which dungeons you want to have affected by the randomization and whether or randomize weather or not.
        You can also disable Monster Houses for dungeons (recommended for early game). Additionally you can force dungeons to be unlocked. 
        Please note that entering story dungeons prematurely can mess with the game's story progression."""


class PersonalityTestConfig(Enum):
    TEST = 0
    TEST_AND_ASK = 1
    ASK = 2


class ImprovementsConfig(TypedDict):
    download_portraits: bool
    patch_moveshortcuts: bool
    patch_unuseddungeonchance: bool
    patch_totalteamcontrol: bool
    personality_test: PersonalityTestConfig


class ImprovementsConfigDoc:
    download_portraits = \
        """If enabled existing Pokémon portraits for starters and NPCs will be downloaded from https://sprites.pmdcollab.org."""
    patch_moveshortcuts = \
        f"""Installs the patch '{MoveShortcutsPatch().name}' by {MoveShortcutsPatch().author}: 
        {MoveShortcutsPatch().description}"""
    patch_unuseddungeonchance = \
        f"""Installs the patch '{UnusedDungeonChancePatch().name}' by {UnusedDungeonChancePatch().author}: 
        {UnusedDungeonChancePatch().description}"""
    patch_totalteamcontrol = \
        f"""Installs patches that allow you to control your team members manually in dungeons. Press Start to toggle.
        Patch by Cipnit."""
    personality_test = \
        f"""Change the behaviour of the hero starter selection in the personality test, using patches by irdkwia. 
        You can select to have the test for selecting your starter (game default) or have an option to be able to select another starter after that or remove the test entirely. 
        Please note that if you selected any but the default option, you may not be able to remove it again if you randomize the ROM again."""


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
    ban_unowns: bool
    abilities_enabled: List[int]


class MonsterConfigDoc:
    iq_groups = \
        """Assigns all Pokémon in the game a random IQ group."""
    abilities = \
        """Assigns all Pokémon in the game a random ability from the "Random Abilities Pool"."""
    typings = \
        """Assigns all Pokémon one to two random types."""
    movesets = \
        """If enabled, assignes all Pokémon random TM/HM, egg move and level up movesets. You can control the properties of the starting move."""
    ban_unowns = \
        """If enabled, starters and NPCs will not randomize into Unowns and Unowns will not spawn in dungeons."""


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


class TextConfigDoc:
    main = \
        """Randomize the game's main text file. This contains everything except for most of the overworld dialogue.
        The randomization is done in a way that (in most cases) similar categories of texts are shuffled, meaning for example, that Pokémon types and names are shuffled.
        
        THIS IS POTENTIALLY UNSTABLE AND COULD LEAD TO GAME CRASHES."""
    story = \
        """Randomize the game's overworld scene text. ALL overworld text is shuffled.
        
        THIS IS POTENTIALLY UNSTABLE AND COULD LEAD TO GAME CRASHES."""


class RandomizerConfig(TypedDict):
    """Configuration for the randomizer."""
    starters_npcs: StartersNpcsConfig
    dungeons: DungeonsConfig
    improvements: ImprovementsConfig
    pokemon: MonsterConfig
    locations: LocationsConfig
    chapters: ChaptersConfig
    text: TextConfig
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
                if field not in target:
                    # Compatibility:
                    if field == 'global_items' and field_type == bool:
                        target[field] = True
                    elif field == 'overworld_music' and field_type == bool:
                        target[field] = True
                    elif field == 'patch_totalteamcontrol' and field_type == bool:
                        target[field] = False
                    elif field == 'personality_test':
                        target[field] = 1
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
        elif typ == int:
            if not isinstance(target, int):
                raise ValueError(f"Expected an integer for a field, but got {target.__class__.__name__}")
            return target
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
        elif typ == List[int]:
            if not isinstance(target, list) or not all(isinstance(x, int) for x in target):
                raise ValueError(f"Value in JSON must be a list of integers for {typ}.")
            return target
        else:
            raise TypeError(f"Unknown type for {cls.__name__}: {typ}")


class EnumJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
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
