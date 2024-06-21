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
import json
import os
from typing import TypedDict
from xml.etree import ElementTree

import click
from skytemple_files.common.i18n_util import _
from skytemple_files.common.ppmdu_config.xml_reader import XmlCombiner
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import (
    get_resources_dir,
    MONSTER_MD,
    get_binary_from_rom,
)
from skytemple_files.data.md.protocol import Ability
from skytemple_files.hardcoded.dungeons import HardcodedDungeons
from skytemple_files.patch.patches import Patcher

from skytemple_randomizer.frontend.cli import LoadedRom
from skytemple_randomizer.string_provider import StringProvider, StringType

ITEM_FILE = "BALANCE/item_p.bin"
WAZA_P = "BALANCE/waza_p.bin"


class InfoRom(TypedDict):
    edition: str


def info_rom(rom: LoadedRom):
    click.echo(json.dumps(InfoRom(edition=rom.static_data.game_edition)), nl=False)


def ppmdu_config():
    res_dir = os.path.join(get_resources_dir(), "ppmdu_config")
    file_names = [
        os.path.join(res_dir, "pmd2data.xml"),
        os.path.join(res_dir, "skytemple.xml"),
    ]

    roots = []
    for f in file_names:
        this_file_root = ElementTree.parse(f).getroot()
        for elem in this_file_root:
            if elem.tag == "External":
                filepath = os.path.join(os.path.dirname(f), elem.attrib["filepath"])
                this_file_root = (
                    XmlCombiner([this_file_root, ElementTree.parse(filepath).getroot()]).combine().getroot()
                )
        roots.append(this_file_root)
    root = XmlCombiner(roots).combine().getroot()
    click.echo(ElementTree.tostring(root, encoding="utf8"), nl=False)


def info_monsters(rom: LoadedRom):
    string_provider = StringProvider(rom.rom, rom.static_data)
    patcher = Patcher(rom.rom, rom.static_data)

    b_attr = "md_index_base"
    if is_applied(patcher, "ExpandPokeList"):
        b_attr = "entid"

    monster_md = FileType.MD.deserialize(rom.rom.getFileByName(MONSTER_MD))

    monster_bases = {}
    for entry in monster_md.entries:
        baseid = getattr(entry, b_attr)
        monster_bases[baseid] = string_provider.get_value(StringType.POKEMON_NAMES, baseid)

    click.echo(json.dumps(monster_bases), nl=False)


def info_items(rom: LoadedRom):
    string_provider = StringProvider(rom.rom, rom.static_data)

    item_p = FileType.ITEM_P.deserialize(rom.rom.getFileByName(ITEM_FILE))

    items = {}
    for i, entry in enumerate(item_p.item_list):
        items[i] = string_provider.get_value(StringType.ITEM_NAMES, i)

    click.echo(json.dumps(items), nl=False)


def info_moves(rom: LoadedRom):
    string_provider = StringProvider(rom.rom, rom.static_data)

    waza_p = FileType.WAZA_P.deserialize(rom.rom.getFileByName(WAZA_P))

    moves = {}
    for i, entry in enumerate(waza_p.moves):
        moves[i] = string_provider.get_value(StringType.MOVE_NAMES, i)

    click.echo(json.dumps(moves), nl=False)


def info_item_categories(rom: LoadedRom):
    cats = {}
    for i, entry in rom.static_data.dungeon_data.item_categories.items():
        # Skip irrelevant
        if i in [7, 11, 12, 13, 14, 15]:
            continue
        cats[i] = entry.name_localized

    click.echo(json.dumps(cats), nl=False)


def info_abilities(rom: LoadedRom):
    string_provider = StringProvider(rom.rom, rom.static_data)

    abilities = {}
    for ability in Ability:
        name = _("Unused") + f" 0x{ability.value:0x}"
        if ability.value < 124:
            name = string_provider.get_value(StringType.ABILITY_NAMES, ability.value)
        abilities[ability.value] = name

    click.echo(json.dumps(abilities), nl=False)


def info_dungeons(rom: LoadedRom):
    string_provider = StringProvider(rom.rom, rom.static_data)

    dungeon_list = HardcodedDungeons.get_dungeon_list(
        get_binary_from_rom(rom.rom, rom.static_data.bin_sections.arm9),
        rom.static_data,
    )

    dungeons = {}
    for i, dungeon in enumerate(dungeon_list):
        dungeons[i] = (
            string_provider.get_value(StringType.DUNGEON_NAMES_MAIN, i),
            string_provider.get_value(StringType.DUNGEON_NAMES_SELECTION, i),
        )

    click.echo(json.dumps(dungeons), nl=False)


def is_applied(patcher: Patcher, patch: str) -> bool:
    try:
        return patcher.is_applied(patch)
    except NotImplementedError:
        return False
