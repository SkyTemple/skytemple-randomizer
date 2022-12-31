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
from range_typed_integers import u8
from skytemple_files.common.util import get_binary_from_rom, set_binary_in_rom
from skytemple_files.hardcoded.text_speed import HardcodedTextSpeed
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.status import Status
DEBUG_SPEED = u8(255)


class MiscRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config['text']['instant']:
            return 1
        return 0

    def run(self, status: Status):
        if not self.config['text']['instant']:
            return status.done()
        status.step('Enabling instant text...')

        arm9 = bytearray(get_binary_from_rom(self.rom, self.static_data.bin_sections.arm9))
        HardcodedTextSpeed.set_text_speed(
            DEBUG_SPEED, arm9, self.static_data
        )
        set_binary_in_rom(self.rom, self.static_data.bin_sections.arm9, arm9)

        status.done()
