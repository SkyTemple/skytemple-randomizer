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

import dataclasses
import json
import sys
import traceback
from typing import NoReturn, Any

import click


@dataclasses.dataclass
class Error:
    error_msg: str
    internal_error: bool = True
    traceback: str | None = None
    error_type: str | None = None

    @classmethod
    def from_current_exception(cls, prepend_msg: str = "", internal_error=True) -> Error:
        return cls.from_exception(*sys.exc_info(), prepend_msg=prepend_msg, internal_error=internal_error)

    @classmethod
    def from_exception(
        cls,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        trb: Any | None,
        *,
        prepend_msg: str = "",
        internal_error=True,
    ) -> Error:
        if prepend_msg != "":
            prepend_msg += ": "
        return Error(
            error_msg=f"{prepend_msg}{exc}",
            internal_error=internal_error,
            traceback="\n".join(traceback.format_tb(trb)) if trb is not None else None,
            error_type=typ.__name__ if typ is not None else None,
        )

    def print(self):
        click.echo(json.dumps(self.__dict__), nl=False)

    def print_and_exit(self, exit_code=1) -> NoReturn:
        self.print()
        sys.stdout.flush()
        sys.stderr.flush()
        sys.exit(exit_code)
