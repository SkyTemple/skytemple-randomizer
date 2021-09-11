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
from random import shuffle

from skytemple_files.common.ppmdu_config.data import Pmd2StringBlock
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_binary_from_rom_ppmdu, set_binary_in_rom_ppmdu
from skytemple_files.hardcoded.text_speed import HardcodedTextSpeed
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_main_string_file, get_all_string_files
from skytemple_randomizer.status import Status
DEBUG_SPEED = 255


class MiscRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config['text']['instant']:
            return 1
        return 0

    def run(self, status: Status):
        if not self.config['text']['instant']:
            return status.done()
        status.step('Enabling instant text...')

        arm9 = bytearray(get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin']))
        HardcodedTextSpeed.set_text_speed(
            DEBUG_SPEED, arm9, self.static_data
        )
        set_binary_in_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin'], arm9)

        status.done()
