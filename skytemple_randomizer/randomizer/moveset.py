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
from skytemple_files.data.md.model import PokeType, Md
from skytemple_files.data.waza_p.model import WazaP
from skytemple_randomizer.config import MovesetConfig
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_allowed_move_ids, MoveRoster
from skytemple_randomizer.status import Status


class MovesetRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config['pokemon']['movesets'] != MovesetConfig.NO:
            return 1
        return 0

    def run(self, status: Status):
        if self.config['pokemon']['movesets'] == MovesetConfig.NO:
            return status.done()
        status.step("Randomizing movesets...")
        md: Md = FileType.MD.deserialize(self.rom.getFileByName('BALANCE/monster.md'))
        waza_p: WazaP = FileType.WAZA_P.deserialize(self.rom.getFileByName('BALANCE/waza_p.bin'))

        valid_move_ids = get_allowed_move_ids(self.config)
        damaging_move_ids = get_allowed_move_ids(self.config, MoveRoster.DAMAGING)

        for md_entry, waza_p_entry in zip(md.entries, waza_p.learnsets):
            waza_p_entry.egg_moves = [choice(valid_move_ids) for _ in waza_p_entry.egg_moves]
            # Don't randomize, since not all have TM/HSs
            #waza_p_entry.tm_hm_moves = [choice(VALID_MOVE_IDS) for _ in waza_p_entry.tm_hm_moves]

            for idx, e in enumerate(waza_p_entry.level_up_moves):
                if idx > 0 or self.config['pokemon']['movesets'] == MovesetConfig.FULLY_RANDOM:
                    e.move_id = choice(valid_move_ids)
                elif self.config['pokemon']['movesets'] == MovesetConfig.FIRST_DAMAGE:
                    e.move_id = choice(damaging_move_ids)
                elif self.config['pokemon']['movesets'] == MovesetConfig.FIRST_STAB:
                    e.move_id = choice(get_allowed_move_ids(self.config, MoveRoster.STAB, md_entry.type_primary))

        self.rom.setFileByName('BALANCE/waza_p.bin', FileType.WAZA_P.serialize(waza_p))

        status.done()
