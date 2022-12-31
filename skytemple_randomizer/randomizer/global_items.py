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

from ndspy.rom import NintendoDSRom
from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.list.items.handler import ItemListHandler
from skytemple_files.patch.patches import Patcher

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.abstract import AbstractFrontend
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.common.items import randomize_items
from skytemple_randomizer.status import Status

ITEM_LIST_COUNT = 25


class GlobalItemsRandomizer(AbstractRandomizer):
    def __init__(self, config: RandomizerConfig, rom: NintendoDSRom, static_data: Pmd2Data, seed: str, frontend: AbstractFrontend):
        super().__init__(config, rom, static_data, seed, frontend)

    def step_count(self) -> int:
        return 2 if self.config['item']['global_items'] else 0

    def run(self, status: Status):
        if not self.config['item']['global_items']:
            return

        status.step("Apply patches...")
        patcher = Patcher(self.rom, self.static_data)
        if not patcher.is_applied('ActorAndLevelLoader'):
            patcher.apply('ActorAndLevelLoader')
        if not patcher.is_applied('ExtractHardcodedItemLists'):
            patcher.apply('ExtractHardcodedItemLists')

        status.step("Randomizing global item lists...")
        for i in range(0, ITEM_LIST_COUNT):
            self.rom.setFileByName(
                f'TABLEDAT/list_{i:02}.bin',
                ItemListHandler.serialize(randomize_items(self.config, self.static_data))
            )

        status.done()
