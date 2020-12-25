#  Copyright 2020 Parakoopa
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
from threading import Thread, Lock
from typing import Optional, List

from ndspy.rom import NintendoDSRom

from skytemple_files.common.util import get_ppmdu_config_for_rom
from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.randomizer.abstract import TestRandomizer, AbstractRandomizer
from skytemple_randomizer.status import Status


RANDOMIZERS = [
    TestRandomizer, TestRandomizer
]


class RandomizerThread(Thread):
    def __init__(self, status: Status, rom: NintendoDSRom, config: RandomizerConfig):
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

        staic_data = get_ppmdu_config_for_rom(rom)
        self.randomizers: List[AbstractRandomizer] = []
        for cls in RANDOMIZERS:
            self.randomizers.append(cls(config, rom, staic_data))

        self.total_steps = sum(x.step_count() for x in self.randomizers)
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
        except BaseException as error:
            self.error = error

        with self.lock:
            self.done = True
            self.status.done()

    def is_done(self) -> bool:
        with self.lock:
            return self.done
