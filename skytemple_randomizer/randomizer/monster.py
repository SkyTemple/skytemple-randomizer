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
from skytemple_files.data.md.model import Md, NUM_ENTITIES, IQGroup, PokeType, Ability
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.status import Status

VALID_IQ_GROUPS = [
    IQGroup.A, IQGroup.B, IQGroup.C, IQGroup.D, IQGroup.E, IQGroup.F,
    IQGroup.G, IQGroup.H, IQGroup.I, IQGroup.J
]
VALID_FIRST_TYPE = [
    PokeType.NORMAL, PokeType.FIRE, PokeType.WATER, PokeType.GRASS,
    PokeType.ELECTRIC, PokeType.ICE, PokeType.FIGHTING, PokeType.FIGHTING, PokeType.POISON,
    PokeType.GROUND, PokeType.FLYING, PokeType.PSYCHIC, PokeType.BUG, PokeType.ROCK,
    PokeType.GHOST, PokeType.DRAGON, PokeType.DARK, PokeType.STEEL
]
VALID_SECOND_TYPE = VALID_FIRST_TYPE + [PokeType.NONE]


class MonsterRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self._has_something_to_randomize():
            return 1
        return 0

    def run(self, status: Status):
        if not self._has_something_to_randomize():
            return status.done()
        status.step("Randomizing Pokémon data...")
        md: Md = FileType.MD.deserialize(self.rom.getFileByName('BALANCE/monster.md'))
        for midx in range(0, NUM_ENTITIES):
            if len(md.entries) <= midx + NUM_ENTITIES:
                continue
            base_entry = md.entries[midx]
            secn_entry = md.entries[midx + NUM_ENTITIES]
            if self.config['pokemon']['iq_groups']:
                group = choice(VALID_IQ_GROUPS)
                base_entry.iq_group = group
                secn_entry.iq_group = group

            if self.config['pokemon']['typings']:
                type1 = choice(VALID_FIRST_TYPE)
                type2 = choice(VALID_SECOND_TYPE)
                while type1 == type2:
                    type2 = choice(VALID_SECOND_TYPE)
                base_entry.type_primary = type1
                secn_entry.type_primary = type1
                base_entry.type_secondary = type2
                secn_entry.type_secondary = type2

            if self.config['pokemon']['abilities']:
                ability_ids = self.config['pokemon']['abilities_enabled'] + [Ability.NONE.value]
                if len(ability_ids) > 0:
                    ability1 = Ability(choice(ability_ids))
                    ability2 = Ability(choice(ability_ids))
                    while ability2 == ability1:
                        ability2 = Ability(choice(ability_ids))
                    base_entry.ability_primary = ability1
                    base_entry.ability_secondary = ability2
                    secn_entry.ability_primary = ability1
                    secn_entry.ability_secondary = ability2

        self.rom.setFileByName('BALANCE/monster.md', FileType.MD.serialize(md))

        status.done()

    def _has_something_to_randomize(self):
        return self.config['pokemon']['iq_groups'] or \
               self.config['pokemon']['typings'] or \
               self.config['pokemon']['abilities']
