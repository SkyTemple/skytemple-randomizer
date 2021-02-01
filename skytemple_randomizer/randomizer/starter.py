"""
Randomizes starters.
Based on mdrngzer.
"""
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

from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_binary_from_rom_ppmdu, set_binary_in_rom_ppmdu
from skytemple_files.data.md.model import NUM_ENTITIES
from skytemple_files.data.str.model import Str
from skytemple_files.hardcoded.personality_test_starters import HardcodedPersonalityTestStarters
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_main_string_file, get_allowed_md_ids, clone_missing_portraits, \
    replace_strings, get_all_string_files
from skytemple_randomizer.status import Status


class StarterRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config['starters_npcs']['starters']:
            return 3
        return 0

    def run(self, status: Status):
        if not self.config['starters_npcs']['starters']:
            return status.done()
        status.step("Randomizing Partner Starters...")
        overlay13 = get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['overlay/overlay_0013.bin'])
        pokemon_string_data = self.static_data.string_index_data.string_blocks["Pokemon Names"]
        langs = list(get_all_string_files(self.rom, self.static_data))

        orig_partner_ids = HardcodedPersonalityTestStarters.get_partner_md_ids(overlay13, self.static_data)
        new_partner_ids = [
            self._random_gender(choice(get_allowed_md_ids(self.config)))
            for _ in range(0, len(orig_partner_ids))
        ]
        HardcodedPersonalityTestStarters.set_partner_md_ids(new_partner_ids, overlay13, self.static_data)

        status.step("Randomizing Player Starters...")
        # The player options are put into two-pairs for each nature, first male then female.
        orig_player_ids = HardcodedPersonalityTestStarters.get_player_md_ids(overlay13, self.static_data)
        new_player_ids = []
        k = 0  # Index of text for "Will be..."
        for i in range(0, len(orig_player_ids)):
            new_id = choice(get_allowed_md_ids(self.config))
            if k % 3 == 0:
                k += 1
            # todo: refactor, this isn't really efficient.
            for lang, string_file in langs:
                string_file.strings[0x67C + k] = replace_strings(
                    string_file.strings[0x67C + k],
                    {
                        self._get_name(string_file, orig_player_ids[i], pokemon_string_data):
                        self._get_name(string_file, new_id, pokemon_string_data)
                    }
                )
            if i % 2 == 1 and new_id + NUM_ENTITIES <= 1154:
                new_id += NUM_ENTITIES
            new_player_ids.append(new_id)
            k += 1
        HardcodedPersonalityTestStarters.set_player_md_ids(new_player_ids, overlay13, self.static_data)

        status.step("Cloning missing starter portraits...")
        kao = FileType.KAO.deserialize(self.rom.getFileByName('FONT/kaomado.kao'))
        for new in new_player_ids + new_partner_ids:
            new_base = new % 600
            clone_missing_portraits(kao, new_base - 1)

        set_binary_in_rom_ppmdu(self.rom, self.static_data.binaries['overlay/overlay_0013.bin'], overlay13)
        for lang, string_file in langs:
            self.rom.setFileByName(f'MESSAGE/{lang.filename}', FileType.STR.serialize(string_file))
        self.rom.setFileByName('FONT/kaomado.kao', FileType.KAO.serialize(kao))

        status.done()

    @staticmethod
    def _random_gender(orig_value):
        """50% male (nothing added to index), 50% female (+600 added to index)"""
        if orig_value + NUM_ENTITIES > 1154:
            return orig_value
        if choice([True, False]):
            return orig_value + NUM_ENTITIES
        return orig_value

    @staticmethod
    def _get_name(string_file: Str, index: int, pokemon_string_data):
        """Returns a Pokémon name from the string file"""
        return string_file.strings[pokemon_string_data.begin + index]
