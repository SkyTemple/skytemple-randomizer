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
from collections import OrderedDict
from random import choice, randrange
from typing import Optional, List

from ndspy.rom import NintendoDSRom

from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.common.ppmdu_config.dungeon_data import Pmd2DungeonItem
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_binary_from_rom_ppmdu
from skytemple_files.dungeon_data.mappa_bin import MAX_WEIGHT
from skytemple_files.dungeon_data.mappa_bin.floor import MappaFloor
from skytemple_files.dungeon_data.mappa_bin.floor_layout import MappaFloorSecondaryTerrainType, MappaFloorLayout, \
    MappaFloorStructureType, MappaFloorWeather, MappaFloorTerrainSettings, MappaFloorDarknessLevel
from skytemple_files.dungeon_data.mappa_bin.item_list import MAX_ITEM_ID, MappaItemCategory, MappaItemList
from skytemple_files.dungeon_data.mappa_bin.model import MappaBin
from skytemple_files.dungeon_data.mappa_bin.monster import MappaMonster, DUMMY_MD_INDEX
from skytemple_files.dungeon_data.mappa_bin.trap_list import MappaTrapList
from skytemple_files.dungeon_data.mappa_g_bin.mappa_converter import convert_mappa_to_mappag
from skytemple_files.hardcoded.dungeons import HardcodedDungeons
from skytemple_randomizer.config import DungeonWeatherConfig, RandomizerConfig, DungeonModeConfig
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import sample_with_minimum_distance, get_allowed_md_ids
from skytemple_randomizer.status import Status

SECONDARY_TERRAIN_TILESET_MAP = {
    0: MappaFloorSecondaryTerrainType.NONE,
    1: MappaFloorSecondaryTerrainType.NONE,
    170: MappaFloorSecondaryTerrainType.NONE,
    2: MappaFloorSecondaryTerrainType.NONE,
    3: MappaFloorSecondaryTerrainType.NONE,
    171: MappaFloorSecondaryTerrainType.NONE,
    4: MappaFloorSecondaryTerrainType.NONE,
    5: MappaFloorSecondaryTerrainType.NONE,
    6: MappaFloorSecondaryTerrainType.NONE,
    7: MappaFloorSecondaryTerrainType.NONE,
    8: MappaFloorSecondaryTerrainType.NONE,
    9: MappaFloorSecondaryTerrainType.NONE,
    10: MappaFloorSecondaryTerrainType.NONE,
    11: MappaFloorSecondaryTerrainType.NONE,
    12: MappaFloorSecondaryTerrainType.NONE,
    172: MappaFloorSecondaryTerrainType.NONE,
    14: MappaFloorSecondaryTerrainType.NONE,
    15: MappaFloorSecondaryTerrainType.NONE,
    173: MappaFloorSecondaryTerrainType.NONE,
    17: MappaFloorSecondaryTerrainType.HAS_1,
    18: MappaFloorSecondaryTerrainType.NONE,
    19: MappaFloorSecondaryTerrainType.NONE,
    20: MappaFloorSecondaryTerrainType.NONE,
    174: MappaFloorSecondaryTerrainType.NONE,
    22: MappaFloorSecondaryTerrainType.NONE,
    23: MappaFloorSecondaryTerrainType.NONE,
    24: MappaFloorSecondaryTerrainType.NONE,
    175: MappaFloorSecondaryTerrainType.NONE,
    26: MappaFloorSecondaryTerrainType.NONE,
    27: MappaFloorSecondaryTerrainType.NONE,
    28: MappaFloorSecondaryTerrainType.NONE,
    29: MappaFloorSecondaryTerrainType.NONE,
    30: MappaFloorSecondaryTerrainType.NONE,
    31: MappaFloorSecondaryTerrainType.NONE,
    176: MappaFloorSecondaryTerrainType.NONE,
    33: MappaFloorSecondaryTerrainType.NONE,
    34: MappaFloorSecondaryTerrainType.NONE,
    35: MappaFloorSecondaryTerrainType.NONE,
    36: MappaFloorSecondaryTerrainType.NONE,
    37: MappaFloorSecondaryTerrainType.NONE,
    38: MappaFloorSecondaryTerrainType.NONE,
    39: MappaFloorSecondaryTerrainType.NONE,
    40: MappaFloorSecondaryTerrainType.HAS_10,
    177: MappaFloorSecondaryTerrainType.NONE,
    42: MappaFloorSecondaryTerrainType.NONE,
    43: MappaFloorSecondaryTerrainType.NONE,
    178: MappaFloorSecondaryTerrainType.NONE,
    45: MappaFloorSecondaryTerrainType.NONE,
    46: MappaFloorSecondaryTerrainType.NONE,
    179: MappaFloorSecondaryTerrainType.NONE,
    48: MappaFloorSecondaryTerrainType.NONE,
    180: MappaFloorSecondaryTerrainType.NONE,
    113: MappaFloorSecondaryTerrainType.NONE,
    119: MappaFloorSecondaryTerrainType.NONE,
    106: MappaFloorSecondaryTerrainType.NONE,
    118: MappaFloorSecondaryTerrainType.HAS_10,
    51: MappaFloorSecondaryTerrainType.NONE,
    52: MappaFloorSecondaryTerrainType.NONE,
    50: MappaFloorSecondaryTerrainType.NONE,
    108: MappaFloorSecondaryTerrainType.NONE,
    62: MappaFloorSecondaryTerrainType.NONE,
    61: MappaFloorSecondaryTerrainType.NONE,
    91: MappaFloorSecondaryTerrainType.NONE,
    96: MappaFloorSecondaryTerrainType.NONE,
    103: MappaFloorSecondaryTerrainType.NONE,
    88: MappaFloorSecondaryTerrainType.NONE,
    85: MappaFloorSecondaryTerrainType.NONE,
    82: MappaFloorSecondaryTerrainType.NONE,
    111: MappaFloorSecondaryTerrainType.HAS_10,
    123: MappaFloorSecondaryTerrainType.NONE,
    125: MappaFloorSecondaryTerrainType.NONE,
    59: MappaFloorSecondaryTerrainType.NONE,
    90: MappaFloorSecondaryTerrainType.NONE,
    65: MappaFloorSecondaryTerrainType.NONE,
    102: MappaFloorSecondaryTerrainType.NONE,
    105: MappaFloorSecondaryTerrainType.NONE,
    99: MappaFloorSecondaryTerrainType.NONE,
    126: MappaFloorSecondaryTerrainType.NONE,
    49: MappaFloorSecondaryTerrainType.NONE,
    127: MappaFloorSecondaryTerrainType.HAS_1,
    181: MappaFloorSecondaryTerrainType.NONE,
    69: MappaFloorSecondaryTerrainType.NONE,
    109: MappaFloorSecondaryTerrainType.NONE,
    74: MappaFloorSecondaryTerrainType.NONE,
    101: MappaFloorSecondaryTerrainType.NONE,
    81: MappaFloorSecondaryTerrainType.NONE,
    104: MappaFloorSecondaryTerrainType.NONE,
    68: MappaFloorSecondaryTerrainType.NONE,
    87: MappaFloorSecondaryTerrainType.NONE,
    79: MappaFloorSecondaryTerrainType.NONE,
    84: MappaFloorSecondaryTerrainType.NONE,
    112: MappaFloorSecondaryTerrainType.NONE,
    57: MappaFloorSecondaryTerrainType.NONE,
    58: MappaFloorSecondaryTerrainType.NONE,
    182: MappaFloorSecondaryTerrainType.NONE,
    117: MappaFloorSecondaryTerrainType.NONE,
    53: MappaFloorSecondaryTerrainType.NONE,
    54: MappaFloorSecondaryTerrainType.NONE,
    55: MappaFloorSecondaryTerrainType.NONE,
    56: MappaFloorSecondaryTerrainType.NONE,
    124: MappaFloorSecondaryTerrainType.NONE,
    63: MappaFloorSecondaryTerrainType.NONE,
    64: MappaFloorSecondaryTerrainType.NONE,
    25: MappaFloorSecondaryTerrainType.NONE,
    16: MappaFloorSecondaryTerrainType.NONE,
    114: MappaFloorSecondaryTerrainType.NONE,
    83: MappaFloorSecondaryTerrainType.NONE,
    115: MappaFloorSecondaryTerrainType.NONE,
    116: MappaFloorSecondaryTerrainType.NONE,
    97: MappaFloorSecondaryTerrainType.NONE,
    76: MappaFloorSecondaryTerrainType.NONE,
    67: MappaFloorSecondaryTerrainType.NONE,
    75: MappaFloorSecondaryTerrainType.NONE,
    110: MappaFloorSecondaryTerrainType.NONE,
    66: MappaFloorSecondaryTerrainType.NONE,
    142: MappaFloorSecondaryTerrainType.NONE,
    143: MappaFloorSecondaryTerrainType.NONE,
    94: MappaFloorSecondaryTerrainType.NONE,
    32: MappaFloorSecondaryTerrainType.NONE,
    195: MappaFloorSecondaryTerrainType.NONE,
    80: MappaFloorSecondaryTerrainType.NONE,
    184: MappaFloorSecondaryTerrainType.NONE,
    198: MappaFloorSecondaryTerrainType.NONE,
    128: MappaFloorSecondaryTerrainType.NONE,
    185: MappaFloorSecondaryTerrainType.NONE,
    132: MappaFloorSecondaryTerrainType.NONE,
    186: MappaFloorSecondaryTerrainType.NONE,
    133: MappaFloorSecondaryTerrainType.NONE,
    134: MappaFloorSecondaryTerrainType.NONE,
    135: MappaFloorSecondaryTerrainType.NONE,
    187: MappaFloorSecondaryTerrainType.NONE,
    136: MappaFloorSecondaryTerrainType.NONE,
    137: MappaFloorSecondaryTerrainType.NONE,
    138: MappaFloorSecondaryTerrainType.NONE,
    188: MappaFloorSecondaryTerrainType.NONE,
    139: MappaFloorSecondaryTerrainType.NONE,
    140: MappaFloorSecondaryTerrainType.NONE,
    141: MappaFloorSecondaryTerrainType.NONE,
    189: MappaFloorSecondaryTerrainType.NONE,
    44: MappaFloorSecondaryTerrainType.NONE,
    129: MappaFloorSecondaryTerrainType.NONE,
    190: MappaFloorSecondaryTerrainType.NONE,
    122: MappaFloorSecondaryTerrainType.NONE,
    130: MappaFloorSecondaryTerrainType.NONE,
    131: MappaFloorSecondaryTerrainType.NONE,
    191: MappaFloorSecondaryTerrainType.NONE,
    192: MappaFloorSecondaryTerrainType.NONE,
    193: MappaFloorSecondaryTerrainType.NONE,
    194: MappaFloorSecondaryTerrainType.NONE,
    78: MappaFloorSecondaryTerrainType.NONE,
    89: MappaFloorSecondaryTerrainType.NONE
}
ALLOWED_TILESET_IDS = [k for k in SECONDARY_TERRAIN_TILESET_MAP.keys() if k < 170]
KECLEON_MD_INDEX = 383
# TODO: Make configurable?
MONSTER_LEVEL_VARIANCE = 3

# Invalid items:
DISALLOWED_ITEM_IDS = [11, 12, 98, 113, 114, 138, 166, 175, 176, 177, 181, 184, 185, 198, 205, 219, 224, 226, 236, 258,
                       259, 293, 294, 295, 296, 297, 298, 299, 300, 324, 339, 345, 349, 353, 360, 361]
ALLOWED_ITEM_IDS = [x for x in range(1, MAX_ITEM_ID + 1) if x not in DISALLOWED_ITEM_IDS]
ALLOWED_ITEM_CATS = [
    MappaItemCategory.THROWN_PIERCE,
    MappaItemCategory.THROWN_ROCK,
    MappaItemCategory.BERRIES_SEEDS_VITAMINS,
    MappaItemCategory.FOODS_GUMMIES,
    MappaItemCategory.HOLD,
    MappaItemCategory.TMS,
    MappaItemCategory.ORBS,
    MappaItemCategory.OTHER
]

MAX_TRAP_LISTS = 100
MAX_ITEM_LISTS = 150
MIN_MONSTERS_PER_LIST = 5
MAX_MONSTERS_PER_LIST = 30  # 48 is theoretical limit [=max used by vanilla game]
#MIN_ITEMS_PER_LIST = 20
#MAX_ITEMS_PER_LIST = 100  # 196 is theoretical limit [=max used by vanilla game]
MIN_ITEMS_PER_CAT = 4
MAX_ITEMS_PER_CAT = 18


class DungeonRandomizer(AbstractRandomizer):
    def __init__(self, config: RandomizerConfig, rom: NintendoDSRom, static_data: Pmd2Data):
        super().__init__(config, rom, static_data)

        self.dungeons = HardcodedDungeons.get_dungeon_list(
            get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin']),
            self.static_data
        )

    def step_count(self) -> int:
        i = 1
        if self.config['dungeons']['items']:
            i += 1
        if self.config['dungeons']['traps']:
            i += 1
        return i

    def run(self, status: Status):
        mappa = FileType.MAPPA_BIN.deserialize(self.rom.getFileByName('BALANCE/mappa_s.bin'))

        item_lists = None
        trap_lists = None

        if self.config['dungeons']['items']:
            status.step("Randomizing dungeon items...")
            item_lists = []
            for _ in range(0, MAX_ITEM_LISTS):
                item_lists.append(self._randomize_items())

        if self.config['dungeons']['traps']:
            status.step("Randomizing dungeon traps...")
            trap_lists = []
            for _ in range(0, MAX_TRAP_LISTS):
                trap_lists.append(self._randomize_traps())

        status.step("Randomizing dungeons...")
        self._randomize(mappa, trap_lists, item_lists)

        mappa_after = FileType.MAPPA_BIN.serialize(mappa)
        self.rom.setFileByName('BALANCE/mappa_s.bin', mappa_after)
        mappag_after = FileType.MAPPA_G_BIN.serialize(convert_mappa_to_mappag(mappa))
        self.rom.setFileByName('BALANCE/mappa_gs.bin', mappag_after)

        status.done()

    def _randomize(
            self, mappa: MappaBin, trap_lists: Optional[List[MappaTrapList]], item_lists: Optional[List[MappaItemList]]
    ):
        for floor_list_index, floor_list in enumerate(mappa.floor_lists):
            dungeon_id = self._get_dungeon_for_fl(floor_list_index)
            if dungeon_id not in self.config['dungeons']['settings'] or not self.config['dungeons']['settings'][dungeon_id]['randomize']:
                continue
            for i_floor, floor in enumerate(floor_list):
                if self._can_be_randomized(floor):
                    if self.config['dungeons']['layouts']:
                        floor.layout = self._randomize_layout(floor.layout, dungeon_id)
                    if self.config['dungeons']['pokemon']:
                        floor.monsters = self._randomize_monsters(
                            min(m.level for m in floor.monsters if m.weight > 0),
                            max(m.level for m in floor.monsters if m.weight > 0)
                        )
                    if trap_lists is not None:
                        floor.traps = choice(trap_lists)
                    if item_lists is not None:
                        floor.floor_items = choice(item_lists)
                        floor.buried_items = choice(item_lists)
                        floor.shop_items = choice(item_lists)
                        floor.monster_house_items = choice(item_lists)
                        floor.unk_items1 = choice(item_lists)
                        floor.unk_items2 = choice(item_lists)
                    if self.config['dungeons']['mode'] == DungeonModeConfig.GROUPED_BY_DUNGEON and i_floor > 0:
                        # If we are randomizing based on dungeon groups, use some settings of the first floor instead
                        # to make them look more like one connected dungeon
                        first_floor = floor_list[0]
                        floor.layout.tileset_id = first_floor.layout.tileset_id
                        floor.layout.music_id = first_floor.layout.music_id
                        floor.layout.secondary_terrain = first_floor.layout.secondary_terrain
                        floor.layout.darkness_level = first_floor.layout.darkness_level
                        floor.layout.iq_booster_enabled = first_floor.layout.iq_booster_enabled
                        floor.layout.enemy_iq = first_floor.layout.enemy_iq

    def _get_dungeon_for_fl(self, floor_index: int):
        for d_idx, d in enumerate(self.dungeons):
            if d.mappa_index == floor_index:
                return d_idx
        return 0

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

    @staticmethod
    def _can_be_randomized(floor: MappaFloor):
        # We don't randomize fixed floors
        return floor.layout.fixed_floor_id == 0

    def _randomize_layout(self, original_layout: MappaFloorLayout, dungeon_id: int):
        tileset = choice(ALLOWED_TILESET_IDS)
        structure = choice(list(MappaFloorStructureType))
        allow_monster_houses = self.config['dungeons']['settings'][dungeon_id]['monster_houses']
        randomize_iq = self.config['dungeons']['settings'][dungeon_id]['enemy_iq']
        # Make Monster Houses less likely by re-rolling 50% of the time when it happens
        if structure == MappaFloorStructureType.SINGLE_MONSTER_HOUSE or structure == MappaFloorStructureType.TWO_ROOMS_ONE_MH:
            if choice((True, False)):
                structure = choice(list(MappaFloorStructureType))
        while not allow_monster_houses and ( structure == MappaFloorStructureType.SINGLE_MONSTER_HOUSE or structure == MappaFloorStructureType.TWO_ROOMS_ONE_MH):
            structure = choice(list(MappaFloorStructureType))
        return MappaFloorLayout(
            structure=structure,
            room_density=randrange(3, 21),
            tileset_id=tileset,
            music_id=randrange(1, 118),
            weather=self._randomize_weather(original_layout, dungeon_id),
            floor_connectivity=randrange(5, 51),
            initial_enemy_density=randrange(1, 14),
            kecleon_shop_chance=randrange(0, 101),
            monster_house_chance=randrange(0, 101) if allow_monster_houses else 0,
            unusued_chance=randrange(0, 101),
            sticky_item_chance=randrange(0, 101),
            dead_ends=choice((True, False)),
            secondary_terrain=SECONDARY_TERRAIN_TILESET_MAP[tileset],
            terrain_settings=MappaFloorTerrainSettings(
                choice((True, False)), False, choice((True, False)), False, False, False, False, False
            ),
            unk_e=choice((True, False)),
            item_density=randrange(0, 11),
            trap_density=randrange(0, 16),
            floor_number=original_layout.floor_number,
            fixed_floor_id=original_layout.fixed_floor_id,
            extra_hallway_density=randrange(0, 36),
            buried_item_density=randrange(0, 11),
            water_density=randrange(0, 41),
            darkness_level=choice(list(MappaFloorDarknessLevel)),
            max_coin_amount=randrange(0, 181) * 5,
            kecleon_shop_item_positions=randrange(0, 14),
            empty_monster_house_chance=randrange(0, 101),
            unk_hidden_stairs=choice((0, 255)),
            hidden_stairs_spawn_chance=randrange(0, 101),
            enemy_iq=randrange(1, 601) if randomize_iq else original_layout.enemy_iq,
            iq_booster_allowed=choice((True, False))
        )

    def _randomize_monsters(self, min_level, max_level):
        monsters = []
        md_ids = sorted(
            set(choice(get_allowed_md_ids(self.config)) for _ in range(0, randrange(MIN_MONSTERS_PER_LIST, MAX_MONSTERS_PER_LIST + 1))))
        weights = sorted(self._random_weights(len(md_ids)))
        for md_id, weight in zip(md_ids, weights):
            level = min(100,
                        max(1, randrange(min_level - MONSTER_LEVEL_VARIANCE, max_level + MONSTER_LEVEL_VARIANCE + 1)))
            monsters.append(MappaMonster(level, weight, weight, md_id))

        # Add Kecleon and Dummy
        monsters.append(MappaMonster(42, 0, 0, KECLEON_MD_INDEX))
        monsters.append(MappaMonster(1, 0, 0, DUMMY_MD_INDEX))

        return sorted(monsters, key=lambda m: m.md_index)

    def _randomize_traps(self):
        # Unusued trap + 24 traps
        ws = sorted(self._random_weights(24))
        return MappaTrapList([0] + ws)

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

    def _randomize_weather(self, original_layout, dungeon_id):
        if not self.config['dungeons']['settings'][dungeon_id]['randomize_weather']:
            return original_layout.weather
        if self.config['dungeons']['weather'] == DungeonWeatherConfig.NO_RANDOMIZE:
            return original_layout.weather
        if self.config['dungeons']['weather'] == DungeonWeatherConfig.ONLY_RANDOM:
            return MappaFloorWeather.RANDOM
        if self.config['dungeons']['weather'] == DungeonWeatherConfig.SHUFFLED:
            return choice(list(MappaFloorWeather))
        if self.config['dungeons']['weather'] == DungeonWeatherConfig.SHUFFLED_LOWER_BAD_CHANCE:
            weather = choice(list(MappaFloorWeather))
            # Re-roll once if we get bad weather
            if weather in (MappaFloorWeather.HAIL, MappaFloorWeather.SANDSTORM, MappaFloorWeather.RANDOM):
                weather = choice(list(MappaFloorWeather))
            return weather
