"""Forked from SkyTemple."""

#  Copyright 2020-2024 Capypara and the SkyTemple Contributors
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
from __future__ import annotations

import locale
from enum import Enum, auto

from ndspy.rom import NintendoDSRom
from skytemple_files.common.ppmdu_config.data import (
    Pmd2Language,
    Pmd2StringBlock,
    Pmd2Data,
)
from skytemple_files.common.types.file_types import FileType


class StringType(Enum):
    """This enum maps to entries from the Pmd2StringBlock of the Pmd2Data's Pmd2StringIndexData."""

    ITEM_NAMES = auto(), "Item Names"
    MOVE_NAMES = auto(), "Move Names"
    POKEMON_NAMES = auto(), "Pokemon Names"
    POKEMON_CATEGORIES = auto(), "Pokemon Categories"
    MOVE_DESCRIPTIONS = auto(), "Move Descriptions"
    ITEM_LONG_DESCRIPTIONS = auto(), "Item Long Descriptions"
    ITEM_SHORT_DESCRIPTIONS = auto(), "Item Short Descriptions"
    TRAP_NAMES = auto(), "Trap Names"
    TYPE_NAMES = auto(), "Type Names"
    ABILITY_NAMES = auto(), "Ability Names"
    ABILITY_DESCRIPTIONS = auto(), "Ability Descriptions"
    PORTRAIT_NAMES = auto(), "Portrait Names"
    GROUND_MAP_NAMES = auto(), "Ground Map Names"
    DUNGEON_NAMES_MAIN = auto(), "Dungeon Names (Main)"
    DUNGEON_NAMES_SELECTION = auto(), "Dungeon Names (Selection)"
    DUNGEON_NAMES_SET_DUNGEON_BANNER = auto(), "Dungeon Names (SetDungeonBanner)"
    DUNGEON_NAMES_BANNER = auto(), "Dungeon Names (Banner)"
    DEFAULT_TEAM_NAMES = auto(), "Default Team Names"
    RANK_NAMES = auto(), "Explorer Ranks Names"
    DIALOGUE_LEVEL_UP = auto(), "Pokemon LEVEL_UP Dialogue"
    DIALOGUE_WAIT = auto(), "Pokemon WAIT Dialogue"
    DIALOGUE_HEALTHY = auto(), "Pokemon HEALTHY Dialogue"
    DIALOGUE_HALF_LIFE = auto(), "Pokemon HALF_LIFE Dialogue"
    DIALOGUE_PINCH = auto(), "Pokemon PINCH Dialogue"
    DIALOGUE_GROUND_WAIT = auto(), "Pokemon GROUND_WAIT Dialogue"
    WEATHER_NAMES = auto(), "Weather Names"
    TACTICS_NAMES = auto(), "Tactics Names"
    IQ_SKILL_NAMES = auto(), "IQ Skills Names"

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, xml_name: str | None = None):
        self._xml_name_ = xml_name

    def __str__(self):
        return self._xml_name_

    def __repr__(self):
        return f"StringType.{self.name}"

    @property
    def xml_name(self):
        return self._xml_name_

    def replace_xml_name(self, new_name):
        self._xml_name_ = new_name


MESSAGE_DIR = "MESSAGE"


class StringProvider:
    """
    StringProvider. Provides strings from the big string table(s).
    """

    def __init__(self, rom: NintendoDSRom, static_data: Pmd2Data):
        self.static_data = static_data
        self.model = FileType.STR.deserialize(
            rom.getFileByName(f"{MESSAGE_DIR}/{self._get_locale_from_app_locale().filename}"),
            string_encoding=self.static_data.string_encoding,
        )

    def get_value(
        self,
        string_type: StringType,
        index: int,
    ) -> str:
        """
        Returns the value of a string in the big string file for the given language, starting from the offset
        defined by the string_type.
        If language is not set, the default ROM language is used.
        """
        return self.model.strings[self.get_index(string_type, index)]

    def get_index(self, string_type: StringType, index: int) -> int:
        """
        Returns the index of a string in the big string file for the given language, starting from the offset
        defined by the string_type.
        If language is not set, the default ROM language is used.
        """
        # TODO: We should probably also check the end offset (overflow check).
        return self._get_string_block(string_type).begin + index

    def get_all(self, string_type: StringType) -> list[str]:
        """
        Returns all strings of the given type.
        If language is not set, the default ROM language is used.
        """
        string_block = self._get_string_block(string_type)
        return self.model.strings[string_block.begin : string_block.end]

    def get_languages(self) -> list[Pmd2Language]:
        """Returns all supported languages."""
        return self.static_data.string_index_data.languages

    def _get_string_block(self, string_type: StringType) -> Pmd2StringBlock:
        string_index_data = self.static_data.string_index_data

        if string_type.xml_name not in string_index_data.string_blocks:
            raise ValueError(f"String mapping for {string_type} not found.")

        return string_index_data.string_blocks[string_type.xml_name]

    def _get_locale_from_app_locale(self) -> Pmd2Language:
        try:
            current_locale = locale.getlocale()[0].split("_")[0]  # type: ignore
            for lang in self.get_languages():
                lang_locale = lang.locale.split("-")[0]
                if lang_locale == current_locale:
                    return lang
            return self.get_languages()[0]
        except Exception:
            return self.get_languages()[0]
