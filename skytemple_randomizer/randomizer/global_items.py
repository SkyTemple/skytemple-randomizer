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
from collections import OrderedDict
from random import choice, randrange

from ndspy.rom import NintendoDSRom

from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.common.ppmdu_config.dungeon_data import Pmd2DungeonItem
from skytemple_files.dungeon_data.mappa_bin import MAX_WEIGHT
from skytemple_files.dungeon_data.mappa_bin.item_list import MappaItemCategory, MappaItemList
from skytemple_files.list.items.handler import ItemListHandler
from skytemple_files.patch.patches import Patcher
from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.dungeon import ALLOWED_ITEM_CATS, ALLOWED_ITEM_IDS, \
    MAX_ITEMS_PER_CAT, MIN_ITEMS_PER_CAT
from skytemple_randomizer.randomizer.util.util import sample_with_minimum_distance
from skytemple_randomizer.status import Status
ITEM_LIST_COUNT = 25


class GlobalItemsRandomizer(AbstractRandomizer):
    def __init__(self, config: RandomizerConfig, rom: NintendoDSRom, static_data: Pmd2Data, seed: str):
        super().__init__(config, rom, static_data, seed)

    def step_count(self) -> int:
        return 2 if self.config['starters_npcs']['global_items'] else 0

    def run(self, status: Status):
        if not self.config['starters_npcs']['global_items']:
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
                ItemListHandler.serialize(self._randomize_items())
            )

        status.done()

    @staticmethod
    def _random_weights(k):
        """
        Returns k random weights, with relative equal distance, in a range of *0.75-*1
        """
        smallest_possible_d = int(MAX_WEIGHT / k)
        d = int(smallest_possible_d * (randrange(75, 100) / 100))
        # We actually subtract the d and add it later to all of the items,
        # to make the first entry also a bit more likely
        weights = [w + d for w in sample_with_minimum_distance(MAX_WEIGHT - d, k, d)]
        # The last weight needs to have 10000
        highest_index = weights.index(max(weights))
        weights[highest_index] = MAX_WEIGHT
        return weights

    def _randomize_items(self):
        categories = {}
        items = OrderedDict()
        cats_as_list = list(ALLOWED_ITEM_CATS)

        # 1/8 chance for money to get a chance
        if choice([True] + [False] * 7):
            cats_as_list.append(MappaItemCategory.POKE)

        # 1/8 chance for Link Box to get a chance
        if choice([True] + [False] * 7):
            cats_as_list.append(MappaItemCategory.LINK_BOX)

        cats_as_list.sort(key=lambda x: x.value)
        weights = sorted(self._random_weights(len(cats_as_list)))
        for i, cat in enumerate(cats_as_list):
            categories[cat] = weights[i]

            if cat.number_of_items is not None:
                allowed_cat_item_ids = [x for x in cat.item_ids() if x in ALLOWED_ITEM_IDS]
                upper_limit = min(MAX_ITEMS_PER_CAT, len(allowed_cat_item_ids))
                if upper_limit <= MIN_ITEMS_PER_CAT:
                    n_items = MIN_ITEMS_PER_CAT
                else:
                    n_items = randrange(MIN_ITEMS_PER_CAT, upper_limit)
                cat_item_ids = sorted(set(
                    (choice(allowed_cat_item_ids) for _ in range(0, n_items))
                ))
                cat_weights = sorted(self._random_weights(len(cat_item_ids)))

                for item_id, weight in zip(cat_item_ids, cat_weights):
                    items[Pmd2DungeonItem(item_id, '???')] = weight

        return MappaItemList(categories, OrderedDict(sorted(items.items(), key=lambda i: i[0].id)))
