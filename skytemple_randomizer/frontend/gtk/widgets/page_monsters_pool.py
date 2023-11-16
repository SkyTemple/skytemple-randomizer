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

import os
from enum import Enum, auto

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw


class MonstersPoolType(Enum):
    ALL = auto()
    STARTERS = auto()


@Gtk.Template(filename=os.path.join(MAIN_PATH, "page_monsters_pool.ui"))
class MonstersPoolPage(Adw.PreferencesPage):
    __gtype_name__ = "StMonstersPoolPage"

    def __init__(
        self,
        *args,
        type: MonstersPoolType,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # todo

    def populate_settings(self, config: RandomizerConfig):
        pass
