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
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_binary_from_rom_ppmdu, set_binary_in_rom_ppmdu
from skytemple_files.hardcoded.recruitment_tables import HardcodedRecruitmentTables
from skytemple_files.list.actor.model import ActorListBin
from skytemple_files.patch.patches import Patcher
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.status import Status

ACTOR_TO_RECRUIT_MAPPING = {21: [16], 120: [0], 121: [1], 122: [2], 123: [3], 137: [4], 138: [5], 139: [6],
                            140: [7], 141: [8], 142: [9], 143: [10], 144: [18], 145: [17], 146: [17], 147: [17],
                            148: [17], 149: [17], 150: [17], 151: [17], 152: [17], 153: [16], 154: [11], 195: [12],
                            209: [13, 14], 211: [15], 215: [4], 216: [6], 217: [5], 230: [9], 255: [7], 256: [11],
                            257: [18], 271: [19], 272: [20], 311: [21], 312: [21], 313: [21], 314: [21], 315: [21],
                            316: [21], 366: [21]}


class RecruitmentTableRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config['starters_npcs']['npcs']:
            return 2
        return 0

    def run(self, status: Status):
        if not self.config['starters_npcs']['npcs']:
            return status.done()

        status.step("Apply 'ActorAndLevelLoader' patch...")
        patcher = Patcher(self.rom, self.static_data)
        if not patcher.is_applied('ActorAndLevelLoader'):
            patcher.apply('ActorAndLevelLoader')

        status.step("Updating special recruitment table...")

        actor_list: ActorListBin = FileType.SIR0.unwrap_obj(
            FileType.SIR0.deserialize(self.rom.getFileByName('BALANCE/actor_list.bin')), ActorListBin
        )

        binary = get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['overlay/overlay_0011.bin'])
        sp_list = HardcodedRecruitmentTables.get_monster_species_list(binary, self.static_data)

        for i, actor in enumerate(actor_list.list):
            if i in ACTOR_TO_RECRUIT_MAPPING:
                for bi in ACTOR_TO_RECRUIT_MAPPING[i]:
                    sp_list[bi] = actor.entid

        HardcodedRecruitmentTables.set_monster_species_list(sp_list, binary, self.static_data)
        set_binary_in_rom_ppmdu(self.rom, self.static_data.binaries['overlay/overlay_0011.bin'], binary)

        status.done()
