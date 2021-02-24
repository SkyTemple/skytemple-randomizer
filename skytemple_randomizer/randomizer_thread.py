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
import logging
import sys
from threading import Thread, Lock
from typing import List

from ndspy.rom import NintendoDSRom

from skytemple_files.common.util import get_ppmdu_config_for_rom
from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.boss import BossRandomizer
from skytemple_randomizer.randomizer.chapter import ChapterRandomizer
from skytemple_randomizer.randomizer.dungeon import DungeonRandomizer
from skytemple_randomizer.randomizer.dungeon_unlocker import DungeonUnlocker
from skytemple_randomizer.randomizer.fixed_room import FixedRoomRandomizer
from skytemple_randomizer.randomizer.global_items import GlobalItemsRandomizer
from skytemple_randomizer.randomizer.location import LocationRandomizer
from skytemple_randomizer.randomizer.monster import MonsterRandomizer
from skytemple_randomizer.randomizer.moveset import MovesetRandomizer
from skytemple_randomizer.randomizer.npc import NpcRandomizer
from skytemple_randomizer.randomizer.overworld_music import OverworldMusicRandomizer
from skytemple_randomizer.randomizer.patch_applier import PatchApplier
from skytemple_randomizer.randomizer.portrait_downloader import PortraitDownloader
from skytemple_randomizer.randomizer.recruitment_table import RecruitmentTableRandomizer
from skytemple_randomizer.randomizer.seed_info import SeedInfo
from skytemple_randomizer.randomizer.starter import StarterRandomizer
from skytemple_randomizer.randomizer.text_main import TextMainRandomizer
from skytemple_randomizer.randomizer.text_script import TextScriptRandomizer
from skytemple_randomizer.randomizer.util.util import save_scripts
from skytemple_randomizer.status import Status


RANDOMIZERS = [
    PatchApplier, NpcRandomizer, StarterRandomizer, BossRandomizer, RecruitmentTableRandomizer, DungeonRandomizer,
    FixedRoomRandomizer, DungeonUnlocker, PortraitDownloader, MonsterRandomizer, MovesetRandomizer,
    LocationRandomizer, ChapterRandomizer, TextMainRandomizer, TextScriptRandomizer, GlobalItemsRandomizer,
    OverworldMusicRandomizer, SeedInfo
]
logger = logging.getLogger(__name__)


class RandomizerThread(Thread):
    def __init__(self, status: Status, rom: NintendoDSRom, config: RandomizerConfig, seed: str):
        """
        Inits the thread. If it's started() access to rom and config MUST NOT be done until is_done().
        is_done is also signaled by the status object's done() event.
        The max number of steps can be retrieved with the attribute 'total_steps'.
        If there's an error, this is marked as done and the error attribute contains the exception.
        """
        super().__init__()
        self.status = status
        self.rom = rom
        self.config = config
        self.lock = Lock()
        self.done = False

        self.static_data = get_ppmdu_config_for_rom(rom)
        self.randomizers: List[AbstractRandomizer] = []
        for cls in RANDOMIZERS:
            self.randomizers.append(cls(config, rom, self.static_data, seed))

        self.total_steps = sum(x.step_count() for x in self.randomizers) + 1
        self.error = None

    def run(self):
        try:
            for randomizer in self.randomizers:
                local_status_steps_left = randomizer.step_count()
                local_status = Status()

                def local_status_fn(_, descr):
                    nonlocal local_status_steps_left
                    if descr != Status.DONE_SPECIAL_STR:
                        if local_status_steps_left > 0:
                            local_status_steps_left -= 1
                        self.status.step(descr)
                    else:
                        for i in range(local_status_steps_left):
                            self.status.step('Randomizing...')

                local_status.subscribe(local_status_fn)
                randomizer.run(local_status)
            self.status.step('Saving scripts...')
            save_scripts(self.rom, self.static_data)
        except BaseException as error:
            logger.error("Exception during randomization.", exc_info=error)
            self.error = sys.exc_info()

        with self.lock:
            self.done = True
            self.status.done()

    def is_done(self) -> bool:
        with self.lock:
            return self.done
