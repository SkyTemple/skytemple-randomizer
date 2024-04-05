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

import typing
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    # todo: Python does not have intersection types at the moment.
    from typing import Protocol
    from gi.repository import Gtk
    from skytemple_randomizer.config import RandomizerConfig

    class RandomizationSettingsWidget(Protocol):
        def populate_settings(self, config: RandomizerConfig): ...

    class RandomizationSettingsWindow(RandomizationSettingsWidget, Protocol):
        def present(self, widget: Gtk.Widget): ...

else:
    RandomizationSettingsWidget = typing.Any
    RandomizationSettingsWindow = typing.Any
