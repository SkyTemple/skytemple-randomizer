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
from random import sample, choice
from typing import List, Dict, Union, Tuple, Iterable

from skytemple_files.common.ppmdu_config.data import Pmd2Data, Pmd2Language
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_files_from_rom_with_extension
from skytemple_files.data.md.model import NUM_ENTITIES
from skytemple_files.data.str.model import Str
from skytemple_files.graphics.kao.model import SUBENTRIES, Kao, NintendoDSRom
from skytemple_randomizer.config import RandomizerConfig

ALLOWED_MD_IDS_BASE = set(x for x in range(1, 537) if x not in [383, 384])
UNOWN_IDS = set(range(201, 229))


def get_main_string_file(rom: NintendoDSRom, static_data: Pmd2Data) -> Tuple[Pmd2Language, Str]:
    lang = None
    for l in static_data.string_index_data.languages:
        if l.locale == 'en-US':
            lang = l
            break
    # If we didn't find english, just take the first
    if lang is None:
        lang = static_data.string_index_data.languages[0]
    return lang, FileType.STR.deserialize(rom.getFileByName(f'MESSAGE/{lang.filename}'))


def get_all_string_files(rom: NintendoDSRom, static_data: Pmd2Data) -> Iterable[Tuple[Pmd2Language, Str]]:
    for lang in static_data.string_index_data.languages:
        yield lang, FileType.STR.deserialize(rom.getFileByName(f'MESSAGE/{lang.filename}'))


def clone_missing_portraits(kao: Kao, index: int):
    """Fills all missing kao subindex slots for index with the first portrait."""
    cloned = kao.get(index, 0)
    # Skip mirrored slots.
    for i in range(2, SUBENTRIES, 2):
        if kao.get(index, i) is None:
            kao.set(index, i, cloned)


def get_allowed_md_ids(conf: RandomizerConfig, with_plus_600=False) -> List[int]:
    if conf['pokemon']['ban_unowns']:
        ents = ALLOWED_MD_IDS_BASE - UNOWN_IDS
    else:
        ents = ALLOWED_MD_IDS_BASE
    if with_plus_600:
        to_add = set()
        for ent in ents:
            if ent + NUM_ENTITIES <= 1154:
                to_add.add(ent + NUM_ENTITIES)
        ents.update(to_add)
    return list(ents)


def replace_strings(original: str, replacement_map: Dict[str, str]):
    """Replaces all strings from the replacement map in original and returns the new string"""
    string = original
    for old, new in replacement_map.items():
        string = string.replace(old, new)
    return string


def replace_text_main(string_file: Str, replace_map: Dict[str, str], start_idx, end_idx):
    new_strings = []
    for idx, string in enumerate(string_file.strings):
        if idx < start_idx or idx > end_idx:
            new_strings.append(replace_strings(string, replace_map))
        else:
            new_strings.append(string)
    string_file.strings = new_strings


def replace_text_script(rom: NintendoDSRom, static_data: Pmd2Data,
                        replace_map_lang: Dict[Pmd2Language, Dict[str, str]]):
    new_dict = {}
    for lang, replace_map in replace_map_lang.items():
        for a, b in replace_map.items():
            new_dict[a.upper()] = b.upper()
        replace_map.update(new_dict)
        for file_path in get_files_from_rom_with_extension(rom, 'ssb'):
            script = get_script(file_path, rom, static_data)
            script.constants = [replace_strings(string, replace_map) for string in script.constants]
            script.strings[lang.name.lower()] = [replace_strings(string, replace_map) for string in script.strings[lang.name.lower()]]


_ssb_file_cache = {}
def clear_script_cache():
    global _ssb_file_cache
    _ssb_file_cache = {}


def clear_script_cache_for(file_path):
    global _ssb_file_cache
    del _ssb_file_cache[file_path]


def get_script(file_path, rom, static_data):
    global _ssb_file_cache
    if file_path not in _ssb_file_cache:
        _ssb_file_cache[file_path] = FileType.SSB.deserialize(rom.getFileByName(file_path), static_data)
    return _ssb_file_cache[file_path]


def save_scripts(rom, static_data):
    for file_path, script in _ssb_file_cache.items():
        rom.setFileByName(file_path, FileType.SSB.serialize(script, static_data))


def ranks(sample):
    """
    Return the ranks of each element in an integer sample.
    """
    indices = sorted(range(len(sample)), key=lambda i: sample[i])
    return sorted(indices, key=lambda i: indices[i])


def sample_with_minimum_distance(n, k, d):
    """
    Sample of k elements from range(n), with a minimum distance d.
    """
    smpl = sample(range(n-(k-1)*(d-1)), k)
    return [s + (d-1)*r for s, r in zip(smpl, ranks(smpl))]


def random_txt_line(text: str):
    lines = text.splitlines()
    line = ""
    while line == "":
        line = choice(lines)
    return line.strip().replace('\\n', '\n')

