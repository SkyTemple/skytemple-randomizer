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
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.status import Status


class IqTacticsRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        i = 0
        if self.config['iq']['randomize_tactics']:
            i += 1
        if self.config['iq']['randomize_iq_gain']:
            i += 1
        if self.config['iq']['randomize_iq_groups']:
            i += 1
        if self.config['iq']['randomize_iq_skills']:
            i += 1
        return i

    def run(self, status: Status):
        pass  # todo
