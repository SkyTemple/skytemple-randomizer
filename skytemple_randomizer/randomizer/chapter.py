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
from skytemple_files.common.types.file_types import FileType
from skytemple_files.script.ssb.model import Ssb
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import replace_text_script, random_txt_line, get_script, \
    get_all_string_files
from skytemple_randomizer.status import Status


SCRIPTS_WITH_CHAPTER_NAMES = [
    'SCRIPT/D01P11A/m20a0101.ssb',
    'SCRIPT/D01P11B/m22a0901.ssb',
    'SCRIPT/D06P11A/m08a0601.ssb',
    'SCRIPT/D08P11A/m09a0101.ssb',
    'SCRIPT/D09P11A/m10a0101.ssb',
    'SCRIPT/D28P33A/m25a0401.ssb',
    'SCRIPT/G01P01B/m02a0101.ssb',
    'SCRIPT/G01P01B/m21a0101.ssb',
    'SCRIPT/G01P01C/m24a0102.ssb',
    'SCRIPT/G01P03A/m13a0101.ssb',
    'SCRIPT/G01P04A/m14a0901.ssb',
    'SCRIPT/G01P07A/c00a0201.ssb',
    'SCRIPT/G01P07A/m11a0101.ssb',
    'SCRIPT/P01P01A/m16a0101.ssb',
    'SCRIPT/P07P01A/m18b1401.ssb',
    'SCRIPT/S04P01A/m01a0101.ssb',
    'SCRIPT/V00P02/m01a02a.ssb',
    'SCRIPT/V17P03A/m17a0101.ssb'
]


class ChapterRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config['chapters']['randomize']:
            return 1
        return 0

    def run(self, status: Status):
        if not self.config['chapters']['randomize']:
            return
        status.step("Randomizing Chapter Names...")

        for script_name in SCRIPTS_WITH_CHAPTER_NAMES:
            ssb: Ssb = get_script(script_name, self.rom, self.static_data)

            for rtn in ssb.routine_ops:
                for op in rtn:
                    if op.op_code.name == 'back_SetBanner2':
                        chapter_name = random_txt_line(self.config['chapters']['text'])
                        string_index = op.params[5] - len(ssb.constants)
                        for lang, _ in get_all_string_files(self.rom, self.static_data):
                            ssb.strings[lang.name.lower()][string_index] = chapter_name

        status.done()
