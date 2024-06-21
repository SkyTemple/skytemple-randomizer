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

import struct
from typing import Any, Sequence

import click
from ndspy.rom import NintendoDSRom
from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.common.util import get_ppmdu_config_for_rom

from skytemple_randomizer.frontend.cli.error import Error


class LoadedRom:
    __slots__ = ["rom", "static_data"]
    rom: NintendoDSRom
    static_data: Pmd2Data

    def __init__(self, rom: NintendoDSRom, static_data: Pmd2Data):
        self.rom = rom
        self.static_data = static_data


class RomArgument(click.Argument):
    def __init__(
        self,
        param_decls: Sequence[str],
        required: bool | None = None,
        **attrs: Any,
    ):
        super().__init__(param_decls, required, **attrs, callback=self.read_rom)

    @staticmethod
    def read_rom(_ctx: click.Context, _slf: click.Parameter, val: Any) -> LoadedRom:
        try:
            rom = NintendoDSRom.fromFile(val)
            static_data = get_ppmdu_config_for_rom(rom)
            return LoadedRom(rom=rom, static_data=static_data)
        except struct.error:
            Error("Failed to open ROM. Not a valid ROM file.", internal_error=False).print_and_exit()
        except Exception as e:
            Error.from_current_exception("Failed to open ROM", internal_error=False).print_and_exit()
