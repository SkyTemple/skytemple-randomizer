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
from skytemple_files.patch.patches import Patcher
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.status import Status


class PatchApplier(AbstractRandomizer):
    def step_count(self) -> int:
        i = 0
        if self.config['improvements']['patch_moveshortcuts']:
            i += 1
        if self.config['improvements']['patch_unuseddungeonchance']:
            i += 1
        return i

    def run(self, status: Status):
        patcher = Patcher(self.rom, self.static_data)

        if self.config['improvements']['patch_moveshortcuts']:
            status.step("Apply 'MoveShortcuts' patch...")
            if not patcher.is_applied('MoveShortcuts'):
                patcher.apply('MoveShortcuts')

        if self.config['improvements']['patch_unuseddungeonchance']:
            status.step("Apply 'UnusedDungeonChancePatch' patch...")
            if not patcher.is_applied('UnusedDungeonChancePatch'):
                patcher.apply('UnusedDungeonChancePatch')

        status.done()
