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

from typing import Any, Sequence

import click

from skytemple_randomizer.config import RandomizerConfig, ConfigFileLoader
from skytemple_randomizer.frontend.cli.error import Error


class ConfigArgument(click.Argument):
    def __init__(
        self,
        param_decls: Sequence[str],
        required: bool | None = None,
        **attrs: Any,
    ):
        super().__init__(param_decls, required, **attrs, callback=self.read_config)

    @staticmethod
    def read_config(_ctx: click.Context, _slf: click.Parameter, val: Any) -> RandomizerConfig:
        try:
            return ConfigFileLoader.load(val)
        except Exception as e:
            Error.from_current_exception("The config file provided is invalid", internal_error=False).print_and_exit()
