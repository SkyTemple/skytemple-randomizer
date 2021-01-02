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
from skytemple_files.data.md.model import PokeType, Md
from skytemple_files.data.waza_p.model import WazaP
from skytemple_randomizer.config import MovesetConfig
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.status import Status


VALID_MOVE_IDS = list(set(range(0, 542)) - {
    355, 467, 356, 357, 358, 359, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370,
    371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386,
    387, 388, 389, 390, 391, 392, 393, 395, 396, 397, 398, 399, 400, 401, 402, 403,
    404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419,
    420, 421, 422, 423, 424, 425, 426, 427, 428, 429
})
DAMAGING_MOVES = [1, 2, 8, 9, 16, 18, 25, 28, 30, 31, 32, 36, 39, 41, 42, 44, 46, 52, 53, 57, 60, 62, 63, 64, 65, 67,
                  68, 69, 71, 72, 73, 75, 76, 77, 78, 80, 81, 82, 87, 90, 91, 92, 93, 96, 97, 100, 101, 103, 105, 107,
                  109, 110, 113, 114, 116, 118, 120, 121, 125, 126, 127, 129, 132, 133, 135, 136, 139, 140, 143, 144,
                  145, 147, 149, 151, 153, 154, 156, 157, 158, 159, 161, 162, 163, 164, 166, 167, 168, 174, 175, 176,
                  178, 179, 180, 182, 188, 189, 190, 193, 198, 200, 201, 203, 204, 205, 206, 207, 208, 210, 211, 213,
                  214, 219, 221, 222, 226, 228, 230, 234, 235, 238, 239, 240, 241, 242, 243, 244, 245, 246, 248, 250,
                  251, 253, 255, 260, 261, 262, 263, 264, 270, 271, 272, 275, 276, 278, 279, 280, 283, 285, 287, 289,
                  290, 291, 292, 297, 299, 300, 303, 306, 308, 309, 310, 311, 312, 314, 320, 321, 322, 323, 325, 331,
                  332, 335, 336, 342, 344, 345, 346, 347, 348, 350, 352, 353, 354, 430, 431, 432, 433, 435, 436, 437,
                  440, 441, 442, 443, 445, 446, 451, 452, 453, 454, 455, 457, 458, 459, 460, 461, 462, 463, 468, 469,
                  470, 471, 473, 474, 475, 476, 477, 479, 481, 484, 485, 486, 487, 488, 489, 490, 491, 494, 495, 497,
                  498, 500, 501, 502, 505, 507, 508, 510, 511, 512, 515, 516, 517, 518, 519, 521, 522, 523, 524, 527,
                  529, 530, 531, 533, 535, 536, 537, 538, 539, 541]
STAB_DICT = {
    PokeType.STEEL: [1, 103, 244, 325, 431, 475, 510, 523, 527, 536],
    PokeType.ICE: [2, 42, 97, 101, 180, 270, 344, 345, 461, 462, 535],
    PokeType.GROUND: [8, 118, 143, 213, 285, 289, 290, 299, 484, 501],
    PokeType.NORMAL: [9, 18, 25, 31, 39, 60, 67, 71, 78, 81, 96, 121, 125, 132, 139, 140, 145, 154, 161, 166, 168, 176,
                      190, 201, 203, 207, 226, 228, 235, 241, 242, 245, 248, 250, 260, 261, 263, 264, 271, 275, 287,
                      311, 312, 314, 321, 322, 347, 348, 352, 455, 457, 471, 474, 487, 497, 505, 516, 541],
    PokeType.WATER: [16, 32, 44, 69, 87, 113, 156, 158, 159, 219, 239, 240, 255, 308, 310, 432, 433, 469],
    PokeType.ROCK: [28, 30, 73, 93, 105, 350, 453, 481, 512, 533],
    PokeType.FLYING: [36, 57, 100, 153, 174, 178, 179, 205, 211, 353, 442, 446, 490, 518],
    PokeType.FIRE: [41, 52, 53, 149, 157, 230, 262, 272, 276, 278, 291, 292, 517, 519, 522, 524],
    PokeType.GHOST: [46, 120, 126, 127, 437, 451, 476, 477],
    PokeType.DARK: [62, 63, 167, 214, 436, 445, 488, 491, 515],
    PokeType.ELECTRIC: [64, 65, 129, 144, 188, 189, 193, 354, 452, 489, 521],
    PokeType.FIGHTING: [68, 72, 75, 77, 90, 92, 116, 136, 175, 204, 206, 210, 222, 243, 246, 300, 303, 430, 440, 454,
                        479, 500, 507, 508, 531],
    PokeType.GRASS: [76, 135, 151, 163, 182, 221, 238, 251, 253, 297, 320, 336, 441, 443, 458, 468, 486, 511, 537],
    PokeType.BUG: [80, 82, 114, 164, 306, 323, 346, 460, 470, 502, 529, 530],
    PokeType.DRAGON: [91, 162, 208, 342, 435, 494, 498, 538, 539],
    PokeType.PSYCHIC: [107, 109, 110, 133, 234, 309, 331, 335, 463, 473],
    PokeType.POISON: [147, 198, 200, 279, 280, 283, 332, 459, 485, 495]
}


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

        for md_entry, waza_p_entry in zip(md.entries, waza_p.learnsets):
            waza_p_entry.egg_moves = [choice(VALID_MOVE_IDS) for _ in waza_p_entry.egg_moves]
            # Don't randomize, since not all have TM/HSs
            #waza_p_entry.tm_hm_moves = [choice(VALID_MOVE_IDS) for _ in waza_p_entry.tm_hm_moves]

            for idx, e in enumerate(waza_p_entry.level_up_moves):
                if idx > 0 or self.config['pokemon']['movesets'] == MovesetConfig.FULLY_RANDOM:
                    e.move_id = choice(VALID_MOVE_IDS)
                elif self.config['pokemon']['movesets'] == MovesetConfig.FIRST_DAMAGE:
                    e.move_id = choice(DAMAGING_MOVES)
                elif self.config['pokemon']['movesets'] == MovesetConfig.FIRST_STAB:
                    if md_entry.type_primary not in STAB_DICT:
                        e.move_id = choice(VALID_MOVE_IDS)
                    else:
                        e.move_id = choice(STAB_DICT[md_entry.type_primary])

        self.rom.setFileByName('BALANCE/waza_p.bin', FileType.WAZA_P.serialize(waza_p))

        status.done()
