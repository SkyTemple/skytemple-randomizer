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
from random import choice

from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_binary_from_rom_ppmdu, set_binary_in_rom_ppmdu
from skytemple_files.hardcoded.fixed_floor import HardcodedFixedFloorTables
from skytemple_files.list.actor.model import ActorListBin
from skytemple_files.patch.patches import Patcher
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_allowed_md_ids
from skytemple_randomizer.status import Status

# Maps actor list indices to fixed room monster spawn indices.
ACTOR_TO_BOSS_MAPPING = {
    7: [35, 109], 9: [67], 18: [35, 109], 19: [59], 20: [67], 79: [33, 107], 80: [21], 81: [41, 115], 82: [40, 114],
    86: [68], 89: [22], 92: [43], 94: [28], 95: [28], 96: [27], 101: [35, 109], 105: [59], 109: [39, 113, 116],
    111: [30, 81], 112: [65], 115: [36, 110], 119: [37, 111], 120: [45], 121: [44], 122: [46],
    123: [23, 69, 100, 101, 102, 103, 104, 105, 106], 128: [67], 130: [17], 131: [34, 108], 132: [26], 133: [38, 112],
    136: [29], 137: [63], 138: [58], 139: [64], 140: [31, 32, 84], 141: [48], 142: [47], 143: [72], 154: [49],
    172: [99],
    181: [51], 182: [87], 183: [50, 88], 184: [89], 191: [66], 195: [70], 196: [42], 198: [30, 81], 199: [30, 81],
    200: [30, 81], 201: [30, 81], 202: [30, 81], 209: [71], 211: [74], 213: [37, 111], 214: [33, 107], 215: [63],
    216: [64], 217: [58], 218: [35, 109], 219: [41, 115], 220: [40, 114], 221: [36, 110], 222: [39, 113, 116],
    224: [34, 108], 225: [59], 226: [29], 227: [30, 81], 228: [30, 81], 229: [33, 107], 230: [47], 231: [57], 232: [57],
    233: [57], 234: [57], 235: [57], 236: [57], 237: [57], 238: [57], 239: [57], 240: [57], 241: [57], 242: [57],
    243: [56], 244: [56], 245: [56], 246: [56], 247: [56], 248: [56], 249: [56], 250: [56], 251: [56], 252: [56],
    253: [56], 254: [56], 255: [31, 32, 84], 256: [49], 258: [53, 85], 259: [54], 260: [52], 261: [55], 270: [61],
    271: [73], 272: [60], 273: [80], 277: [78], 278: [79], 279: [77], 280: [82], 281: [83], 282: [83], 283: [83],
    284: [83], 294: [33, 107], 295: [33, 107], 317: [117], 318: [119], 319: [118], 326: [75], 327: [75], 328: [75],
    329: [75], 330: [75], 331: [75], 332: [76], 333: [76], 334: [76], 335: [76], 336: [76], 337: [90], 338: [90],
    339: [90], 349: [86], 350: [86], 351: [86], 352: [86], 353: [86], 354: [86], 361: [91, 92, 93], 362: [91, 92, 93],
    363: [91, 92, 93], 367: [24], 368: [25], 369: [25], 370: [25], 371: [25], 372: [25], 373: [25], 374: [25],
    375: [25],
    380: [94], 381: [95], 382: [96], 383: [97], 384: [98]
}
# Secret Bazar Pokémon that aren't also NPCs
EXTRA_FF_MONSTER_RANDOMIZE = [16, 18, 19, 20]


class BossRandomizer(AbstractRandomizer):
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

        status.step("Updating bosses...")

        actor_list: ActorListBin = FileType.SIR0.unwrap_obj(
            FileType.SIR0.deserialize(self.rom.getFileByName('BALANCE/actor_list.bin')), ActorListBin
        )

        binary = get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['overlay/overlay_0029.bin'])
        boss_list = HardcodedFixedFloorTables.get_monster_spawn_list(binary, self.static_data)

        for i, actor in enumerate(actor_list.list):
            if i in ACTOR_TO_BOSS_MAPPING:
                for bi in ACTOR_TO_BOSS_MAPPING[i]:
                    boss_list[bi].md_idx = actor.entid

        for extra_id in EXTRA_FF_MONSTER_RANDOMIZE:
            boss_list[extra_id].md_idx = choice(get_allowed_md_ids(self.config, False))

        HardcodedFixedFloorTables.set_monster_spawn_list(binary, boss_list, self.static_data)
        set_binary_in_rom_ppmdu(self.rom, self.static_data.binaries['overlay/overlay_0029.bin'], binary)

        status.done()


# For reference, this is how I created that mapping in ACTOR_TO_BOSS_MAPPING
def create_mapping():
    from ndspy.rom import NintendoDSRom
    rom = NintendoDSRom.fromFile('/home/marco/dev/skytemple/skytemple/skyworkcopy_us_unpatched.nds')
    from skytemple_files.common.util import get_ppmdu_config_for_rom
    static_data = get_ppmdu_config_for_rom(rom)
    from skytemple_files.patch.patches import Patcher
    patcher = Patcher(rom, static_data)
    patcher.apply('ActorAndLevelLoader')

    from skytemple_files.common.types.file_types import FileType
    from skytemple_files.data.md.model import Md
    md: Md = FileType.MD.deserialize(rom.getFileByName('BALANCE/monster.md'))
    from skytemple_files.list.actor.model import ActorListBin
    actor_list: ActorListBin = FileType.SIR0.unwrap_obj(
        FileType.SIR0.deserialize(rom.getFileByName('BALANCE/actor_list.bin')), ActorListBin
    )
    from skytemple_files.hardcoded.fixed_floor import HardcodedFixedFloorTables
    from skytemple_files.common.util import get_binary_from_rom_ppmdu
    boss_list = HardcodedFixedFloorTables.get_monster_spawn_list(
        get_binary_from_rom_ppmdu(rom, static_data.binaries['overlay/overlay_0029.bin']),
        static_data
    )

    actor_list_pokedex_number_mapping = []
    for e in actor_list.list:
        monster = md.entries[e.entid]
        actor_list_pokedex_number_mapping.append(monster.national_pokedex_number)

    boss_list_pokedex_number_mapping = []
    for boss in boss_list:
        try:
            monster = md.entries[boss.md_idx]
            boss_list_pokedex_number_mapping.append(monster.national_pokedex_number)
        except IndexError:
            boss_list_pokedex_number_mapping.append(0)

    mapping = {}
    for idx, a in enumerate(actor_list_pokedex_number_mapping):
        if a == 0:
            continue
        indices = [i for i, x in enumerate(boss_list_pokedex_number_mapping) if x == a]
        if len(indices) > 0:
            mapping[idx] = indices

    print(mapping)
