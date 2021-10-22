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
import math
from collections import OrderedDict
from enum import Enum, auto
from itertools import chain
from random import choice, randrange, randint
from typing import Optional, List, Dict, Tuple

from ndspy.rom import NintendoDSRom

from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.common.ppmdu_config.dungeon_data import Pmd2DungeonItem
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_binary_from_rom_ppmdu, set_binary_in_rom_ppmdu
from skytemple_files.dungeon_data.mappa_bin import MAX_WEIGHT
from skytemple_files.dungeon_data.mappa_bin.floor import MappaFloor
from skytemple_files.dungeon_data.mappa_bin.floor_layout import MappaFloorLayout, \
    MappaFloorStructureType, MappaFloorWeather, MappaFloorTerrainSettings, MappaFloorDarknessLevel
from skytemple_files.dungeon_data.mappa_bin.item_list import MappaItemList
from skytemple_files.dungeon_data.mappa_bin.model import MappaBin
from skytemple_files.dungeon_data.mappa_bin.monster import MappaMonster, DUMMY_MD_INDEX
from skytemple_files.dungeon_data.mappa_bin.trap_list import MappaTrapList
from skytemple_files.dungeon_data.mappa_bin.validator.exception import DungeonValidatorError, \
    DungeonTotalFloorCountInvalidError, InvalidFloorListReferencedError, InvalidFloorReferencedError, \
    DungeonMissingFloorError, FloorReusedError
from skytemple_files.dungeon_data.mappa_bin.validator.validator import DungeonValidator
from skytemple_files.dungeon_data.mappa_g_bin.mappa_converter import convert_mappa_to_mappag
from skytemple_files.hardcoded.dungeons import HardcodedDungeons, DungeonDefinition
from skytemple_randomizer.config import DungeonWeatherConfig, RandomizerConfig, DungeonModeConfig
from skytemple_randomizer.frontend.abstract import AbstractFrontend
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import sample_with_minimum_distance, get_allowed_md_ids, \
    get_allowed_item_ids
from skytemple_randomizer.status import Status

ALLOWED_TILESET_IDS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27,
                       28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 42, 43, 44, 45, 46, 48, 49, 50, 51, 52, 53,
                       54, 55, 56, 57, 58, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 74, 75, 76, 78, 79, 80, 81, 82, 83,
                       84, 85, 87, 88, 89, 90, 91, 94, 96, 97, 99, 101, 102, 103, 104, 105, 106, 108, 109, 110, 111,
                       112, 113, 114, 115, 116, 117, 118, 119, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132,
                       133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143]
KECLEON_MD_INDEX = 383
# TODO: Make configurable?
MONSTER_LEVEL_VARIANCE = 3

ALLOWED_ITEM_CATS = [
    0, 1, 2, 3, 4, 5, 9, 8
]
SKY_PEAK_MAPPA_IDX = 72
SHAYMIN_IDS = [534, 535]

MAX_TRAP_LISTS = 100
MAX_ITEM_LISTS = 150
MIN_MONSTERS_PER_LIST = 5
MAX_MONSTERS_PER_LIST = 30  # 48 is theoretical limit [=max used by vanilla game]
#MIN_ITEMS_PER_LIST = 20
#MAX_ITEMS_PER_LIST = 100  # 196 is theoretical limit [=max used by vanilla game]
MIN_ITEMS_PER_CAT = 4
MAX_ITEMS_PER_CAT = 18


class FixedRoomPosition(Enum):
    BEGIN = auto()
    MIDDLE = auto()
    END = auto()


class DungeonRandomizer(AbstractRandomizer):
    def __init__(self, config: RandomizerConfig, rom: NintendoDSRom, static_data: Pmd2Data, seed: str, frontend: AbstractFrontend):
        super().__init__(config, rom, static_data, seed, frontend)

        self.dungeons = HardcodedDungeons.get_dungeon_list(
            get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin']),
            self.static_data
        )
        self.mappa: Optional[MappaBin] = None

    def step_count(self) -> int:
        i = 2
        if self.config['dungeons']['items']:
            i += 1
        if self.config['dungeons']['traps']:
            i += 1
        return i

    def run(self, status: Status):
        self.mappa = FileType.MAPPA_BIN.deserialize(self.rom.getFileByName('BALANCE/mappa_s.bin'))

        status.step("Fixing dungeon errors...")
        # We may need to do this twice
        for _ in range(2):
            validator = DungeonValidator(self.mappa.floor_lists)
            validator.validate(self.dungeons)
            for error in validator.errors:
                self._fix_error(error)
        assert DungeonValidator(self.mappa.floor_lists).validate(self.dungeons)

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
        self._randomize(self.mappa, trap_lists, item_lists)

        mappa_after = FileType.MAPPA_BIN.serialize(self.mappa)
        self.rom.setFileByName('BALANCE/mappa_s.bin', mappa_after)
        mappag_after = FileType.MAPPA_G_BIN.serialize(convert_mappa_to_mappag(self.mappa))
        self.rom.setFileByName('BALANCE/mappa_gs.bin', mappag_after)

        status.done()

    def _randomize(
            self, mappa: MappaBin, trap_lists: Optional[List[MappaTrapList]], item_lists: Optional[List[MappaItemList]]
    ):
        mappa.floor_lists = self._randomize_floor_count(mappa.floor_lists)
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
                            max(m.level for m in floor.monsters if m.weight > 0),
                            floor_list_index != SKY_PEAK_MAPPA_IDX
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
                        floor.layout.iq_booster_boost = first_floor.layout.iq_booster_boost
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
        while not allow_monster_houses and (structure == MappaFloorStructureType.SINGLE_MONSTER_HOUSE or structure == MappaFloorStructureType.TWO_ROOMS_ONE_MH):
            structure = choice(list(MappaFloorStructureType))
        return MappaFloorLayout(
            structure=structure,
            room_density=randrange(3, 21),
            tileset_id=tileset,
            music_id=randrange(1, 118),
            weather=self._randomize_weather(original_layout, dungeon_id),
            floor_connectivity=randrange(5, 51),
            initial_enemy_density=randrange(1, 7),
            kecleon_shop_chance=randrange(0, 101),
            monster_house_chance=
                randrange(0, self.config['dungeons']['max_mh_chance'].value + 1) if allow_monster_houses else 0,
            unusued_chance=randrange(0, 101),
            sticky_item_chance=randrange(0, self.config['dungeons']['max_sticky_chance'].value + 1),
            dead_ends=choice((True, False)),
            secondary_terrain=randrange(0, 30),
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
            iq_booster_boost=choice((0, 1))
        )

    def _randomize_monsters(self, min_level, max_level, allow_shaymin=True):
        monsters = []
        allowed = get_allowed_md_ids(self.config)
        if not allow_shaymin:
            for idx in SHAYMIN_IDS:
                if idx in allowed:
                    allowed.remove(idx)
        md_ids = sorted(
            set(choice(allowed) for _ in range(0, randrange(MIN_MONSTERS_PER_LIST, MAX_MONSTERS_PER_LIST + 1))))
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
            cats_as_list.append(6)

        # 1/8 chance for Link Box to get a chance
        if choice([True] + [False] * 7):
            cats_as_list.append(10)

        cats_as_list.sort()
        weights = sorted(self._random_weights(len(cats_as_list)))
        for i, cat_id in enumerate(cats_as_list):
            cat = self.static_data.dungeon_data.item_categories[cat_id]
            categories[cat] = weights[i]

            cat_item_ids = []
            if cat.number_of_items is not None:
                allowed_cat_item_ids = [x for x in cat.item_ids() if x in get_allowed_item_ids(self.config)]
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
                    cat_weights = sorted(self._random_weights(len(cat_item_ids)))

                    for item_id, weight in zip(cat_item_ids, cat_weights):
                        items[Pmd2DungeonItem(item_id, '???')] = weight
            if len(cat_item_ids) == 0:
                categories[cat] = 0

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

    def _randomize_floor_count(self, floor_lists: List[List[MappaFloor]]) -> List[List[MappaFloor]]:
        if self.config['dungeons']['min_floor_change_percent'].value == 0 and self.config['dungeons']['max_floor_change_percent'].value == 0:
            return floor_lists
        new_floor_lists = []
        for i in range(0, len(floor_lists)):
            dungeons: Dict[int, DungeonDefinition] = {}
            do_continue = False
            for dungeon_id, dungeon in enumerate(self.dungeons):
                if dungeon.mappa_index == i:
                    if dungeon_id not in self.config['dungeons']['settings'] or not self.config['dungeons']['settings'][dungeon_id]['randomize']:
                        do_continue = True
                        break
                    dungeons[dungeon_id] = dungeon
            if do_continue:
                new_floor_lists.append(floor_lists[i])
                continue

            old_list = floor_lists[i]
            try:
                new_dungeon_size = randrange(
                    len(old_list) - round(len(old_list) * (self.config['dungeons']['min_floor_change_percent'].value / 100)),
                    len(old_list) + round(len(old_list) * (self.config['dungeons']['max_floor_change_percent'].value / 100))
                )
            except ValueError:
                new_dungeon_size = len(old_list)
            new_dungeon_size = max(sum(1 for x in dungeons.values() if x.mappa_index == i), min(99, new_dungeon_size))
            if new_dungeon_size == len(old_list) or len(dungeons) < 1:
                new_floor_list = old_list
            else:
                old_dungeons = [dict(d.__dict__) for d in dungeons.values()]
                new_floor_list = self._resize_floor_list(dungeons, new_dungeon_size, old_list)
                if new_floor_list is False:
                    # we bailed out :(
                    new_floor_list = old_list
                    for i, d in enumerate(dungeons.values()):
                        d.__dict__.update(old_dungeons[i])
            new_floor_lists.append(new_floor_list)
        assert DungeonValidator(new_floor_lists).validate(self.dungeons)
        arm9 = bytearray(get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin']))
        HardcodedDungeons.set_dungeon_list(
            self.dungeons, arm9, self.static_data
        )
        set_binary_in_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin'], arm9)
        return new_floor_lists

    def _copy_randomly_into_until_size(self, lst: List[MappaFloor], expected_length):
        if len(lst) < 1:
            lst.append(self._mappa_generate_new_floor())
        while len(lst) < expected_length:
            idx = brandint(0, len(lst) - 1)
            lst.insert(brandint(0, len(lst)), MappaFloor.from_xml(lst[idx].to_xml()))

    def _resize_floor_list(self, dungeons: Dict[int, DungeonDefinition], new_dungeon_size: int, old_list: List[MappaFloor]):
        fixed_floors_per_dungeon: Dict[int, List[Tuple[FixedRoomPosition, MappaFloor]]] = {}
        list_parts: Dict[int, List[MappaFloor]] = {}

        # Re-distribute floors - if the dungeon only had one floor, leave it at length 1
        # + collect all fixed floors per dungeon
        count_dungeons_with_only_one = sum([1 for x in dungeons.values() if x.number_floors < 2])
        # for this we ignore all 1-sized
        increase_percent = (new_dungeon_size - count_dungeons_with_only_one) / len(old_list)
        for dungeon_id, dungeon in dungeons.items():
            list_parts[dungeon_id] = []
            fixed_floors_per_dungeon[dungeon_id] = []
            for floori, floor in enumerate(old_list[dungeon.start_after:dungeon.start_after + dungeon.number_floors]):
                if floor.layout.fixed_floor_id != 0:
                    # todo: multiple in a row and beginning and end? we support it below!
                    pos = FixedRoomPosition.MIDDLE
                    if floori < 1:
                        pos = FixedRoomPosition.BEGIN
                    if floori > dungeon.number_floors - 1:
                        pos = FixedRoomPosition.END
                    fixed_floors_per_dungeon[dungeon_id].append((pos, floor))
            new_length = 1
            if dungeon.number_floors == 1:
                list_parts[dungeon_id] = [old_list[dungeon.start_after]]
            else:
                # Redistribute
                list_parts[dungeon_id] = old_list[dungeon.start_after:dungeon.start_after + dungeon.number_floors]
                new_length = max(1, math.floor(dungeon.number_floors * increase_percent))
                self._copy_randomly_into_until_size(list_parts[dungeon_id], new_length)
                while len(list_parts[dungeon_id]) > new_length:
                    idx = brandint(0, len(list_parts[dungeon_id]) - 1)
                    del list_parts[dungeon_id][idx]
            dungeon.number_floors = new_length
            dungeon.number_floors_in_group = new_dungeon_size
        difference = new_dungeon_size - len(list(chain.from_iterable(list_parts.values())))
        # OK but if all dungeons are length 1 or smaller, we bail out
        while difference < 0:
            for dungeon_id, dungeon in dungeons.items():
                if dungeon.number_floors > 1:
                    difference += 1
                    idx = brandint(0, len(list_parts[dungeon_id]) - 1)
                    del list_parts[dungeon_id][idx]
                    dungeon.number_floors -= 1
                if difference == 0:
                    break
        # fill up remaining empty spaces due to rounding
        while difference > 0:
            for dungeon_id, dungeon in dungeons.items():
                if dungeon.number_floors > 1 or not any(d.layout.fixed_floor_id != 0 for d in list_parts[dungeon_id]):
                    difference -= 1
                    idx = brandint(0, len(list_parts[dungeon_id]) - 1)
                    list_parts[dungeon_id].insert(brandint(0, len(list_parts[dungeon_id]) - 1),
                                                  MappaFloor.from_xml(list_parts[dungeon_id][idx].to_xml()))
                    dungeon.number_floors += 1
                if difference == 0:
                    break

        # Re-add fixed floors:
        for dungeon_id, lst in list_parts.items():
            len_before = len(lst)
            ffs = fixed_floors_per_dungeon[dungeon_id]
            expected_length = len(lst) - len(ffs)
            if expected_length < 0:
                # bail out!
                return False
            lst = [x for x in lst if x if x.layout.fixed_floor_id == 0][0:expected_length]
            self._copy_randomly_into_until_size(lst, expected_length)
            while len(lst) > expected_length:
                idx = brandint(0, len(lst) - 1)
                del lst[idx]
            ff_begin: List[MappaFloor] = []
            ff_end: List[MappaFloor] = []
            for pos, ff in ffs:
                if pos == FixedRoomPosition.BEGIN:
                    ff_begin.append(ff)
                elif pos == FixedRoomPosition.END:
                    ff_end.insert(0, ff)
                else:
                    lst.insert(brandint(0, len(lst) - 1), ff)

            list_parts[dungeon_id] = ff_begin + lst + ff_end
            assert len(list_parts[dungeon_id]) == expected_length + len(ffs)
            assert len(list_parts[dungeon_id]) == len_before

        # Correct start_after
        current_cursor = 0
        for dungeon, lst in zip(dungeons.values(), list_parts.values()):
            dungeon.start_after = current_cursor
            current_cursor += dungeon.number_floors
            assert dungeon.number_floors == len(lst)

        new_floor_list = list(chain.from_iterable(list_parts.values()))
        assert len(new_floor_list) == new_dungeon_size
        return new_floor_list

    # ---------------- Deal with dungeon errors; copied from SkyTemple dungeon module

    def _fix_error(self, e: DungeonValidatorError):
        if isinstance(e, DungeonTotalFloorCountInvalidError):
            self.dungeons[e.dungeon_id].number_floors_in_group = e.expected_floor_count_in_group
        elif isinstance(e, InvalidFloorListReferencedError) or isinstance(e, FloorReusedError):
            self.dungeons[e.dungeon_id].mappa_index = self._mappa_generate_and_insert_new_floor_list()
            self.dungeons[e.dungeon_id].start_after = 0
            self.dungeons[e.dungeon_id].number_floors = 1
            self.dungeons[e.dungeon_id].number_floors_in_group = 1
        elif isinstance(e, InvalidFloorReferencedError):
            valid_floors = len(self.mappa.floor_lists[e.dungeon.mappa_index]) - e.dungeon.start_after
            if valid_floors > 0:
                self.dungeons[e.dungeon_id].number_floors = valid_floors
            else:
                self.mappa.floor_lists[e.dungeon.mappa_index].append(self._mappa_generate_new_floor())
                self.dungeons[e.dungeon_id].number_floors = 1
        elif isinstance(e, DungeonMissingFloorError):
            # Special case for Regigigas Chamber
            if self._is_regigias_special_case(self.dungeons, e):
                # Remove additional floors
                self.mappa.floor_lists[e.dungeon.mappa_index] = [
                    f for i, f in enumerate(self.mappa.floor_lists[e.dungeon.mappa_index])
                    if i not in e.floors_in_mappa_not_referenced
                ]
            else:
                # Add additional floors
                if min(e.floors_in_mappa_not_referenced) == e.dungeon.start_after + e.dungeon.number_floors:
                    if check_consecutive(e.floors_in_mappa_not_referenced):
                        max_floor_id = max(e.floors_in_mappa_not_referenced)
                        self.dungeons[e.dungeon_id].number_floors = max_floor_id - self.dungeons[e.dungeon_id].start_after + 1

    @staticmethod
    def _is_regigias_special_case(dungeons, e):
        return e.dungeon_id == 61 and dungeons[e.dungeon_id].mappa_index == 52 and \
                    dungeons[e.dungeon_id].start_after == 18 and e.floors_in_mappa_not_referenced == [19]

    def _mappa_generate_and_insert_new_floor_list(self):
        index = len(self.mappa.floor_lists)
        self.mappa.floor_lists.append([self._mappa_generate_new_floor()])
        return index

    def _mappa_generate_new_floor(self) -> MappaFloor:
        """Copies the first floor of test dungeon and returns it"""
        return MappaFloor.from_xml(self.mappa.floor_lists[0][0].to_xml())


def check_consecutive(l):
    return sorted(l) == list(range(min(l), max(l)+1))


def brandint(a, b):
    if a >= b:
        return a
    return randint(a, b)
