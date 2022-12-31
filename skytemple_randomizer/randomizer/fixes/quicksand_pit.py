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

from skytemple_files.script.ssb.model import Ssb

from skytemple_randomizer.frontend.abstract import AbstractFrontend
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_script
from skytemple_randomizer.status import Status

SCRIPT_NAME = "SCRIPT/D14P12A/m14a0103.ssb"


class FixQuicksandPit(AbstractRandomizer):
    def __init__(self, config, rom, static_data, seed, frontend: AbstractFrontend):
        super().__init__(config, rom, static_data, seed, frontend)
        self.bgs = [b for b in self.static_data.script_data.bgms if b.loops]

    def step_count(self) -> int:
        return 1

    def run(self, status: Status):
        status.step("Fixing Quicksand Pit...")
        try:
            ssb: Ssb = get_script(SCRIPT_NAME, self.rom, self.static_data)

            for rtn in ssb.routine_ops:
                for op in rtn:
                    op_c = self.static_data.script_data.op_codes__by_name[op.op_code.name][0]
                    if op_c.name == 'WaitAnimation':
                        op.op_code = self.static_data.script_data.op_codes__by_name['Null'][0]
        except Exception:
            # We ignore errors, it's possible ROM Hacks removed this script
            raise  # todo!

        status.done()
