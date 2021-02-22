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
from skytemple_files.common.ppmdu_config.data import GAME_REGION_US
from skytemple_files.common.types.file_types import FileType
from skytemple_randomizer.config import version
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_all_string_files
from skytemple_randomizer.status import Status

STR_EU = 16330
STR_US = 16328


class SeedInfo(AbstractRandomizer):
    def step_count(self) -> int:
        return 1

    def run(self, status: Status):
        status.step("Loading Seed Info...")

        langs = list(get_all_string_files(self.rom, self.static_data))
        str_offset = STR_EU
        if self.static_data.game_region == GAME_REGION_US:
            str_offset = STR_US

        for lang, string_file in langs:
            string_file.strings[str_offset] = f"""Randomized with SkyTemple Randomizer.
Version:[CS:Z]{version()}[CR]
Seed: [CS:C]{self.seed}[CR]

[CS:H]PLEASE NOTE:[CR]
This seed will only produce the same output
when used with the exact same version
and configuration of the randomizer that
was used."""

        for lang, string_file in langs:
            self.rom.setFileByName(f'MESSAGE/{lang.filename}', FileType.STR.serialize(string_file))

        status.done()
