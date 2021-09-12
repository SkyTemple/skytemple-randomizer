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
from random import choice

from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_binary_from_rom_ppmdu, set_binary_in_rom_ppmdu
from skytemple_files.data.md.model import Md
from skytemple_files.hardcoded.guest_pokemon import GuestPokemonList
from skytemple_files.list.actor.model import ActorListBin
from skytemple_files.patch.patches import Patcher
from skytemple_randomizer.config import MovesetConfig
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import MoveRoster, get_allowed_move_ids
from skytemple_randomizer.status import Status

# Maps actor list indices to guest Pokémon indices
ACTOR_TO_GUEST_MAPPING = {
    291: [0],
    292: [1],
    124: [2, 4, 14, 15],
    279: [3, 17],
    105: [5, 8, 11, 12],
    109: [6],
    136: [7],
    131: [9],
    104: [10],
    144: [13],
    311: [16]
}


class GuestRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        guest_poke_moves = (1 if self.config['pokemon']['movesets'] else 0)
        if self.config['starters_npcs']['npcs']:
            return 2 + guest_poke_moves
        return 1 + guest_poke_moves

    def run(self, status: Status):
        status.step("Apply 'EditExtraPokemon' patch...")
        patcher = Patcher(self.rom, self.static_data)
        if not patcher.is_applied('EditExtraPokemon'):
            patcher.apply('EditExtraPokemon')
        arm9 = bytearray(get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin']))
        guests = GuestPokemonList.read(arm9, self.static_data)

        if self.config['starters_npcs']['npcs']:
            status.step("Updating guest Pokémon...")

            actor_list: ActorListBin = FileType.SIR0.unwrap_obj(
                FileType.SIR0.deserialize(self.rom.getFileByName('BALANCE/actor_list.bin')), ActorListBin
            )

            for i, actor in enumerate(actor_list.list):
                if i in ACTOR_TO_GUEST_MAPPING:
                    for bi in ACTOR_TO_GUEST_MAPPING[i]:
                        guests[bi].poke_id = actor.entid

        if self.config['pokemon']['movesets'] != MovesetConfig.NO:
            status.step("Updating guest Pokémon movesets...")

            valid_move_ids = get_allowed_move_ids(self.config)
            damaging_move_ids = get_allowed_move_ids(self.config, MoveRoster.DAMAGING)
        
            md: Md = FileType.MD.deserialize(self.rom.getFileByName('BALANCE/monster.md'))
            for guest in guests:
                if self.config['pokemon']['movesets'] == MovesetConfig.FULLY_RANDOM:
                    guest.moves = [choice(valid_move_ids), choice(valid_move_ids), choice(valid_move_ids), choice(valid_move_ids)]
                elif self.config['pokemon']['movesets'] == MovesetConfig.FIRST_DAMAGE:
                    guest.moves = [choice(damaging_move_ids), choice(valid_move_ids), choice(valid_move_ids), choice(valid_move_ids)]
                elif self.config['pokemon']['movesets'] == MovesetConfig.FIRST_STAB:
                    md_entry = md.entries[guest.poke_id]
                    first = choice(get_allowed_move_ids(self.config, MoveRoster.STAB, md_entry.type_primary))
                    guest.moves = [first, choice(valid_move_ids), choice(valid_move_ids), choice(valid_move_ids)]

        GuestPokemonList.write(guests, arm9, self.static_data)
        set_binary_in_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin'], arm9)

        status.done()
