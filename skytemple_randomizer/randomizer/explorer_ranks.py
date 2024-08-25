#  Copyright 2020-2024 Capypara and the SkyTemple Contributors
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
from range_typed_integers import u32
from skytemple_files.common.util import get_binary_from_rom, set_binary_in_rom
from skytemple_files.hardcoded.rank_up_table import HardcodedRankUpTable
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_allowed_item_ids
from skytemple_randomizer.status import Status
from skytemple_files.common.i18n_util import _

MIN_PNTS = u32(1)
MAX_UNLOCK_PNTS = u32(100000)


class ExplorerRanksRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if (
            self.config["starters_npcs"]["explorer_rank_rewards"]
            or self.config["starters_npcs"]["explorer_rank_unlocks"]
        ):
            return 1
        return 0

    def run(self, status: Status):
        rand_rewards = self.config["starters_npcs"]["explorer_rank_rewards"]
        rand_unlocks = self.config["starters_npcs"]["explorer_rank_unlocks"]
        if not rand_rewards and not rand_unlocks:
            return status.done()

        status.step(_("Randomizing rank data..."))
        arm9 = bytearray(get_binary_from_rom(self.rom, self.static_data.bin_sections.arm9))
        ranks = HardcodedRankUpTable.get_rank_up_table(arm9, self.static_data)

        if rand_unlocks:
            unlocks = []
            for i in range(len(ranks) - 1):
                unlocks.append(u32(self.rng.randint(MIN_PNTS, MAX_UNLOCK_PNTS)))
            unlocks.append(ranks[-1].points_needed_next)
            unlocks.sort()

            # Sort unlocks by distance to next rank
            previous_points_needed = 0
            points_to_next_array = []
            for points_needed in unlocks:
                points_to_next_array.append(points_needed - previous_points_needed)
                previous_points_needed = points_needed
            points_to_next_array.sort()

            # Rebuild unlocks array
            for i, points_to_next in enumerate(points_to_next_array):
                previous_unlock = 0 if i == 0 else unlocks[i - 1]
                unlocks[i] = u32(previous_unlock + points_to_next)

        for i in range(len(ranks)):
            if rand_unlocks:
                # noinspection PyUnboundLocalVariable
                ranks[i].points_needed_next = unlocks[i]
            if rand_rewards:
                ranks[i].item_awarded = u32(self.rng.choice(get_allowed_item_ids(self.config)))

        HardcodedRankUpTable.set_rank_up_table(ranks, arm9, self.static_data)
        set_binary_in_rom(self.rom, self.static_data.bin_sections.arm9, arm9)

        status.done()
