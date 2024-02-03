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

import os

from typing import TYPE_CHECKING

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

if TYPE_CHECKING:
    from skytemple_randomizer.frontend.gtk.widgets import MonstersPage


@Gtk.Template(filename=os.path.join(MAIN_PATH, "page_movesets.ui"))
class MovesetsPage(Adw.PreferencesPage):
    __gtype_name__ = "StMovesetsPage"

    randomization_settings: RandomizerConfig | None
    parent_page: MonstersPage
    _suppress_signals: bool

    def __init__(
        self,
        *args,
        parent_page: MonstersPage,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parent_page = parent_page
        self.randomization_settings = None
        self._suppress_signals = False

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config
        # todo
        # TODO: We need to sync the selected moveset randomization type with parent, so the current value
        #       of the checkbox.
        self._suppress_signals = False

    def get_enabled(self) -> bool:
        return self.parent_page.row_randomize_movesets.get_active()

    def set_enabled(self, state: bool):
        self.parent_page.row_randomize_movesets.set_active(state)
