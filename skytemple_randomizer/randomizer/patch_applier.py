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
from time import sleep

from skytemple_files.common.i18n_util import _
from skytemple_files.common.types.file_types import FileType
from skytemple_files.patch.patches import Patcher

from skytemple_randomizer.config import QuizMode
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.status import Status


class PatchApplier(AbstractRandomizer):
    def step_count(self) -> int:
        i = 1
        if self.config["improvements"]["patch_moveshortcuts"]:
            i += 1
        if self.config["improvements"]["patch_unuseddungeonchance"]:
            i += 1
        if self.config["improvements"]["patch_totalteamcontrol"]:
            i += 1
        if self.config["improvements"]["patch_fixmemorysoftlock"]:
            i += 1
        if self.config["improvements"]["patch_disarm_monster_houses"]:
            i += 1
        if self.config["improvements"]["patch_sametypepartner"]:
            i += 1
        if self.config["quiz"]["mode"] != QuizMode.TEST:
            i += 1
        return i

    def run(self, status: Status):
        patcher = Patcher(self.rom, self.static_data)

        status.step(_("Apply base patches by psy_commando and Frostbyte..."))
        sleep(5)  # gotta give some spotlight to them.
        if not patcher.is_applied("ActorAndLevelLoader"):
            patcher.apply("ActorAndLevelLoader")
        if not patcher.is_applied("ProvideATUPXSupport"):
            patcher.apply("ProvideATUPXSupport")
        if not patcher.is_applied("ExtraSpace"):
            patcher.apply("ExtraSpace")
        if not patcher.is_applied("AntiSoftlock"):
            patcher.apply("AntiSoftlock")
        # FixEvolutionGlitch shenanigans
        cannot_apply_fixevo = True
        try:
            cannot_apply_fixevo = patcher.is_applied("FixEvolutionGlitch")
        except NotImplementedError:
            pass
        if not cannot_apply_fixevo:
            patcher.apply("FixEvolutionGlitch")

        if self.config["improvements"]["patch_moveshortcuts"]:
            status.step(_("Apply 'MoveShortcuts' patch..."))
            if not patcher.is_applied("MoveShortcuts"):
                patcher.apply("MoveShortcuts")

        if self.config["improvements"]["patch_unuseddungeonchance"]:
            status.step(_("Apply 'UnusedDungeonChance' patch..."))
            if not patcher.is_applied("UnusedDungeonChance"):
                patcher.apply("UnusedDungeonChance")

        if self.config["improvements"]["patch_totalteamcontrol"]:
            status.step(_("Apply 'Complete Team Control' patches..."))
            if not patcher.is_applied("CompleteTeamControl"):
                patcher.apply("CompleteTeamControl")
            if not patcher.is_applied("FarOffPalOverdrive"):
                patcher.apply("FarOffPalOverdrive")
            if not patcher.is_applied("PartnersTriggerHiddenTraps"):
                patcher.apply("PartnersTriggerHiddenTraps")
            if not patcher.is_applied("ReduceJumpcutPauseTime"):
                patcher.apply("ReduceJumpcutPauseTime")

        if not patcher.is_applied("NoWeatherStop"):
            patcher.apply("NoWeatherStop")

        if not patcher.is_applied("RemoveBodySizeCheck"):
            patcher.apply("RemoveBodySizeCheck")

        if self.config["quiz"]["mode"] != QuizMode.TEST:
            status.step(_("Apply personality test patches..."))
            if not patcher.is_applied("ChooseStarter"):
                patcher.apply("ChooseStarter")
            if self.config["quiz"]["mode"] == QuizMode.ASK:
                if not patcher.is_applied("SkipQuiz"):
                    patcher.apply("SkipQuiz")

        if self.config["improvements"]["patch_fixmemorysoftlock"]:
            status.step(_("Apply 'FixMemorySoftlock' patch..."))
            if not patcher.is_applied("FixMemorySoftlock"):
                patcher.apply("FixMemorySoftlock")

        if self.config["improvements"]["patch_sametypepartner"]:
            status.step(_("Apply 'SameTypePartner' patch..."))
            if not patcher.is_applied("SameTypePartner"):
                patcher.apply("SameTypePartner")

        if self.config["improvements"]["patch_disarm_monster_houses"]:
            status.step(_("Apply 'DisarmOneRoomMonsterHouses' patch..."))
            if not patcher.is_applied("DisarmOneRoomMonsterHouses"):
                patcher.apply("DisarmOneRoomMonsterHouses")

        # Change MD properties if ExpandPokeList patch is applied
        md_properties = FileType.MD.properties()
        expand_poke_applied = False
        try:
            expand_poke_applied = patcher.is_applied("ExpandPokeList")
        except NotImplementedError:
            pass

        if expand_poke_applied:
            md_properties.num_entities = 2048
            md_properties.max_possible = 2048
        else:
            md_properties.num_entities = 600
            md_properties.max_possible = 554

        status.done()
