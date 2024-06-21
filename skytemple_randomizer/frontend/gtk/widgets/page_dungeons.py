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
from typing import cast

from skytemple_randomizer.config import RandomizerConfig, DungeonModeConfig
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.widgets import (
    BaseSettingsDialog,
    DungeonsChancesPage,
    DungeonsSettingsPage,
    RandomizationSettingsWindow,
    DungeonsIndividualSettingsPage,
)


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_dungeons.ui"))
class DungeonsPage(Adw.PreferencesPage):
    __gtype_name__ = "StDungeonsPage"
    row_dungeon_mode = cast(Adw.ComboRow, Gtk.Template.Child())
    row_randomization_settings = cast(Adw.ActionRow, Gtk.Template.Child())
    row_chance_thresholds = cast(Adw.ActionRow, Gtk.Template.Child())
    row_per_dungeon_settings = cast(Adw.ActionRow, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    _suppress_signals: bool

    @Gtk.Template.Callback()
    def on_signal_for_dialog(self, w: Gtk.Widget, *args):
        dialog: RandomizationSettingsWindow | None = None
        if w == self.row_randomization_settings:
            dialog = BaseSettingsDialog(
                title=self.row_randomization_settings.get_title(),
                content=DungeonsSettingsPage(),
                content_width=512,
            )
        if w == self.row_chance_thresholds:
            dialog = BaseSettingsDialog(
                title=self.row_chance_thresholds.get_title(),
                content=DungeonsChancesPage(),
                content_width=512,
            )
        if w == self.row_per_dungeon_settings:
            p = DungeonsIndividualSettingsPage()
            dialog = BaseSettingsDialog(
                title=self.row_per_dungeon_settings.get_title(),
                content=p,
                help_callback=p.help_pool,
                search_callback=p.on_search_changed,
                end_button_factory=p.create_window_end_buttons,
            )

        if dialog is not None:
            frontend = GtkFrontend.instance()
            dialog.populate_settings(frontend.randomization_settings)
            dialog.present(frontend.window)
            return False

    @Gtk.Template.Callback()
    def on_row_dungeon_mode_starters_notify_selected(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["mode"] = DungeonModeConfig(self.row_dungeon_mode.get_selected())

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config
        self.row_dungeon_mode.set_selected(config["dungeons"]["mode"].value)
        self._suppress_signals = False
