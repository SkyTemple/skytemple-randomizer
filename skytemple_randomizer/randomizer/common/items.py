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
from collections import OrderedDict
from random import choice, randrange
from typing import List

from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.common.types.file_types import FileType
from skytemple_files.dungeon_data.mappa_bin.protocol import MappaItemListProtocol

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.randomizer.common.weights import random_weights
from skytemple_randomizer.randomizer.util.util import get_allowed_item_ids

ALLOWED_ITEM_CATS = [
    0, 1, 2, 3, 4, 5, 9, 8
]
MIN_ITEMS_PER_CAT = 4
MAX_ITEMS_PER_CAT = 18


def randomize_items(config: RandomizerConfig, static_data: Pmd2Data) -> MappaItemListProtocol:
    categories = {}
    items = OrderedDict()
    cats_as_list = list(ALLOWED_ITEM_CATS)

    # 1/8 chance for money to get a chance
    if choice([True] + [False] * 7):
        cats_as_list.append(6)

    # 1/8 chance for Link Box to get a chance
    if choice([True] + [False] * 7):
        cats_as_list.append(10)

    cats_as_list.sort()
    weights = sorted(random_weights(len(cats_as_list)))
    for i, cat_id in enumerate(cats_as_list):
        cat = static_data.dungeon_data.item_categories[cat_id]
        categories[cat.id] = weights[i]

        cat_item_ids: List[int] = []
        if cat.number_of_items is not None:
            allowed_cat_item_ids = [x for x in cat.item_ids() if x in get_allowed_item_ids(config)]
            upper_limit = min(MAX_ITEMS_PER_CAT, len(allowed_cat_item_ids))
            if upper_limit <= MIN_ITEMS_PER_CAT:
                n_items = MIN_ITEMS_PER_CAT
            else:
                n_items = randrange(MIN_ITEMS_PER_CAT, upper_limit)
            cat_item_ids = []
            if len(allowed_cat_item_ids) > 0:
                cat_item_ids = sorted(set(
                    (choice(allowed_cat_item_ids) for _ in range(0, n_items))
                ))
                cat_weights = sorted(random_weights(len(cat_item_ids)))

                for item_id, weight in zip(cat_item_ids, cat_weights):
                    items[item_id] = weight
        if len(cat_item_ids) == 0:
            categories[cat.id] = 0

    return FileType.MAPPA_BIN.get_item_list_model()(
        categories,
        dict(sorted(items.items(), key=lambda i: i[0]))
    )

