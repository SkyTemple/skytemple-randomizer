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
from random import shuffle, randrange, choice
from typing import Iterable

from range_typed_integers import u8
from skytemple_files.common.ppmdu_config.data import Pmd2Language, Pmd2StringBlock
from skytemple_files.common.types.file_types import FileType
from skytemple_files.data.item_p.protocol import ItemPProtocol
from skytemple_files.data.str.model import Str
from skytemple_files.data.waza_p.protocol import WazaPProtocol
from skytemple_files.patch.patches import Patcher

from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_all_string_files
from skytemple_randomizer.status import Status
from skytemple_files.common.i18n_util import _

from skytemple_randomizer.string_provider import StringType

SPRITE_PALETTES_COMBINATIONS = [
    (0, 0),
    (0, 1),
    (0, 2),
    (0, 3),
    (0, 4),
    (0, 10),
    (0, 11),
    (1, 1),
    (1, 5),
    (1, 7),
    (1, 11),
    (2, 0),
    (2, 2),
    (2, 3),
    (2, 4),
    (2, 6),
    (2, 12),
    (3, 3),
    (3, 6),
    (4, 0),
    (4, 3),
    (4, 4),
    (4, 6),
    (4, 10),
    (4, 11),
    (5, 0),
    (5, 1),
    (5, 2),
    (5, 3),
    (5, 4),
    (5, 5),
    (5, 6),
    (5, 7),
    (5, 8),
    (5, 10),
    (5, 11),
    (5, 12),
    (6, 3),
    (6, 11),
    (7, 0),
    (7, 3),
    (8, 0),
    (8, 2),
    (8, 3),
    (10, 0),
    (10, 3),
    (10, 4),
    (10, 5),
    (11, 1),
    (12, 1),
    (13, 2),
    (13, 3),
    (13, 11),
    (13, 12),
    (13, 13),
    (14, 3),
    (14, 4),
    (14, 13),
    (15, 0),
    (15, 1),
    (15, 3),
    (15, 4),
    (15, 7),
    (15, 11),
    (15, 12),
    (16, 3),
    (16, 5),
    (16, 11),
    (16, 12),
    (17, 0),
    (17, 1),
    (17, 2),
    (17, 3),
    (17, 4),
    (17, 6),
    (17, 7),
    (17, 9),
    (17, 10),
    (17, 11),
    (17, 12),
    (17, 13),
    (17, 15),
    (18, 3),
    (19, 0),
    (19, 3),
    (20, 2),
    (20, 10),
    (24, 0),
    (25, 5),
    (26, 1),
    (27, 1),
    (27, 4),
    (27, 5),
    (27, 10),
    (27, 13),
    (27, 14),
    (28, 2),
    (28, 3),
    (28, 11),
    (29, 3),
    (29, 4),
    (30, 0),
    (30, 10),
    (30, 11),
    (31, 5),
    (31, 10),
    (32, 0),
    (32, 10),
    (33, 1),
    (34, 7),
    (34, 10),
    (35, 2),
    (35, 3),
    (35, 4),
    (35, 10),
    (35, 12),
    (35, 13),
    (36, 15),
    (37, 0),
    (37, 3),
    (37, 11),
    (37, 12),
    (37, 14),
    (38, 2),
    (38, 8),
    (39, 0),
    (39, 10),
    (40, 0),
    (40, 2),
    (40, 5),
    (40, 8),
    (40, 10),
    (40, 11),
    (40, 12),
    (40, 14),
    (41, 3),
    (42, 4),
    (43, 0),
    (43, 3),
    (43, 11),
    (43, 13),
    (44, 12),
    (46, 5),
    (46, 9),
    (46, 10),
    (47, 3),
    (49, 0),
    (49, 4),
    (49, 5),
    (49, 6),
    (49, 9),
    (49, 13),
    (50, 0),
    (51, 6),
    (52, 4),
    (52, 10),
    (53, 0),
    (53, 1),
    (53, 2),
    (53, 3),
    (53, 4),
    (53, 5),
    (53, 6),
    (53, 7),
    (53, 8),
    (53, 9),
    (53, 10),
    (53, 11),
    (53, 12),
    (53, 13),
    (53, 14),
    (53, 15),
    (54, 0),
    (54, 4),
    (54, 5),
    (54, 6),
    (54, 7),
    (54, 10),
    (55, 0),
    (55, 1),
    (55, 4),
    (55, 5),
    (55, 6),
    (55, 7),
    (55, 8),
    (55, 9),
    (55, 11),
    (55, 12),
    (55, 15),
    (56, 0),
    (56, 2),
    (56, 4),
    (56, 6),
    (56, 7),
    (56, 8),
    (56, 10),
    (56, 12),
    (56, 13),
    (56, 15),
    (57, 2),
    (57, 4),
    (57, 10),
    (57, 12),
    (57, 15),
    (58, 1),
    (58, 6),
    (58, 7),
    (58, 12),
    (58, 15),
    (59, 1),
    (59, 3),
    (59, 10),
    (60, 5),
    (61, 1),
    (61, 4),
    (61, 7),
    (62, 3),
]


class BlindItemsMovesRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        steps = 0
        if self.config["item"]["blind_items"]["enable"]:
            steps += 2
        if self.config["pokemon"]["blind_moves"]["enable"]:
            steps += 1
        return steps

    def run(self, status: Status):
        patcher = Patcher(self.rom, self.static_data)

        if self.config["item"]["blind_items"]["enable"]:
            status.step(_("Apply 'DisableTips' patch..."))
            if not patcher.is_applied("DisableTips"):
                patcher.apply("DisableTips")
            self.blind_items(status)
        if self.config["pokemon"]["blind_moves"]["enable"]:
            self.blind_moves(status)
        status.done()

    def blind_items(self, status: Status):
        status.step(_('Enabling "Blind Items" Mode...'))
        pool = self.config["item"]["blind_items"]["names"].splitlines()
        shuffle(pool)
        allowed = self.config["dungeons"]["items_enabled"]

        item_p: ItemPProtocol = FileType.ITEM_P.deserialize(self.rom.getFileByName("BALANCE/item_p.bin"))
        strings = list(self.get_strings())
        for item in item_p.item_list:
            if item.item_id not in allowed:
                continue
            sprite, palette = choice(SPRITE_PALETTES_COMBINATIONS)
            item.sprite = u8(sprite)
            item.palette = u8(palette)
            item.buy_price = randrange(1, 3001)
            item.sell_price = item.buy_price // randrange(1, 20)
            self.modify_string(strings, StringType.ITEM_NAMES, item.item_id, pool.pop())
            self.modify_string(strings, StringType.ITEM_SHORT_DESCRIPTIONS, item.item_id, "???")
            self.modify_string(strings, StringType.ITEM_LONG_DESCRIPTIONS, item.item_id, "???")
        self.rom.setFileByName("BALANCE/item_p.bin", FileType.ITEM_P.serialize(item_p))
        self.save_strings(strings)

    def blind_moves(self, status: Status):
        status.step(_('Enabling "Blind Moves" Mode...'))
        pool = self.config["pokemon"]["blind_moves"]["names"].splitlines()
        shuffle(pool)
        allowed = self.config["pokemon"]["moves_enabled"]

        waza_p: WazaPProtocol = FileType.WAZA_P.deserialize(self.rom.getFileByName("BALANCE/waza_p.bin"))
        strings = list(self.get_strings())
        for move in waza_p.moves:
            if move.move_id not in allowed:
                continue
            move.type = u8(randrange(1, 18))
            self.modify_string(strings, StringType.MOVE_NAMES, move.move_id, pool.pop())
            self.modify_string(strings, StringType.MOVE_DESCRIPTIONS, move.move_id, "???")

        self.rom.setFileByName("BALANCE/waza_p.bin", FileType.WAZA_P.serialize(waza_p))
        self.save_strings(strings)

    def get_strings(self) -> Iterable[tuple[Pmd2Language, Str]]:
        return get_all_string_files(self.rom, self.static_data)

    def save_strings(self, strings: Iterable[tuple[Pmd2Language, Str]]):
        for lang, string_file in strings:
            self.rom.setFileByName(f"MESSAGE/{lang.filename}", FileType.STR.serialize(string_file))

    def modify_string(
        self,
        strings: Iterable[tuple[Pmd2Language, Str]],
        string_type: StringType,
        idx: int,
        new_string: str,
    ):
        for lang, string_file in strings:
            index = self._get_string_block(string_type).begin + idx
            string_file.strings[index] = new_string

    def _get_string_block(self, string_type: StringType) -> Pmd2StringBlock:
        string_index_data = self.static_data.string_index_data

        if string_type.xml_name not in string_index_data.string_blocks:
            raise ValueError(f"String mapping for {string_type} not found.")

        return string_index_data.string_blocks[string_type.xml_name]
