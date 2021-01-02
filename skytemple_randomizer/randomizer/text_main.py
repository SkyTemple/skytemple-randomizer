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
from random import shuffle

from skytemple_files.common.ppmdu_config.data import Pmd2StringBlock
from skytemple_files.common.types.file_types import FileType
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_main_string_file
from skytemple_randomizer.status import Status


class TextMainRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config['text']['main']:
            return 1
        return 0

    def run(self, status: Status):
        if not self.config['text']['main']:
            return status.done()
        status.step('Randomizing all main text...')
        lang, strings = get_main_string_file(self.rom, self.static_data)

        for string_block in self._collect_categories(self.static_data.string_index_data.string_blocks):
            part = strings.strings[string_block.begin:string_block.end]
            shuffle(part)
            strings.strings[string_block.begin:string_block.end] = part

        self.rom.setFileByName(f'MESSAGE/{lang.filename}', FileType.STR.serialize(strings))

        status.done()

    def _collect_categories(self, string_cats):
        current_index = 0
        for cat in sorted(string_cats.values(), key=lambda c: c.begin):
            if cat.begin > current_index:
                # yield a placeholder category
                yield Pmd2StringBlock(f"({current_index} - {cat.begin - 1})", current_index, cat.begin)
            yield cat
            current_index = cat.end
