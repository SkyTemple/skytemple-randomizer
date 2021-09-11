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
from skytemple_files.hardcoded.default_starters import HardcodedDefaultStarters
from skytemple_files.list.actor.model import ActorListBin
from skytemple_randomizer.config import MovesetConfig
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.moveset import VALID_MOVE_IDS, DAMAGING_MOVES, STAB_DICT
from skytemple_randomizer.status import Status

# Maps actor list indices to special PC indices
ACTOR_TO_SPC_MAPPING = {
    104: [0],
    6: [1],
    5: [3],
    7: [4],
    8: [8],
    9: [7],
    112: [2],
    191: [5],
    136: [6],
    293: [9]
}


class SpecialPcRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        sp_poke_moves = (1 if self.config['pokemon']['movesets'] else 0)
        if self.config['starters_npcs']['npcs']:
            return 1 + sp_poke_moves
        return 0 + sp_poke_moves

    def run(self, status: Status):
        arm9 = bytearray(get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin']))
        pcs = HardcodedDefaultStarters.get_special_episode_pcs(arm9, self.static_data)

        if self.config['starters_npcs']['npcs']:
            status.step("Updating special episode Pokémon...")

            actor_list: ActorListBin = FileType.SIR0.unwrap_obj(
                FileType.SIR0.deserialize(self.rom.getFileByName('BALANCE/actor_list.bin')), ActorListBin
            )

            for i, actor in enumerate(actor_list.list):
                if i in ACTOR_TO_SPC_MAPPING:
                    for bi in ACTOR_TO_SPC_MAPPING[i]:
                        pcs[bi].poke_id = actor.entid

        if self.config['pokemon']['movesets'] != MovesetConfig.NO:
            status.step("Updating special episode Pokémon movesets...")
            md: Md = FileType.MD.deserialize(self.rom.getFileByName('BALANCE/monster.md'))
            for pc in pcs:
                pc.move2 = choice(VALID_MOVE_IDS)
                pc.move3 = choice(VALID_MOVE_IDS)
                pc.move4 = choice(VALID_MOVE_IDS)
                pc.do_not_fix_entire_moveset = False
                if self.config['pokemon']['movesets'] == MovesetConfig.FULLY_RANDOM:
                    pc.move1 = choice(VALID_MOVE_IDS)
                elif self.config['pokemon']['movesets'] == MovesetConfig.FIRST_DAMAGE:
                    pc.move1 = choice(DAMAGING_MOVES)
                elif self.config['pokemon']['movesets'] == MovesetConfig.FIRST_STAB:
                    md_entry = md.entries[pc.poke_id]
                    if md_entry.type_primary not in STAB_DICT:
                        pc.move1 = choice(DAMAGING_MOVES)
                    else:
                        pc.move1 = choice(STAB_DICT[md_entry.type_primary])

        HardcodedDefaultStarters.set_special_episode_pcs(pcs, arm9, self.static_data)
        set_binary_in_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin'], arm9)

        status.done()
