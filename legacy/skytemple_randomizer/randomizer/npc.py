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
from random import choice, randrange
from typing import Dict

from range_typed_integers import u16
from skytemple_files.common.types.file_types import FileType
from skytemple_files.data.md.protocol import Gender
from skytemple_files.data.str.model import Str
from skytemple_files.list.actor.model import ActorListBin
from skytemple_files.patch.patches import Patcher
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_main_string_file, get_allowed_md_ids, replace_text_main, \
    replace_text_script, clone_missing_portraits, get_all_string_files, Roster
from skytemple_randomizer.status import Status


class NpcRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config['starters_npcs']['npcs']:
            return 5
        return 0

    def run(self, status: Status):
        if not self.config['starters_npcs']['npcs']:
            return status.done()
        lang, string_file = get_main_string_file(self.rom, self.static_data)
        pokemon_string_data = self.static_data.string_index_data.string_blocks["Pokemon Names"]

        status.step("Apply 'ActorAndLevelLoader' patch...")
        patcher = Patcher(self.rom, self.static_data)
        if not patcher.is_applied('ActorAndLevelLoader'):
            patcher.apply('ActorAndLevelLoader')

        status.step("Randomizing NPC actor list...")
        mapped_actors = self._randomize_actors(string_file, pokemon_string_data)

        status.step("Replacing main text that mentions NPCs...")
        names_mapped_all = {}
        for lang, string_file in get_all_string_files(self.rom, self.static_data):
            names_mapped: Dict[str, str] = {}
            names_mapped_all[lang] = names_mapped
            for old, new in mapped_actors.items():
                old_base = old % 600
                new_base = new % 600
                old_name = self._get_name(string_file, old_base, pokemon_string_data)
                new_name = self._get_name(string_file, new_base, pokemon_string_data)
                names_mapped[old_name] = new_name
            replace_text_main(string_file, names_mapped, pokemon_string_data.begin, pokemon_string_data.end)
            self.rom.setFileByName(f'MESSAGE/{lang.filename}', FileType.STR.serialize(string_file))

        status.step("Replacing script text that mentions NPCs...")
        replace_text_script(self.rom, self.static_data, names_mapped_all)

        status.step("Cloning missing NPC portraits...")
        kao = FileType.KAO.deserialize(self.rom.getFileByName('FONT/kaomado.kao'))
        for new in mapped_actors.values():
            new_base = new % 600
            clone_missing_portraits(kao, new_base - 1)
        self.rom.setFileByName('FONT/kaomado.kao', FileType.KAO.serialize(kao))

        status.done()

    def _randomize_actors(self, string_file, pokemon_string_data) -> Dict[int, int]:
        """Returns a dict that maps old entids -> new entids"""
        actor_list: ActorListBin = FileType.SIR0.unwrap_obj(
            FileType.SIR0.deserialize(self.rom.getFileByName('BALANCE/actor_list.bin')), ActorListBin
        )
        md = FileType.MD.deserialize(self.rom.getFileByName('BALANCE/monster.md'))

        mapped: Dict[int, int] = {}
        # We want to map actors with the same name to the same ID
        mapped_for_names: Dict[str, u16] = {}
        num_entities = FileType.MD.properties().num_entities
        old_entid_bases = [actor.entid % num_entities for actor in actor_list.list]
        new_entid: u16
        for actor in actor_list.list:
            if actor.entid > 0:
                old_name = self._get_name(string_file, actor.entid % num_entities, pokemon_string_data)
                if old_name in mapped_for_names.keys():
                    new_entid = mapped_for_names[old_name]
                    if new_entid >= 1154:
                        new_entid -= u16(num_entities)  # type: ignore
                else:
                    new_entid = choice(get_allowed_md_ids(self.config, True, roster=Roster.NPCS))
                    # Make it less likely to get duplicates
                    while new_entid in mapped.values() and randrange(0, 4) != 0:
                        new_entid = choice(get_allowed_md_ids(self.config, True, roster=Roster.NPCS))
                    # Due to the way the string replacing works we don't want anything that previously existed.
                    while md.get_by_index(new_entid).gender == Gender.INVALID or new_entid % num_entities in old_entid_bases:
                        new_entid = choice(get_allowed_md_ids(self.config, True, roster=Roster.NPCS))
                mapped[actor.entid] = new_entid
                mapped_for_names[old_name] = new_entid
                actor.entid = new_entid

        self.rom.setFileByName(
            'BALANCE/actor_list.bin', FileType.SIR0.serialize(FileType.SIR0.wrap_obj(actor_list))
        )
        return mapped

    @staticmethod
    def _get_name(string_file: Str, index: int, pokemon_string_data):
        """Returns a Pokémon name from the string file"""
        return string_file.strings[pokemon_string_data.begin + index]
