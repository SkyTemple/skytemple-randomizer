"""Managing the configuration for the randomizer."""
#  Copyright 2020 Parakoopa
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
import time
from enum import Enum
from typing import TypedDict, Optional, List, Dict

from gi.repository import Gtk

from skytemple_files.common.ppmdu_config.dungeon_data import Pmd2DungeonDungeon, Pmd2DungeonAbility
from skytemple_files.common.util import open_utf8

CLASSREF = '__classref'


class StartersNpcsConfig(TypedDict):
    starters: bool
    npcs: bool  # and bosses


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


class DungeonsConfig(TypedDict):
    mode: DungeonModeConfig
    layouts: bool
    weather: DungeonWeatherConfig
    items: bool
    pokemon: bool
    traps: bool
    fixed_rooms: bool
    settings: Dict[int, DungeonSettingsConfig]


class ImprovementsConfig(TypedDict):
    download_portraits: bool
    patch_moveshortcuts: bool
    patch_unuseddungeonchance: bool


class MovesetConfig(Enum):
    NO = 0
    FULLY_RANDOM = 1
    FIRST_DAMAGE = 2
    FIRST_STAB = 3


class MonsterConfig(TypedDict):
    iq_groups: bool
    abilities: bool
    typings: bool
    exp_required: bool
    movesets: MovesetConfig
    ban_unowns: bool
    abilities_enabled: List[int]


class LocationsConfig(TypedDict):
    randomize: bool
    first: str
    second: str


class ChaptersConfig(TypedDict):
    randomize: bool
    text: str


class TextConfig(TypedDict):
    main: bool
    story: bool


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


def get_effective_seed(seed: Optional[str]):
    """If the seed is empty, returns system time, otherwise tries to
    convert it into a number or returns the hash value"""
    if seed is not None:
        seed = seed.strip()
    if seed is None or seed == "":
        return round(time.time())
    else:
        try:
            return int(seed)
        except ValueError:
            return hash(seed)


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
                    raise KeyError(f"Configuration '{field_type}' missing for {typ}.")
                kwargs[field] = cls._handle(target[field], field_type)
            v = typ(**kwargs)
            v[CLASSREF] = typ
            return v
        elif hasattr(typ, '__bases__') and Enum in typ.__bases__:
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


class ConfigUIApplier:
    """Applies configuration to the UI widgets."""
    def __init__(self, builder: Gtk.Builder, dungeons: List[Pmd2DungeonDungeon], abilities: List[Pmd2DungeonAbility]):
        self.builder = builder
        self.dungeons = dungeons
        self.abilities = abilities

    def apply(self, config: RandomizerConfig):
        self._handle(config)

    def _handle(self, config, field_name=None):
        if isinstance(config, dict) and CLASSREF in config:
            typ = config[CLASSREF]
        else:
            typ = config.__class__
        if hasattr(typ, '__bases__') and dict in typ.__bases__ and len(typ.__annotations__) > 0:
            for field, field_type in typ.__annotations__.items():
                field_full = field
                if field_name is not None:
                    field_full = field_name + '_' + field
                self._handle(config[field], field_full)
        elif hasattr(typ, '__bases__') and Enum in typ.__bases__:
            self._handle(config.value, field_name)
        elif typ == bool:
            assert field_name, "Field name must be set for primitive"
            w: Gtk.Switch = self._ui_get('switch_' + field_name)
            w.set_active(config)
        elif typ == int:
            assert field_name, "Field name must be set for primitive"
            w: Gtk.ComboBox = self._ui_get('cb_' + field_name)
            w.set_active_id(str(config))
        elif typ == str:
            assert field_name, "Field name must be set for primitive"
            try:
                w: Gtk.Entry = self._ui_get('entry_' + field_name)
                w.set_text(config)
            except ValueError:
                w: Gtk.TextView = self._ui_get('text_' + field_name)
                w.get_buffer().set_text(config)
        elif typ == dict and len(config) > 0 and isinstance(next(iter(config.values())), dict):
            w: Gtk.TreeView = self._ui_get('tree_' + field_name)
            s: Gtk.ListStore = w.get_model()
            for idx, settings in config.items():
                settings: DungeonSettingsConfig
                s.append([idx, self._get_dungeon_name(idx), settings['randomize'], settings['monster_houses'],
                          settings['randomize_weather'], settings['unlock']])
        elif typ == list and (len(config) < 1 or isinstance(next(iter(config)), int)):
            w: Gtk.TreeView = self._ui_get('tree_' + field_name)
            s: Gtk.ListStore = w.get_model()
            for i in range(0, len(self.abilities)):
                s.append([i, self._get_ability_name(i), i in config])
        else:
            raise TypeError(f"Unknown type for {self.__class__.__name__}: {typ}")

    def _ui_get(self, n):
        w: Gtk.Switch = self.builder.get_object(n)
        if w is None:
            raise ValueError(f"UI element '{n}' not found.")
        return w

    def _get_dungeon_name(self, idx):
        return self.dungeons[idx].name

    def _get_ability_name(self, idx):
        return self.abilities[idx].name


class ConfigUIReader:
    """Loads configuration from the UI widgets."""
    def __init__(self, builder: Gtk.Builder):
        self.builder = builder

    def read(self) -> RandomizerConfig:
        return self._handle(RandomizerConfig)

    def _handle(self, typ: type, field_name=None):
        if hasattr(typ, '__bases__') and dict in typ.__bases__ and len(typ.__annotations__) > 0:
            d = {}
            for field, field_type in typ.__annotations__.items():
                field_full = field
                if field_name is not None:
                    field_full = field_name + '_' + field
                d[field] = self._handle(field_type, field_full)
            return d
        elif hasattr(typ, '__bases__') and Enum in typ.__bases__:
            return typ(self._handle(int, field_name))
        elif typ == bool:
            assert field_name, "Field name must be set for primitive"
            w: Gtk.Switch = self._ui_get('switch_' + field_name)
            return w.get_active()
        elif typ == int:
            assert field_name, "Field name must be set for primitive"
            w: Gtk.ComboBox = self._ui_get('cb_' + field_name)
            return int(w.get_active_id())
        elif typ == str:
            assert field_name, "Field name must be set for primitive"
            try:
                w: Gtk.Entry = self._ui_get('entry_' + field_name)
                return w.get_text()
            except ValueError:
                w: Gtk.TextView = self._ui_get('text_' + field_name)
                buffer = w.get_buffer()
                return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        elif typ == Dict[int, DungeonSettingsConfig]:
            w: Gtk.TreeView = self._ui_get('tree_' + field_name)
            s: Gtk.ListStore = w.get_model()
            d = {}
            for idx, name, randomize, monster_houses, randomize_weather, unlock in s:
                d[idx] = {'randomize': randomize, 'monster_houses': monster_houses,
                          'randomize_weather': randomize_weather, 'unlock': unlock}
            return d
        elif typ == List[int]:
            w: Gtk.TreeView = self._ui_get('tree_' + field_name)
            s: Gtk.ListStore = w.get_model()
            d = []
            for idx, name, use in s:
                if use:
                    d.append(idx)
            return d
        else:
            raise TypeError(f"Unknown type for {self.__name__}: {typ}")

    def _ui_get(self, n):
        w: Gtk.Switch = self.builder.get_object(n)
        if w is None:
            raise ValueError(f"UI element '{n}' not found.")
        return w


class EnumJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return json.JSONEncoder.default(self, obj)
