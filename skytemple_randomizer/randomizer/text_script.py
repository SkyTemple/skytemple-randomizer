#  Copyright 2020-2024 Capypara and the SkyTemple Contributors
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
from random import shuffle

from skytemple_files.common.ppmdu_config.data import GAME_REGION_JP
from skytemple_files.common.util import get_files_from_rom_with_extension
from skytemple_files.script.ssb.model import Ssb
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import (
    get_all_string_files,
    get_script,
)
from skytemple_randomizer.status import Status
from skytemple_files.common.i18n_util import _


class TextScriptRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config["text"]["story"]:
            return 2
        return 0

    def run(self, status: Status):
        if not self.config["text"]["story"]:
            return status.done()
        status.step(_("Randomizing all script text: Reading strings..."))

        if self.static_data.game_region == GAME_REGION_JP:
            return self.run_for_jp(status)

        all_strings_langs = {}
        for lang, __ in get_all_string_files(self.rom, self.static_data):
            all_strings: list[str] = []
            ssb_map: dict[str, Ssb] = {}
            all_strings_langs[lang] = all_strings, ssb_map
            for file_path in get_files_from_rom_with_extension(self.rom, "ssb"):
                script = get_script(file_path, self.rom, self.static_data)
                all_strings += script.strings[lang.name.lower()]
                ssb_map[file_path] = script

        status.step(_("Randomizing all script text: Writing strings..."))
        for lang, (all_strings, ssb_map) in all_strings_langs.items():
            shuffle(all_strings)
            for file_path, script in ssb_map.items():
                samples = []
                for ___ in range(0, len(script.strings[lang.name.lower()])):
                    samples.append(all_strings.pop())
                script.strings[lang.name.lower()] = samples

        status.done()

    def run_for_jp(self, status: Status):
        # The JP ROM uses constant strings.
        # TODO:
        #   See https://github.com/SkyTemple/skytemple-randomizer/issues/153
        #   This is not trivial to implement for the JP ROM. We need to make sure to only
        #   the parameters for opcodes that use language strings in the EU/NA ROM are updated, because
        #   the game also uses constant strings for things such as loading scenes. Randomizing these with the
        #   rest WILL lead to problems.
        #
        #   However the approach used for EU/NA is way to simple and will not work here. We would need to go through
        #   the parameters, note their position and then when rebuilding the constant table for an SSB script
        #   make sure that somehow all strings we don't want to change are still there...
        #
        #   Opcode and parameter combinations that use language strings in the EU ROM:
        #       ('message_Talk', 0)
        #       ('CaseText', 1)
        #       ('back_SetSpecialEpisodeBanner', 1)
        #       ('message_Mail', 0)
        #       ('DefaultText', 0)
        #       ('back_SetBanner', 1)
        #       ('back_SetTitleBanner', 1)
        #       ('CaseMenu', 0)
        #       ('back_SetBanner2', 5)
        #       ('back_SetSpecialEpisodeBanner3', 1)
        #       ('message_ImitationSound', 0)
        #       ('back_SetSpecialEpisodeBanner2', 1)
        #       ('message_Notice', 0)
        #       ('message_Monologue', 0)
        #       ('message_Narration', 1)
        #       ('message_Explanation', 0)
        status.done()
