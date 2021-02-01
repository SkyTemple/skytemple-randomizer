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
from typing import Dict

from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_files_from_rom_with_extension
from skytemple_files.script.ssb.model import Ssb
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_all_string_files, get_script
from skytemple_randomizer.status import Status


class TextScriptRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config['text']['story']:
            return 2
        return 0

    def run(self, status: Status):
        if not self.config['text']['story']:
            return status.done()
        status.step('Randomizing all script text: Reading strings...')

        all_strings_langs = {}
        for lang, _ in get_all_string_files(self.rom, self.static_data):
            all_strings = []
            ssb_map: Dict[str, Ssb] = {}
            all_strings_langs[lang] = all_strings, ssb_map
            for file_path in get_files_from_rom_with_extension(self.rom, 'ssb'):
                script = get_script(file_path, self.rom, self.static_data)
                all_strings += script.strings[lang.name.lower()]
                ssb_map[file_path] = script

        status.step('Randomizing all script text: Writing strings...')
        for lang, (all_strings, ssb_map) in all_strings_langs.items():
            shuffle(all_strings)
            for file_path, script in ssb_map.items():
                samples = []
                for _ in range(0, len(script.strings[lang.name.lower()])):
                    samples.append(all_strings.pop())
                script.strings[lang.name.lower()] = samples

        status.done()
