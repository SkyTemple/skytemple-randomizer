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
from skytemple_files.common.ppmdu_config.data import GAME_REGION_JP
from skytemple_files.common.ppmdu_config.data import Pmd2StringBlock
from skytemple_files.common.types.file_types import FileType
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_all_string_files
from skytemple_randomizer.status import Status
from skytemple_files.common.i18n_util import _


class TextMainRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config["text"]["main"]:
            return 1
        return 0

    def run(self, status: Status):
        if not self.config["text"]["main"]:
            return status.done()
        status.step(_("Randomizing all main text..."))

        if self.static_data.game_region == GAME_REGION_JP:
            return self.run_for_jp(status)

        for lang, strings in get_all_string_files(self.rom, self.static_data):
            for string_block in self._collect_categories(self.static_data.string_index_data.string_blocks):
                part = strings.strings[string_block.begin : string_block.end]
                self.rng.shuffle(part)
                strings.strings[string_block.begin : string_block.end] = part

            self.rom.setFileByName(f"MESSAGE/{lang.filename}", FileType.STR.serialize(strings))

        status.done()

    def run_for_jp(self, status: Status):
        # TODO: Trying to shuffle strings in the JP ROM currently consistently results in a crash upon entering
        #       the main menu.
        status.done()

    def _collect_categories(self, string_cats):
        current_index = 0
        for cat in sorted(string_cats.values(), key=lambda c: c.begin):
            if cat.begin > current_index:
                # yield a placeholder category
                yield Pmd2StringBlock(f"({current_index} - {cat.begin - 1})", "", current_index, cat.begin)
            yield cat
            current_index = cat.end
