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
from random import choice

from skytemple_files.common.util import get_files_from_rom_with_extension
from skytemple_files.script.ssb.model import Ssb
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_script
from skytemple_randomizer.status import Status


class OverworldMusicRandomizer(AbstractRandomizer):
    def __init__(self, config, rom, static_data, seed):
        super().__init__(config, rom, static_data, seed)
        self.bgs = [b for b in self.static_data.script_data.bgms if b.loops]

    def step_count(self) -> int:
        if self.config['starters_npcs']['overworld_music']:
            return 1
        return 0

    def run(self, status: Status):
        if not self.config['starters_npcs']['overworld_music']:
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
                            if any((b.id == op.params[i] for b in self.bgs)):
                                op.params[i] = self._get_random_music_id()
                    # We don't really support those, so replace them with 1 sec wait.
                    if op_c.name == 'WaitBgmSignal' or op_c.name == 'WaitBgm' or op_c.name == 'WaitBgm2':
                        op.op_code = self.static_data.script_data.op_codes__by_name['Wait'][0]
                        op.params = [60]

        status.done()

    def _get_random_music_id(self):
        r = choice(self.bgs)
        return r.id
