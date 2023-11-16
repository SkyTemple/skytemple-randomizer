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
import sys
import webbrowser
from typing import cast

from skytemple_files.common.i18n_util import _

from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.widgets import (
    RandomizeDialog,
    RandomizationSettingsWidget,
    BaseSettingsDialog,
    SettingsPage,
)


@Gtk.Template(filename=os.path.join(MAIN_PATH, "window_main.ui"))
class MainWindow(Adw.ApplicationWindow):
    __gtype_name__ = "StMainWindow"

    header_bar = cast(Gtk.HeaderBar, Gtk.Template.Child())
    page_monsters = cast(Adw.ViewStackPage, Gtk.Template.Child())
    page_dungeons = cast(Adw.ViewStackPage, Gtk.Template.Child())
    page_text = cast(Adw.ViewStackPage, Gtk.Template.Child())
    page_tweaks = cast(Adw.ViewStackPage, Gtk.Template.Child())

    @Gtk.Template.Callback()
    def on_main_window_realize(self, *args):
        if sys.platform.startswith("darwin"):
            self.header_bar.set_decoration_layout("close,minimize,maximize:")

        frontend = GtkFrontend.instance()
        frontend.window = self
        window_size = frontend.settings.get_window_size()
        if window_size is not None:
            self.set_default_size(*window_size)
        if frontend.settings.get_window_maximized():
            self.maximize()
        else:
            self.unmaximize()

        self.populate_settings()

    @Gtk.Template.Callback()
    def on_button_randomize_clicked(self, *args):
        dialog = RandomizeDialog(
            transient_for=self, destroy_with_parent=True, modal=True
        )
        dialog.present()

    @Gtk.Template.Callback()
    def on_button_settings_clicked(self, *args):
        dialog = BaseSettingsDialog(
            title=_("Settings"),
            content=SettingsPage(
                repopulate_randomization_settings=self.populate_settings
            ),
        )
        w, h = self.get_default_size()
        dialog.set_default_size(round(w * 0.8), 420)
        dialog.populate_settings(GtkFrontend.instance().randomization_settings)
        dialog.set_transient_for(self)
        dialog.set_application(self.get_application())
        dialog.present()

    @Gtk.Template.Callback()
    def on_button_help_clicked(self, *args):
        webbrowser.open_new_tab(
            "https://wiki.skytemple.org/index.php/SkyTemple:UI-Link/skytemple-randomizer"
        )

    @Gtk.Template.Callback()
    def on_main_window_notify_default_width(self, *args):
        GtkFrontend.instance().settings.set_window_width(self.get_width())

    @Gtk.Template.Callback()
    def on_main_window_notify_default_height(self, *args):
        GtkFrontend.instance().settings.set_window_height(self.get_height())

    @Gtk.Template.Callback()
    def on_main_window_notify_maximized(self, *args):
        GtkFrontend.instance().settings.set_window_maximized(self.is_maximized())

    def populate_settings(self):
        frontend = GtkFrontend.instance()
        cast(
            RandomizationSettingsWidget, self.page_dungeons.get_child()
        ).populate_settings(frontend.randomization_settings)
        cast(
            RandomizationSettingsWidget, self.page_monsters.get_child()
        ).populate_settings(frontend.randomization_settings)
        cast(RandomizationSettingsWidget, self.page_text.get_child()).populate_settings(
            frontend.randomization_settings
        )
        cast(
            RandomizationSettingsWidget, self.page_tweaks.get_child()
        ).populate_settings(frontend.randomization_settings)
