#  Copyright 2020-2021 Capypara and the SkyTemple Contributors
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
from enum import Enum, auto
from random import sample, choice
from typing import List, Dict, Union, Tuple, Iterable

from skytemple_files.common.ppmdu_config.data import Pmd2Data, Pmd2Language
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_files_from_rom_with_extension
from skytemple_files.data.md.model import NUM_ENTITIES, PokeType
from skytemple_files.data.str.model import Str
from skytemple_files.graphics.kao.model import SUBENTRIES, Kao, NintendoDSRom
from skytemple_randomizer.config import RandomizerConfig


DAMAGING_MOVES = {1, 2, 8, 9, 16, 18, 25, 28, 30, 31, 32, 36, 39, 41, 42, 44, 46, 52, 53, 57, 60, 62, 63, 64, 65, 67,
                  68, 69, 71, 72, 73, 75, 76, 77, 78, 80, 81, 82, 87, 90, 91, 92, 93, 96, 97, 100, 101, 103, 105, 107,
                  109, 110, 113, 114, 116, 118, 120, 121, 125, 126, 127, 129, 132, 133, 135, 136, 139, 140, 143, 144,
                  145, 147, 149, 151, 153, 154, 156, 157, 158, 159, 161, 162, 163, 164, 166, 167, 168, 174, 175, 176,
                  178, 179, 180, 182, 188, 189, 190, 193, 198, 200, 201, 203, 204, 205, 206, 207, 208, 210, 211, 213,
                  214, 219, 221, 222, 226, 228, 230, 234, 235, 238, 239, 240, 241, 242, 243, 244, 245, 246, 248, 250,
                  251, 253, 255, 260, 261, 262, 263, 264, 270, 271, 272, 275, 276, 278, 279, 280, 283, 285, 287, 289,
                  290, 291, 292, 297, 299, 300, 303, 306, 308, 309, 310, 311, 312, 314, 320, 321, 322, 323, 325, 331,
                  332, 335, 336, 342, 344, 345, 346, 347, 348, 350, 352, 353, 354, 430, 431, 432, 433, 435, 436, 437,
                  440, 441, 442, 443, 445, 446, 451, 452, 453, 454, 455, 457, 458, 459, 460, 461, 462, 463, 468, 469,
                  470, 471, 473, 474, 475, 476, 477, 479, 481, 484, 485, 486, 487, 488, 489, 490, 491, 494, 495, 497,
                  498, 500, 501, 502, 505, 507, 508, 510, 511, 512, 515, 516, 517, 518, 519, 521, 522, 523, 524, 527,
                  529, 530, 531, 533, 535, 536, 537, 538, 539, 541}
STAB_DICT = {
    PokeType.STEEL: {1, 103, 244, 325, 431, 475, 510, 523, 527, 536},
    PokeType.ICE: {2, 42, 97, 101, 180, 270, 344, 345, 461, 462, 535},
    PokeType.GROUND: {8, 118, 143, 213, 285, 289, 290, 299, 484, 501},
    PokeType.NORMAL: {9, 18, 25, 31, 39, 60, 67, 71, 78, 81, 96, 121, 125, 132, 139, 140, 145, 154, 161, 166, 168, 176,
                      190, 201, 203, 207, 226, 228, 235, 241, 242, 245, 248, 250, 260, 261, 263, 264, 271, 275, 287,
                      311, 312, 314, 321, 322, 347, 348, 352, 455, 457, 471, 474, 487, 497, 505, 516, 541},
    PokeType.WATER: {16, 32, 44, 69, 87, 113, 156, 158, 159, 219, 239, 240, 255, 308, 310, 432, 433, 469},
    PokeType.ROCK: {28, 30, 73, 93, 105, 350, 453, 481, 512, 533},
    PokeType.FLYING: {36, 57, 100, 153, 174, 178, 179, 205, 211, 353, 442, 446, 490, 518},
    PokeType.FIRE: {41, 52, 53, 149, 157, 230, 262, 272, 276, 278, 291, 292, 517, 519, 522, 524},
    PokeType.GHOST: {46, 120, 126, 127, 437, 451, 476, 477},
    PokeType.DARK: {62, 63, 167, 214, 436, 445, 488, 491, 515},
    PokeType.ELECTRIC: {64, 65, 129, 144, 188, 189, 193, 354, 452, 489, 521},
    PokeType.FIGHTING: {68, 72, 75, 77, 90, 92, 116, 136, 175, 204, 206, 210, 222, 243, 246, 300, 303, 430, 440, 454,
                        479, 500, 507, 508, 531},
    PokeType.GRASS: {76, 135, 151, 163, 182, 221, 238, 251, 253, 297, 320, 336, 441, 443, 458, 468, 486, 511, 537},
    PokeType.BUG: {80, 82, 114, 164, 306, 323, 346, 460, 470, 502, 529, 530},
    PokeType.DRAGON: {91, 162, 208, 342, 435, 494, 498, 538, 539},
    PokeType.PSYCHIC: {107, 109, 110, 133, 234, 309, 331, 335, 463, 473},
    PokeType.POISON: {147, 198, 200, 279, 280, 283, 332, 459, 485, 495}
}


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


def clone_missing_portraits(kao: Kao, index: int, *, force=False):
    """Fills all missing kao subindex slots for index with the first portrait."""
    cloned = kao.get(index, 0)
    # Skip mirrored slots.
    for i in range(1 if force else 2, SUBENTRIES, 1 if force else 2):
        if kao.get(index, i) is None:
            kao.set(index, i, cloned)
        elif force:
            kao.get(index, i).set(cloned.get())


class Roster(Enum):
    DUNGEON = auto()
    NPCS = auto()
    STARTERS = auto()


class MoveRoster(Enum):
    DEFAULT = auto()
    DAMAGING = auto()
    STAB = auto()


def get_allowed_md_ids(conf: RandomizerConfig, with_plus_600=False, *, roster=Roster.DUNGEON) -> List[int]:
    from skytemple_randomizer.randomizer.special import fun
    ents = set(conf['pokemon']['monsters_enabled'])
    if with_plus_600:
        to_add = set()
        for ent in ents:
            if ent + NUM_ENTITIES <= 1154:
                to_add.add(ent + NUM_ENTITIES)
        ents.update(to_add)
    if fun.is_fun_allowed():
        return fun.get_allowed_md_ids(ents, roster)
    return list(ents)


def get_allowed_item_ids(conf: RandomizerConfig) -> List[int]:
    return conf['dungeons']['items_enabled']


def _assert_not_empty(l):
    if len(l) < 1:
        raise ValueError("Could not generate a valid move with the given settings.")
    return l


def get_allowed_move_ids(conf: RandomizerConfig, roster=MoveRoster.DEFAULT, stab_type: PokeType = None) -> List[int]:
    base = set(conf['pokemon']['moves_enabled'])
    if roster == MoveRoster.DEFAULT:
        return list(base)
    elif roster == MoveRoster.DAMAGING:
        return _assert_not_empty(list(base.intersection(DAMAGING_MOVES)))
    elif roster == MoveRoster.STAB:
        if stab_type not in STAB_DICT:
            return _assert_not_empty(list(base.intersection(DAMAGING_MOVES)))
        l = list(base.intersection(STAB_DICT[stab_type]))
        if len(l) < 1:
            return _assert_not_empty(list(base.intersection(DAMAGING_MOVES)))
        return l


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

