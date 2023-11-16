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
from typing import cast

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.widgets import (
    BaseSettingsDialog,
    DungeonsIndividualSettingsDialog,
    DungeonsChancesPage,
    DungeonsSettingsPage,
    RandomizationSettingsWindow,
)


@Gtk.Template(filename=os.path.join(MAIN_PATH, "page_dungeons.ui"))
class DungeonsPage(Adw.PreferencesPage):
    __gtype_name__ = "StDungeonsPage"
    row_dungeon_mode = cast(Adw.ComboRow, Gtk.Template.Child())
    row_randomization_settings = cast(Adw.ActionRow, Gtk.Template.Child())
    row_chance_thresholds = cast(Adw.ActionRow, Gtk.Template.Child())
    row_per_dungeon_settings = cast(Adw.ActionRow, Gtk.Template.Child())

    @Gtk.Template.Callback()
    def on_signal_for_dialog(self, w: Gtk.Widget, *args):
        dialog: RandomizationSettingsWindow | None = None
        if w == self.row_randomization_settings:
            dialog = BaseSettingsDialog(
                title=self.row_randomization_settings.get_title(),
                content=DungeonsSettingsPage(),
            )
        if w == self.row_chance_thresholds:
            dialog = BaseSettingsDialog(
                title=self.row_chance_thresholds.get_title(),
                content=DungeonsChancesPage(),
            )
        if w == self.row_per_dungeon_settings:
            dialog = DungeonsIndividualSettingsDialog(
                title=self.row_per_dungeon_settings.get_title(),
            )

        if dialog is not None:
            frontend = GtkFrontend.instance()
            width, height = frontend.window.get_default_size()
            dialog.set_default_size(round(width * 0.8), round(height * 0.8))
            dialog.populate_settings(frontend.randomization_settings)
            dialog.set_transient_for(frontend.window)
            dialog.set_application(frontend.application)
            dialog.present()
            return False

    @Gtk.Template.Callback()
    def on_row_dungeon_mode_starters_notify_selected(self, *args):
        pass

    def populate_settings(self, config: RandomizerConfig):
        pass
