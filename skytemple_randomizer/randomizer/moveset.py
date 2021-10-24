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
from random import choice
from typing import List, Tuple

from skytemple_files.common.ppmdu_config.data import Pmd2Language
from skytemple_files.common.types.file_types import FileType
from skytemple_files.data.item_p.model import ItemP
from skytemple_files.data.md.model import PokeType, Md
from skytemple_files.data.str.model import Str
from skytemple_files.data.waza_p.model import WazaP
from skytemple_randomizer.config import MovesetConfig
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_allowed_move_ids, MoveRoster, get_all_string_files
from skytemple_randomizer.status import Status


class MovesetRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        i = 0
        if self.config['pokemon']['movesets'] != MovesetConfig.NO:
            i += 1
        if self.config['pokemon']['tm_hm_movesets']:
            i += 1
        if self.config['pokemon']['tms_hms']:
            i += 1
        return i

    def run(self, status: Status):
        md: Md = FileType.MD.deserialize(self.rom.getFileByName('BALANCE/monster.md'))
        waza_p: WazaP = FileType.WAZA_P.deserialize(self.rom.getFileByName('BALANCE/waza_p.bin'))

        if self.config['pokemon']['movesets'] == MovesetConfig.NO:
            status.step("Randomizing Level-Up movesets...")

            valid_move_ids = get_allowed_move_ids(self.config)
            damaging_move_ids = get_allowed_move_ids(self.config, MoveRoster.DAMAGING)

            for md_entry, waza_p_entry in zip(md.entries, waza_p.learnsets):
                waza_p_entry.egg_moves = [choice(valid_move_ids) for _ in waza_p_entry.egg_moves]

                for idx, e in enumerate(waza_p_entry.level_up_moves):
                    if idx > 0 or self.config['pokemon']['movesets'] == MovesetConfig.FULLY_RANDOM:
                        e.move_id = choice(valid_move_ids)
                    elif self.config['pokemon']['movesets'] == MovesetConfig.FIRST_DAMAGE:
                        e.move_id = choice(damaging_move_ids)
                    elif self.config['pokemon']['movesets'] == MovesetConfig.FIRST_STAB:
                        e.move_id = choice(get_allowed_move_ids(self.config, MoveRoster.STAB, md_entry.type_primary))

        allowed_move_ids = get_allowed_move_ids(self.config, MoveRoster.DEFAULT)
        if self.config['pokemon']['tms_hms']:
            status.step("Randomizing TMs/HMs...")
            item_p: ItemP = FileType.ITEM_P.deserialize(self.rom.getFileByName('BALANCE/item_p.bin'))
            move_names = self.static_data.string_index_data.string_blocks["Move Names"]
            item_names = self.static_data.string_index_data.string_blocks["Item Names"]
            long_descs = self.static_data.string_index_data.string_blocks["Item Long Descriptions"]
            short_descs = self.static_data.string_index_data.string_blocks["Item Short Descriptions"]
            str_files: List[Tuple[Pmd2Language, Str]] = list(get_all_string_files(self.rom, self.static_data))
            for item in item_p.item_list:
                if item.category == 5:
                    move_id = choice(allowed_move_ids)
                    item.move_id = move_id
                    this_move_names = [t.strings[move_names.begin + move_id] for _, t in str_files]
                    self._update_all_langs([f'[M:I0]{name}' for name in this_move_names], str_files, item_names.begin + item.item_id)
                    self._update_all_langs([f'Teaches [CS:M]{name}[CR].' for name in this_move_names], str_files, short_descs.begin  + item.item_id)
                    # TODO: Long description links.
                    self._update_all_langs([f'Teaches the move [CS:M]{name}[CR].\n[C]\n[equip_list]' for name in this_move_names], str_files, long_descs.begin + item.item_id)

            self.rom.setFileByName('BALANCE/item_p.bin', FileType.ITEM_P.serialize(item_p))
            for lang, string_file in str_files:
                self.rom.setFileByName(f'MESSAGE/{lang.filename}', FileType.STR.serialize(string_file))

        if self.config['pokemon']['tm_hm_movesets']:
            status.step("Randomizing TM/HM movesets...")
            item_p: ItemP = FileType.ITEM_P.deserialize(self.rom.getFileByName('BALANCE/item_p.bin'))
            move_ids = []
            for item in item_p.item_list:
                if item.category == 5:
                    move_ids.append(item.move_id)

            for md_entry, waza_p_entry in zip(md.entries, waza_p.learnsets):
                waza_p_entry.tm_hm_moves = [choice(move_ids) for _ in waza_p_entry.tm_hm_moves]

        self.rom.setFileByName('BALANCE/waza_p.bin', FileType.WAZA_P.serialize(waza_p))
        status.done()

    @staticmethod
    def _update_all_langs(texts: List[str], str_files: List[Tuple[Pmd2Language, Str]], index: int):
        for text, (_, str_file) in zip(texts, str_files):
            str_file.strings[index] = text
