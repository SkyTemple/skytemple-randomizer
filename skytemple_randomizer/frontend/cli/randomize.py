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
from __future__ import annotations

import json
import random
from functools import partial
from time import sleep
from typing import TYPE_CHECKING, Callable, TypedDict

import click
import sys
from ndspy.rom import NintendoDSRom

from skytemple_randomizer.frontend.abstract import AbstractFrontend, PortraitDebugLine
from skytemple_randomizer.randomizer_thread import RandomizerThread
from skytemple_randomizer.status import Status
from skytemple_randomizer.config import RandomizerConfig, get_effective_seed

if TYPE_CHECKING:
    from skytemple_randomizer.frontend.cli import LoadedRom


class CliFrontend(AbstractFrontend):
    def idle_add(self, fn: Callable):
        fn()

    def portrait_debug__add(self, line: PortraitDebugLine):
        if line.status == "failed":
            print(
                f"Warning: Failed to download a portrait/sprite: {line.monster_name} {line.form_name} "
                f"({line.monster_idx}/{line.form_idx}):\n{line.traceback}",
                file=sys.stderr,
                flush=True,
            )


class Progress(TypedDict):
    current_step: int
    total_steps: int
    current_step_description: str


class Done(TypedDict):
    done: bool


def run_randomization(rom: LoadedRom, config: RandomizerConfig) -> NintendoDSRom:
    status = Status()
    seed = get_effective_seed(config["seed"])
    random.seed(seed)
    randomizer = RandomizerThread(
        status,
        rom.rom,
        config,
        str(seed),
        CliFrontend(),
    )
    status.subscribe(partial(status_update, randomizer))
    randomizer.start()

    while True:
        if check_done(randomizer):
            break
        sleep(0.2)

    return rom.rom


def status_update(randomizer: RandomizerThread, progress: int, description: str):
    if description == Status.DONE_SPECIAL_STR:
        return
    click.echo(
        json.dumps(
            Progress(
                current_step=progress,
                total_steps=randomizer.total_steps,
                current_step_description=description,
            )
        )
    )


def check_done(randomizer: RandomizerThread) -> bool:
    if not randomizer.is_done():
        return False

    if randomizer.error:
        from skytemple_randomizer.frontend.cli import Error

        Error.from_exception(*randomizer.error, prepend_msg="Randomizing failed").print_and_exit(2)
    else:
        click.echo(json.dumps(Done(done=True)))
    return True
