#  Copyright 2020-2023 Capypara and the SkyTemple Contributors
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
from abc import ABC, abstractmethod

from ndspy.rom import NintendoDSRom

from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.abstract import AbstractFrontend
from skytemple_randomizer.status import Status


class AbstractRandomizer(ABC):
    def __init__(self, config: RandomizerConfig, rom: NintendoDSRom, static_data: Pmd2Data, seed: str, frontend: AbstractFrontend):
        self.config = config
        self.rom = rom
        self.static_data = static_data
        self.seed = seed
        self.frontend = frontend

    @abstractmethod
    def step_count(self) -> int:
        """The number of steps that this randomizer will go through"""

    @abstractmethod
    def run(self, status: Status):
        """
        Run the randomization.
        Updates status completions at status. status.step(description_string) is run for each started new step
        of the randomization, up to self.step_count() times. status.done() is run when this randomizer is finished.
        """
