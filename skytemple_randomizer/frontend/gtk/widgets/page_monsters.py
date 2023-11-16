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
    MonstersAbilitiesPage,
    MovesetsPage,
    TacticsIqPage,
    MonstersPoolPage,
    MonstersPoolType,
    RandomizationSettingsWindow,
)


@Gtk.Template(filename=os.path.join(MAIN_PATH, "page_monsters.ui"))
class MonstersPage(Adw.PreferencesPage):
    __gtype_name__ = "StMonstersPage"
    row_allowed_monsters = cast(Adw.ActionRow, Gtk.Template.Child())
    row_randomize_starters = cast(Adw.SwitchRow, Gtk.Template.Child())
    button_randomize_starters = cast(Gtk.Button, Gtk.Template.Child())
    row_randomize_npcs = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_randomize_abilities = cast(Adw.SwitchRow, Gtk.Template.Child())
    button_randomize_abilities = cast(Gtk.Button, Gtk.Template.Child())
    row_randomize_movesets = cast(Adw.ActionRow, Gtk.Template.Child())
    row_randomize_typings = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_tactics_iq = cast(Adw.ActionRow, Gtk.Template.Child())

    @Gtk.Template.Callback()
    def on_signal_for_dialog(self, w: Gtk.Widget, *args):
        dialog: RandomizationSettingsWindow | None = None
        if w == self.row_randomize_movesets:
            dialog = BaseSettingsDialog(
                title=self.row_randomize_movesets.get_title(), content=MovesetsPage()
            )
        if w == self.row_allowed_monsters:
            dialog = BaseSettingsDialog(
                title=self.row_allowed_monsters.get_title(),
                content=MonstersPoolPage(type=MonstersPoolType.ALL),
            )
        if w == self.button_randomize_starters:
            dialog = BaseSettingsDialog(
                title=self.row_randomize_starters.get_title(),
                content=MonstersPoolPage(type=MonstersPoolType.STARTERS),
            )
        if w == self.button_randomize_abilities:
            dialog = BaseSettingsDialog(
                title=self.row_randomize_abilities.get_title(),
                content=MonstersAbilitiesPage(),
            )
        if w == self.row_tactics_iq:
            dialog = BaseSettingsDialog(
                title=self.row_tactics_iq.get_title(),
                content=TacticsIqPage(),
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
    def on_row_randomize_starters_notify_active(self, *args):
        pass

    @Gtk.Template.Callback()
    def on_row_randomize_npcs_notify_active(self, *args):
        pass

    @Gtk.Template.Callback()
    def on_row_randomize_abilities_notify_active(self, *args):
        pass

    @Gtk.Template.Callback()
    def on_row_randomize_typings_notify_active(self, *args):
        pass

    def populate_settings(self, config: RandomizerConfig):
        pass
