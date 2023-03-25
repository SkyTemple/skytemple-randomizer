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
import os
from datetime import datetime
from enum import Enum
from random import choice, randrange
from typing import List, Union, Dict, Optional, Set, Sequence

from PIL import Image
from ndspy.rom import NintendoDSRom
from range_typed_integers import u16

from skytemple_files.common.ppmdu_config.data import Pmd2Data, Pmd2StringBlock
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_files_from_rom_with_extension
from skytemple_files.graphics.kao.protocol import KaoProtocol
from skytemple_randomizer.config import data_dir
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.seed_info import escape
from skytemple_randomizer.randomizer.util.util import clone_missing_portraits, get_main_string_file, \
    get_all_string_files, get_script, Roster
from skytemple_randomizer.status import Status


class FunArtistCredit(Enum):
    DECIMETER = "Decimeter", "https://twitter.com/Decimeter_"
    NOIVERN = "Noivern", "https://twitter.com/notarealnoivern"
    NERO_INTRUDER = "NeroIntruder", "https://twitter.com/NeroIntruder"
    REPPAMON = "Reppamon", "Reppamon#1249"
    DONKIN_DO = "DonkinDo", "https://twitter.com/DonkinDo"
    ADVOS = "Advos", "https://twitter.com/AdvosArt"
    GROMCHURCH = "gromchurch", "gromchurch#2351"
    DASK = "DasK", "http://reddit.com/u/thedask"
    REA = "pachigirl48", "rea#9004"
    ED = "Edael", "https://twitter.com/Exodus_Drake"
    CAMUS_ZEKE_SIRIUS = "CamusZekeSirius", "CamusZekeSirius#3218"
    WINGCAPMAN = "Wingcapman", "Wingcapman#8215"
    SPARKS = "sparklingdemon", "sparks#4828"
    C_PARIAH = "C. Pariah", "C. Pariah#7659"
    FABLE = "FabledTiefling", "https://twitter.com/Fable_PH"
    BORZOI = "borzoifeet (authhor of PMD: Anamnesis)\\nwith edits by Edael and Noivern", "https://clv.carrd.co/\\nhttp://pmd-anamnesis.cfw.me/\\nhttps://twitter.com/Exodus_Drake\\nhttps://twitter.com/notarealnoivern"

    NA = "n/a", "n/a"

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, url: str):
        self.url = url

    def __repr__(self):
        return f'FunArtistCredit["{self.name}"]'


class FunPortrait(Enum):
    PIKACHU = 25, FunArtistCredit.DECIMETER
    ODDISH = 43, FunArtistCredit.SPARKS
    DIGLETT = 50, FunArtistCredit.NERO_INTRUDER
    KOFFING = 109, FunArtistCredit.NERO_INTRUDER
    MEW = 151, FunArtistCredit.REPPAMON
    TOTODILE = 158, {'158.png': FunArtistCredit.NOIVERN, '158b.png': FunArtistCredit.DECIMETER}
    LEDYBA = 165, FunArtistCredit.NOIVERN
    QUAGSIRE = 195, FunArtistCredit.GROMCHURCH
    PORYGON2 = 260, FunArtistCredit.NERO_INTRUDER
    TYRGOUE = 263, FunArtistCredit.DASK
    MUDKIP = 286, FunArtistCredit.DECIMETER
    POOCHY = 289, FunArtistCredit.REA
    LOUDRED = 322, FunArtistCredit.ED
    SKITTY = 328, FunArtistCredit.NERO_INTRUDER
    BAGON = 403, FunArtistCredit.C_PARIAH
    REGISTEEL = 411, FunArtistCredit.CAMUS_ZEKE_SIRIUS
    KYOGRE = 414, FunArtistCredit.NOIVERN
    GROUDON = 415, FunArtistCredit.NOIVERN
    RAYQUAZA = 416, FunArtistCredit.NOIVERN
    DEOXYS = 418, FunArtistCredit.NERO_INTRUDER
    TORTERRA = 424, FunArtistCredit.NOIVERN
    SHANX = 438, FunArtistCredit.NOIVERN
    BUNEARY = 469, FunArtistCredit.REA
    PROBOPASS = 518, FunArtistCredit.DONKIN_DO
    DIALGA = 525, FunArtistCredit.NOIVERN
    PDIALGA = 552, FunArtistCredit.ADVOS
    PALKIA = 528, FunArtistCredit.NOIVERN
    SHAYMIN = 534, FunArtistCredit.WINGCAPMAN
    SSHAYMIN = 535, FunArtistCredit.WINGCAPMAN
    WIGGLY = 40, FunArtistCredit.FABLE
    WIGGLY2 = 555, FunArtistCredit.FABLE
    WIGGLY3 = 560, FunArtistCredit.FABLE
    DRATINI = 147, FunArtistCredit.NOIVERN
    DRAGONAIR = 148, FunArtistCredit.NOIVERN
    DRAGONITE = 149, FunArtistCredit.NOIVERN
    SABLEYE = 330, FunArtistCredit.BORZOI
    SABLEYE2 = 573, FunArtistCredit.BORZOI
    EEVEE = 133, FunArtistCredit.REPPAMON
    VAPOREON = 134, FunArtistCredit.REPPAMON
    JOLTEON = 135, FunArtistCredit.REPPAMON
    FLAREON = 136, FunArtistCredit.REPPAMON
    ESPEON = 196, FunArtistCredit.REPPAMON
    UMBREON = 197, FunArtistCredit.REPPAMON
    LEAFEON = 512, FunArtistCredit.REPPAMON
    GLACEON = 513, FunArtistCredit.REPPAMON

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, credit: Union[FunArtistCredit, Dict[str, FunArtistCredit]]):
        if isinstance(credit, dict):
            credit = credit[choice(list(credit.keys()))]
        self.file_name = str(self.value) + '.png'
        self.credit = credit

    def __repr__(self):
        return f'FunArtistCredits({self.value})'


class CustomFunPortrait:
    def __init__(self, value, file_name, credit):
        self.value = value
        self.file_name = file_name
        self.credit = credit


FunPortraitLike = Union[CustomFunPortrait, FunPortrait]


def is_fun_allowed():
    if 'SKYTEMPLE_FUN' in os.environ:
        return bool(int(os.environ['SKYTEMPLE_FUN']))
    now = datetime.now()
    return now.month == 4 and now.day == 1


def _get_fun_portraits() -> Sequence[FunPortraitLike]:
    return list(FunPortrait)


def get_allowed_md_ids(base_set: Set[u16], roster: Roster) -> List[u16]:
    s = set()
    num_entities = FileType.MD.properties().num_entities
    for x in _get_fun_portraits():
        s.add(u16(x.value))
        if x.value + num_entities <= 1154:
            s.add(u16(x.value + num_entities))
    extra_candidates: List[u16] = list(base_set - s)
    extras_max = 0
    if roster == Roster.NPCS:
        extras_max = 5
    elif roster == Roster.DUNGEON:
        extras_max = 50
    for _ in range(0, extras_max):
        y = choice(extra_candidates)
        s.add(y)
        if y + num_entities <= 1154:
            s.add(u16(y + num_entities))
    return list(base_set & s)


def replace_portraits(rom: NintendoDSRom, static_data: Pmd2Data):
    kao: KaoProtocol = FileType.KAO.deserialize(rom.getFileByName('FONT/kaomado.kao'))
    for portrait in _get_fun_portraits():
        portrait_id = portrait.value - 1
        pil_img = Image.open(os.path.join(data_dir(), 'fun', portrait.file_name))
        kaoimg = kao.get(portrait_id, 0)
        try:
            if kaoimg is None:
                kao.set_from_img(portrait_id, 0, pil_img)
            else:
                kaoimg.set(pil_img)
            clone_missing_portraits(kao, portrait_id, force=True)
        except AttributeError as ex:
            if "compress well" not in str(ex):
                raise ex

    rom.setFileByName('FONT/kaomado.kao', FileType.KAO.serialize(kao))


def process_text_strings(rom: NintendoDSRom, static_data: Pmd2Data):
    for lang, strings in get_all_string_files(rom, static_data):
        for string_block in _collect_text_categories(static_data.string_index_data.string_blocks):
            for i in range(9, string_block.end - string_block.begin):
                if randrange(0, 500) == 0:
                    try:
                        strings.strings[string_block.begin + i] = "April Fools!"
                    except IndexError:
                        pass

        rom.setFileByName(f'MESSAGE/{lang.filename}', FileType.STR.serialize(strings))


def process_story_strings(rom: NintendoDSRom, static_data: Pmd2Data):
    for lang, _ in get_all_string_files(rom, static_data):
        for file_path in get_files_from_rom_with_extension(rom, 'ssb'):
            script = get_script(file_path, rom, static_data)
            for i in range(9, len(script.strings[lang.name.lower()])):
                if randrange(0, 500) == 0:
                    script.strings[lang.name.lower()][i] = "April Fools!"


def get_artist_credits(rom: NintendoDSRom, static_data: Pmd2Data):
    credits = ""
    lang, msg = get_main_string_file(rom, static_data)
    for entry in _get_fun_portraits():
        name = msg.strings[static_data.string_index_data.string_blocks['Pokemon Names'].begin + entry.value]
        credits += f"""
        case menu("{name}"):
            message_Talk("Author: [CS:A]{escape(entry.credit.value)}[CR]\\n{escape(entry.credit.url)}");
            jump @l_artists;
"""
    return credits


class SpecialFunRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if is_fun_allowed():
            return 1
        return 0

    def run(self, status: Status):
        if not is_fun_allowed():
            return status.done()

        status.step("Finishing up...")

        process_text_strings(self.rom, self.static_data)
        process_story_strings(self.rom, self.static_data)

        status.done()


def _collect_text_categories(string_cats):
    current_index = 0
    for cat in sorted(string_cats.values(), key=lambda c: c.begin):
        if cat.begin > current_index:
            # yield a placeholder category
            yield Pmd2StringBlock(f"({current_index} - {cat.begin - 1})", "", current_index, cat.begin)
        yield cat
        current_index = cat.end
