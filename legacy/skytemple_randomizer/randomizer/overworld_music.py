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
from random import choice

from range_typed_integers import u8
from skytemple_files.common.util import get_files_from_rom_with_extension, get_binary_from_rom, \
    set_binary_in_rom
from skytemple_files.hardcoded.main_menu_music import HardcodedMainMenuMusic
from skytemple_files.script.ssb.model import Ssb
from skytemple_randomizer.frontend.abstract import AbstractFrontend
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_script
from skytemple_randomizer.status import Status


class OverworldMusicRandomizer(AbstractRandomizer):
    def __init__(self, config, rom, static_data, seed, frontend: AbstractFrontend):
        super().__init__(config, rom, static_data, seed, frontend)
        self.bgs = [u8(b.id) for b in self.static_data.script_data.bgms if b.loops]

    def step_count(self) -> int:
        i = 0
        if self.config['starters_npcs']['topmenu_music']:
            i += 1
        if self.config['starters_npcs']['overworld_music']:
            i += 1
        return i

    def run(self, status: Status):
        if self.config['starters_npcs']['topmenu_music']:
            status.step("Randomizing Titlescreen Music...")
            ov0 = bytearray(get_binary_from_rom(self.rom, self.static_data.bin_sections.overlay0))
            ov9 = bytearray(get_binary_from_rom(self.rom, self.static_data.bin_sections.overlay9))
            HardcodedMainMenuMusic.set_main_menu_music(
                self._get_random_music_id(), ov0, self.static_data, ov9
            )
            set_binary_in_rom(self.rom, self.static_data.bin_sections.overlay0, ov0)
            set_binary_in_rom(self.rom, self.static_data.bin_sections.overlay9, ov9)

        if not self.config['starters_npcs']['overworld_music']:
            status.done()
            return

        status.step("Randomizing Overworld Music...")

        for script_name in get_files_from_rom_with_extension(self.rom, 'ssb'):
            ssb: Ssb = get_script(script_name, self.rom, self.static_data)

            for rtn in ssb.routine_ops:
                for op in rtn:
                    op_c = self.static_data.script_data.op_codes__by_name[op.op_code.name][0]
                    for i, param_spec in enumerate(op_c.arguments):
                        if param_spec.type == 'Bgm':
                            # Only randomize real music (looping tracks)
                            if any((b == op.params[i] for b in self.bgs)):
                                op.params[i] = self._get_random_music_id()
                    # We don't really support those, so replace them with 1 sec wait.
                    if op_c.name == 'WaitBgmSignal' or op_c.name == 'WaitBgm' or op_c.name == 'WaitBgm2':
                        op.op_code = self.static_data.script_data.op_codes__by_name['Wait'][0]
                        op.params = [60]

        status.done()

    def _get_random_music_id(self):
        r = choice(self.bgs)
        return r
