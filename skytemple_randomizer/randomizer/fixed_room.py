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
import os
from random import randrange
from typing import List, Tuple, Iterable

from ndspy.rom import NintendoDSRom

from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import open_utf8, get_binary_from_rom_ppmdu
from skytemple_files.dungeon_data.fixed_bin.model import FixedFloorActionRule, TileRule, TileRuleType, FixedBin, \
    FixedFloor, EntityRule
from skytemple_files.dungeon_data.mappa_bin.floor import MappaFloor
from skytemple_files.dungeon_data.mappa_bin.model import MappaBin
from skytemple_files.dungeon_data.mappa_g_bin.mappa_converter import convert_mappa_to_mappag
from skytemple_files.hardcoded.dungeons import HardcodedDungeons
from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.status import Status

BOSS_ROOMS = range(1, 110)
FLOOR = TileRule(TileRuleType.FLOOR_ROOM)
WALL = TileRule(TileRuleType.WALL_HALLWAY_IMPASSABLE)
SECONDARY = TileRule(TileRuleType.SECONDARY_ROOM)
START_DUNGEON_BGS = 170


class FixedRoomRandomizer(AbstractRandomizer):
    def __init__(self, config: RandomizerConfig, rom: NintendoDSRom, static_data: Pmd2Data):
        super().__init__(config, rom, static_data)

        self.dungeons = HardcodedDungeons.get_dungeon_list(
            get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin']),
            self.static_data
        )

    def step_count(self) -> int:
        if self.config['dungeons']['fixed_rooms']:
            return 1
        return 0

    def run(self, status: Status):
        if not self.config['dungeons']['fixed_rooms']:
            return status.done()

        mappa: MappaBin = FileType.MAPPA_BIN.deserialize(self.rom.getFileByName('BALANCE/mappa_s.bin'))
        fixed: FixedBin = FileType.FIXED_BIN.deserialize(self.rom.getFileByName('BALANCE/fixed.bin'),
                                                         static_data=self.static_data)

        status.step('Randomizing Boss Floor Layouts...')
        for i in BOSS_ROOMS:
            fixed_room = fixed.fixed_floors[i]
            for floor_list, floor_id in self._get_dungeon_floors_for_fixed_room(mappa.floor_lists, i):
                self._assign_dungeon_floor_regular_tileset(floor_list, floor_id)
            w, h, new_layout = self._get_random_room(self._get_special_in_floor(fixed_room))
            fixed_room.width = w
            fixed_room.height = h
            fixed_room.actions = new_layout

        self.rom.setFileByName('BALANCE/fixed.bin', FileType.FIXED_BIN.serialize(fixed))
        self.rom.setFileByName('BALANCE/mappa_s.bin', FileType.MAPPA_BIN.serialize(mappa))
        mappag_after = FileType.MAPPA_G_BIN.serialize(convert_mappa_to_mappag(mappa))
        self.rom.setFileByName('BALANCE/mappa_gs.bin', mappag_after)

        status.done()

    def _get_dungeon_floors_for_fixed_room(
            self, floor_lists: List[List[MappaFloor]], ff_id: int
    ) -> Iterable[Tuple[List[MappaFloor], int]]:
        for fl in floor_lists:
            for flooridx, floor in enumerate(fl):
                if floor.layout.fixed_floor_id == ff_id:
                    yield fl, flooridx

    def _assign_dungeon_floor_regular_tileset(self, floor_list: List[MappaFloor], floor_id: int):
        if floor_list[floor_id].layout.tileset_id >= START_DUNGEON_BGS:
            floor_list[floor_id].layout.tileset_id = floor_list[floor_id - 1].layout.tileset_id

    def _get_special_in_floor(self, floor: FixedFloor):
        l = []
        for action in floor.actions:
            if isinstance(action, EntityRule) or \
                    action.tr_type == TileRuleType.LEADER_SPAWN or \
                    action.tr_type == TileRuleType.ATTENDANT1_SPAWN or \
                    action.tr_type == TileRuleType.ATTENDANT2_SPAWN or \
                    action.tr_type == TileRuleType.ATTENDANT3_SPAWN:
                l.append(action)
        return l

    def _get_random_room(self, entities_and_special_tiles_to_preserve: List[FixedFloorActionRule]):
        room_data = self._get_random_room_txt()
        width = len(room_data[0])
        height = len(room_data)
        actions = []
        for line in room_data:
            for char in line:
                if char == '#':
                    actions.append(WALL)
                elif char == '~':
                    actions.append(SECONDARY)
                elif char == '.':
                    actions.append(FLOOR)
                else:
                    raise ValueError(f"Invalid fixed floor layout data found (char: {char}).")

        # Randomly replace floor with entities to preserve
        while len(entities_and_special_tiles_to_preserve) > 0:
            index = randrange(0, len(actions))
            if actions[index] == FLOOR:
                actions[index] = entities_and_special_tiles_to_preserve.pop()

        return width, height, actions

    def _get_random_room_txt(self):
        from skytemple_randomizer.main import data_dir
        i = randrange(0, 1000)
        with open_utf8(os.path.join(data_dir(), 'fixed_floor_layouts', f'{i}.txt')) as f:
            return f.read().splitlines()
