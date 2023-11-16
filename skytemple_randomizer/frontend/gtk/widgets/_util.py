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
from __future__ import annotations

import typing
from asyncio import Protocol
from typing import TYPE_CHECKING

from skytemple_randomizer.config import RandomizerConfig


if TYPE_CHECKING:
    # todo: Python does not have intersection types at the moment.
    from gi.repository import Gtk

    class RandomizationSettingsWidget(Protocol):
        def populate_settings(self, config: RandomizerConfig):
            ...

    class RandomizationSettingsWindow(RandomizationSettingsWidget):
        def set_default_size(self, w: int, h: int):
            ...

        def set_transient_for(self, window: Gtk.Window | None):
            ...

        def set_application(self, app: Gtk.Application | None):
            ...

        def present(self):
            ...

else:
    RandomizationSettingsWidget = typing.Any
    RandomizationSettingsWindow = typing.Any
