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
from random import randint
from time import sleep

from ndspy.rom import NintendoDSRom

from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.common.types.file_types import FileType
from skytemple_files.patch.patches import Patcher
from skytemple_randomizer.config import QuizMode, RandomizerConfig, QuizQuestion
from skytemple_randomizer.frontend.abstract import AbstractFrontend
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_all_string_files
from skytemple_randomizer.status import Status
QUESTION_MAPPING = {
    0: [0, 1, 2],
    1: [3, 4, 5],
    2: [6, 7, 8],
    3: [9, 10, 11, 12],
    4: [13, 14],
    5: [15, 16, 17],
    6: [18, 19],
    7: [20, 21, 22],
    8: [23, 24, 25],
    9: [26, 27, 28],
    10: [29, 30, 31, 32],
    11: [33, 34, 35],
    12: [36, 37],
    13: [38, 39, 40],
    14: [41, 42, 43],
    15: [44, 45],
    16: [46, 47],
    17: [48, 49, 50],
    18: [51, 52],
    19: [53, 54],
    20: [55, 56],
    21: [57, 58, 59],
    22: [60, 61],
    23: [62, 63],
    24: [64, 65, 66, 67],
    25: [68, 69, 70],
    26: [71, 72, 73],
    27: [74, 75, 76],
    28: [77, 78],
    29: [79, 80],
    30: [81, 82, 83],
    31: [84, 85, 86],
    32: [87, 88],
    33: [89, 90],
    34: [91, 92],
    35: [93, 94],
    36: [95, 96, 97],
    37: [98, 99, 100],
    38: [101, 102, 103],
    39: [104, 105],
    40: [106, 107, 108],
    41: [109, 110, 111],
    42: [112, 113, 114],
    43: [115, 116],
    44: [117, 118, 119],
    45: [120, 121, 122],
    46: [123, 124],
    47: [125, 126, 127, 128],
    48: [129, 130],
    49: [131, 132],
    50: [133, 134],
    51: [135, 136, 137],
    52: [138, 139, 140],
    53: [141, 142, 143],
    54: [144, 145],
    55: [146, 147, 148],
    56: [149, 150, 151],
    57: [152, 153, 154],
    58: [155, 156],
    59: [157, 158],
    60: [159, 160, 161],
    61: [162, 163, 164],
    62: [165, 166, 167],
    63: [168, 169, 170],
    66: [173, 174]
}
FALLBACK_QUESTION = """[CS:B]Um... there weren't enough questions available 
during randomization.[CR]"""
FALLBACK_ANSWER = "How embarrassing..."


class QuizRandomizer(AbstractRandomizer):
    def __init__(self, config: RandomizerConfig, rom: NintendoDSRom, static_data: Pmd2Data, seed: str, frontend: AbstractFrontend):
        super().__init__(config, rom, static_data, seed, frontend)

    def step_count(self) -> int:
        if self.config['quiz']['randomize']:
            return 1
        return 0

    def run(self, status: Status):
        if not self.config['quiz']['randomize']:
            return status.done()
        status.step("Randomizing Quiz...")

        question_block = self.static_data.string_index_data.string_blocks['Personality Quiz Questions']
        answer_block = self.static_data.string_index_data.string_blocks['Personality Quiz Answers']

        for lang, string_file in get_all_string_files(self.rom, self.static_data):
            two_answers_pool = []
            three_answers_pool = []
            four_or_more_answers_pool = []

            for q in self.config['quiz']['questions']:
                if len(q['answers']) == 2:
                    two_answers_pool.append(q)
                elif len(q['answers']) == 3:
                    three_answers_pool.append(q)
                else:
                    assert len(q['answers']) > 3
                    four_or_more_answers_pool.append(q)

            for game_question_id, game_answer_ids in QUESTION_MAPPING.items():
                assert len(game_answer_ids) > 1
                pools = [four_or_more_answers_pool]
                if len(game_answer_ids) == 2:
                    pools = [two_answers_pool, three_answers_pool, four_or_more_answers_pool]
                elif len(game_answer_ids) == 3:
                    pools = [three_answers_pool, four_or_more_answers_pool]
                while len(pools) > 0 and len(pools[0]) < 1:
                    pools.pop()
                if len(pools) > 0:
                    question = self._pick_question(len(game_answer_ids), pools[0])
                else:
                    question = self._generate_fallback_question(len(game_answer_ids))

                string_file.strings[question_block.begin + game_question_id] = question['question']
                for answer_id, answer in zip(game_answer_ids, question['answers']):
                    string_file.strings[answer_block.begin + answer_id] = answer

            self.rom.setFileByName(f'MESSAGE/{lang.filename}', FileType.STR.serialize(string_file))

        status.done()

    @staticmethod
    def _pick_question(answer_len, pool) -> QuizQuestion:
        question_idx = 0
        if len(pool) > 1:
            question_idx = randint(0, len(pool) - 1)
        question = pool.pop(question_idx)
        question['answers'] = question['answers'][:answer_len]
        assert len(question['answers']) == answer_len
        return question

    @staticmethod
    def _generate_fallback_question(answer_len) -> QuizQuestion:
        return {
            'question': FALLBACK_QUESTION,
            'answers': [FALLBACK_ANSWER for _ in range(answer_len)]
        }


if __name__ == '__main__':
    import json
    with open('/home/marco/dev/skytemple/skytemple/randomizer/skytemple_randomizer/data/default.json') as f:
        data = json.load(f)
    for question in data['quiz']['questions']:
        for answer in question['answers']:
            if len(answer) > 22:
                print(answer)
