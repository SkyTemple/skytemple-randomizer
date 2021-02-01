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
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_main_string_file, replace_text_script, random_txt_line, \
    get_all_string_files
from skytemple_randomizer.status import Status


class LocationRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config['locations']['randomize']:
            return 2  # names, names mentioned in script
        return 0

    def run(self, status: Status):
        if not self.config['locations']['randomize']:
            return
        status.step("Randomizing Location Names...")
        ground_map_names = self.static_data.string_index_data.string_blocks["Ground Map Names"]
        dunge_names_main = self.static_data.string_index_data.string_blocks["Dungeon Names (Main)"]
        dunge_names_sele = self.static_data.string_index_data.string_blocks["Dungeon Names (Selection)"]
        dunge_names_sdba = self.static_data.string_index_data.string_blocks["Dungeon Names (SetDungeonBanner)"]
        dunge_names_bann = self.static_data.string_index_data.string_blocks["Dungeon Names (Banner)"]

        rename_dungeon_map_all = {}
        for lang, strings in get_all_string_files(self.rom, self.static_data):
            rename_dungeon_map = {}
            rename_dungeon_map_all[lang] = rename_dungeon_map
            for main, sele, sdba, bann in zip(
                    range(dunge_names_main.begin, dunge_names_main.end),
                    range(dunge_names_sele.begin, dunge_names_sele.end),
                    range(dunge_names_sdba.begin, dunge_names_sdba.end),
                    range(dunge_names_bann.begin, dunge_names_bann.end),
            ):
                orig_name = strings.strings[main]
                new_name = self._generate_name()
                rename_dungeon_map[orig_name] = new_name
                strings.strings[main] = new_name
                strings.strings[sele] = new_name
                strings.strings[sdba] = new_name
                strings.strings[bann] = new_name

            for i in range(ground_map_names.begin, ground_map_names.end):
                orig_name = strings.strings[i]
                if orig_name in rename_dungeon_map:
                    new_name = rename_dungeon_map[orig_name]
                else:
                    new_name = self._generate_name()
                rename_dungeon_map[orig_name] = new_name
                strings.strings[i] = new_name

            self.rom.setFileByName(f'MESSAGE/{lang.filename}', FileType.STR.serialize(strings))

        status.step("Replacing script text that mentions locations...")
        replace_text_script(self.rom, self.static_data, rename_dungeon_map_all)

        status.done()

    def _generate_name(self) -> str:
        return random_txt_line(self.config['locations']['first']) + " " + random_txt_line(self.config['locations']['second'])
