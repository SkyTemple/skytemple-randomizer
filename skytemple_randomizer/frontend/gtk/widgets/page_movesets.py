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

from typing import TYPE_CHECKING, cast

from skytemple_randomizer.config import RandomizerConfig, MovesetConfig
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

if TYPE_CHECKING:
    from skytemple_randomizer.frontend.gtk.widgets import MonstersPage


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_movesets.ui"))
class MovesetsPage(Adw.PreferencesPage):
    __gtype_name__ = "StMovesetsPage"
    row_movesets = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_restrictions = cast(Adw.ComboRow, Gtk.Template.Child())
    row_tm_hm_movesets = cast(Adw.SwitchRow, Gtk.Template.Child())

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

        self.row_movesets.set_active(config["pokemon"]["movesets"] != MovesetConfig.NO)
        self.select_restriction(config["pokemon"]["movesets"])
        self.row_tm_hm_movesets.set_active(config["pokemon"]["tm_hm_movesets"])

        self._suppress_signals = False

    @Gtk.Template.Callback()
    def on_row_movesets_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        if self.row_movesets.get_active():
            self.randomization_settings["pokemon"]["movesets"] = self.current_restriction()
        else:
            self.randomization_settings["pokemon"]["movesets"] = MovesetConfig.NO

    @Gtk.Template.Callback()
    def on_row_restrictions_notify_selected(self, *args):
        if self._suppress_signals or not self.row_movesets.get_active():
            return
        assert self.randomization_settings is not None
        self.randomization_settings["pokemon"]["movesets"] = self.current_restriction()

    @Gtk.Template.Callback()
    def on_row_tm_hm_movesets_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["pokemon"]["tm_hm_movesets"] = self.row_tm_hm_movesets.get_active()

    def select_restriction(self, config: MovesetConfig):
        selected_idx = config.value - 1
        self.row_restrictions.set_selected(selected_idx if selected_idx > 0 else 0)

    def current_restriction(self) -> MovesetConfig:
        return MovesetConfig(self.row_restrictions.get_selected() + 1)
