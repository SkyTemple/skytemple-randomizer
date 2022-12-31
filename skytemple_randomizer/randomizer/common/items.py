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
from collections import OrderedDict
from math import ceil
from numbers import Number
from random import choice, randrange
from typing import List, Dict

from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.common.types.file_types import FileType
from skytemple_files.dungeon_data.mappa_bin import MAX_WEIGHT
from skytemple_files.dungeon_data.mappa_bin.protocol import MappaItemListProtocol

from skytemple_randomizer.config import RandomizerConfig, ItemAlgorithm
from skytemple_randomizer.randomizer.common.weights import random_weights
from skytemple_randomizer.randomizer.util.util import get_allowed_item_ids

CLASSIC_ALLOWED_ITEM_CATS = [
    0, 1, 2, 3, 4, 5, 8, 9
]
ALLOWED_ITEM_CATS = [
    0, 1, 2, 3, 4, 5, 6, 8, 9, 10
]
MIN_ITEMS_PER_CAT = 4
MAX_ITEMS_PER_CAT = 18


def randomize_items(config: RandomizerConfig, static_data: Pmd2Data) -> MappaItemListProtocol:
    if config['item']['algorithm'] == ItemAlgorithm.BALANCED:
        return balanced_item_randomizer(config, static_data)
    if config['item']['algorithm'] == ItemAlgorithm.CLASSIC:
        return classic_item_randomizer(config, static_data)

    raise NotImplementedError("Unknown item algorithm.")


def classic_item_randomizer(config: RandomizerConfig, static_data: Pmd2Data) -> MappaItemListProtocol:
    categories = {}
    items = OrderedDict()
    cats_as_list = list(CLASSIC_ALLOWED_ITEM_CATS)

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


def balanced_item_randomizer(config: RandomizerConfig, static_data: Pmd2Data) -> MappaItemListProtocol:
    categories = OrderedDict()
    items = OrderedDict()

    min_items = MIN_ITEMS_PER_CAT * len(ALLOWED_ITEM_CATS)
    max_items = MAX_ITEMS_PER_CAT * len(ALLOWED_ITEM_CATS)
    items_in_cats: Dict[int, List[int]] = {}
    chosen_items_per_cat: Dict[int, List[int]] = {}

    cats_as_list = list(ALLOWED_ITEM_CATS)

    # Take note of all allowed items and which categories they are in
    all_allowed_item_ids = []
    for cat_id in cats_as_list:
        cat = static_data.dungeon_data.item_categories[cat_id]
        items_in_cats[cat_id] = [x for x in cat.item_ids() if x in get_allowed_item_ids(config)]
        all_allowed_item_ids.extend(items_in_cats[cat_id])

    # We roll random items and then check their category.
    # We also take note of the items for that category in chosen_items_per_cat.
    for _ in range(0, randrange(min_items, max_items)):
        if len(all_allowed_item_ids) < 1:
            break
        item_index = choice(range(0, len(all_allowed_item_ids)))
        item_id = all_allowed_item_ids.pop(item_index)
        item_cat_id = -1
        for cat_id, items_in_this_cat in items_in_cats.items():
            if item_id in items_in_this_cat:
                item_cat_id = cat_id
                break
        if item_cat_id not in chosen_items_per_cat:
            chosen_items_per_cat[item_cat_id] = []
        chosen_items_per_cat[item_cat_id].append(item_id)

    chosen_items_per_cat = dict(sorted(chosen_items_per_cat.items()))

    # Calculate the category weights based on the number of items in each category
    # First we take into account the weight multipliers
    weighted_chosen_items_per_cat_count = {}
    for cat_id, chosen_items in chosen_items_per_cat.items():
        #  'int' is not a 'Number' according to mypy??
        weight_multiplier: Number = 1  # type: ignore
        if cat_id in config['item']['weights']:
            weight_multiplier = config['item']['weights'][cat_id]
            if weight_multiplier <= 0:  # type: ignore
                weight_multiplier = 0.01  # type: ignore
        weighted_chosen_items_per_cat_count[cat_id] = ceil(len(chosen_items) * weight_multiplier)  # type: ignore
    weights_before = 0
    total_items_weighted = sum(item_count_weighted for item_count_weighted in weighted_chosen_items_per_cat_count.values())
    for cat_id, chosen_items in chosen_items_per_cat.items():
        item_count_weighted = weighted_chosen_items_per_cat_count[cat_id]
        categories[cat_id] = weights_before + ceil(MAX_WEIGHT * (item_count_weighted / total_items_weighted))
        weights_before = categories[cat_id]

        # Randomize the item weights in each category
        cat_weights = sorted(random_weights(len(chosen_items)))

        for item_id, weight in zip(sorted(chosen_items), cat_weights):
            items[item_id] = weight

    categories[next(reversed(categories))] = MAX_WEIGHT

    return FileType.MAPPA_BIN.get_item_list_model()(
        categories,
        dict(sorted(items.items(), key=lambda i: i[0]))
    )
