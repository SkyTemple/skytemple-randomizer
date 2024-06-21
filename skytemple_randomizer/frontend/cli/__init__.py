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

import base64
import json
import os

import click

from skytemple_randomizer.config import (
    ConfigFileLoader,
    deep_typeddict_to_dict,
    EnumJsonEncoder,
    RandomizerConfig,
)
from skytemple_randomizer.data_dir import data_dir
from skytemple_randomizer.frontend.cli.config_argument import ConfigArgument
from skytemple_randomizer.frontend.cli.error import Error
from skytemple_randomizer.frontend.cli.randomize import run_randomization
from skytemple_randomizer.frontend.cli.rom_argument import RomArgument, LoadedRom
from skytemple_randomizer.frontend.cli import info


def init(cli: click.Group):
    @cli.command(help="Runs the Randomization.")
    @click.option("--print-result/--no-print-result", default=False)
    @click.argument("input_rom", cls=RomArgument)
    @click.argument("config", cls=ConfigArgument)
    @click.argument("output_rom", required=False)
    def randomize(
        input_rom: LoadedRom,
        config: RandomizerConfig,
        print_result: bool,
        output_rom: str | None,
    ):
        if print_result is False and output_rom is None:
            Error("Either OUTPUT_ROM or --print-result must be specified.").print_and_exit()
        elif print_result is True and output_rom is not None:
            Error("If --print-result is set, no OUTPUT_ROM must be specified.").print_and_exit()

        try:
            rom = run_randomization(input_rom, config)

            if output_rom:
                rom.saveToFile(output_rom, updateDeviceCapacity=True)
            else:
                data = rom.save(updateDeviceCapacity=True)
                click.echo(json.dumps({"data": base64.b64encode(data).decode("ascii")}))

        except Exception:
            Error.from_current_exception().print_and_exit()

    @cli.command(help="Prints the default config for the given ROM as JSON.")
    @click.argument("rom", cls=RomArgument)
    def default_config(rom: LoadedRom):
        # Currently the default config is the same for all regions.
        click.echo(
            json.dumps(
                deep_typeddict_to_dict(ConfigFileLoader.load(os.path.join(data_dir(), "default.json"))),
                cls=EnumJsonEncoder,
            ),
            nl=False,
        )

    @cli.command(help="Prints general metadata information about the ROM.")
    @click.argument("rom", cls=RomArgument)
    def info_rom(rom: LoadedRom):
        try:
            info.info_rom(rom)
        except Exception:
            Error.from_current_exception().print_and_exit()

    @cli.command(help="Prints the PPMDU config.")
    def ppmdu_config():
        try:
            info.ppmdu_config()
        except Exception:
            Error.from_current_exception().print_and_exit()

    @cli.command(help="Prints a mapping of monster group IDs and names from the ROM.")
    @click.argument("rom", cls=RomArgument)
    def info_monsters(rom: LoadedRom):
        try:
            info.info_monsters(rom)
        except Exception:
            Error.from_current_exception().print_and_exit()

    @cli.command(help="Prints a mapping of item IDs and names from the ROM.")
    @click.argument("rom", cls=RomArgument)
    def info_items(rom: LoadedRom):
        try:
            info.info_items(rom)
        except Exception:
            Error.from_current_exception().print_and_exit()

    @cli.command(help="Prints a mapping of move IDs and names from the ROM.")
    @click.argument("rom", cls=RomArgument)
    def info_moves(rom: LoadedRom):
        try:
            info.info_moves(rom)
        except Exception:
            Error.from_current_exception().print_and_exit()

    @cli.command(help="Prints a mapping of item categories and names.")
    @click.argument("rom", cls=RomArgument)
    def info_item_categories(rom: LoadedRom):
        try:
            info.info_item_categories(rom)
        except Exception:
            Error.from_current_exception().print_and_exit()

    @cli.command(help="Prints a mapping of ability IDs and names from the ROM.")
    @click.argument("rom", cls=RomArgument)
    def info_abilities(rom: LoadedRom):
        try:
            info.info_abilities(rom)
        except Exception:
            Error.from_current_exception().print_and_exit()

    @cli.command(help="Prints a mapping of dungeon IDs and names from the ROM.")
    @click.argument("rom", cls=RomArgument)
    def info_dungeons(rom: LoadedRom):
        try:
            info.info_dungeons(rom)
        except Exception:
            Error.from_current_exception().print_and_exit()
