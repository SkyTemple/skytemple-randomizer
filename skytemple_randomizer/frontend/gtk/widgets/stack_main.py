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
import sys
import webbrowser
from typing import cast

from ndspy.rom import NintendoDSRom
from skytemple_files.common.i18n_util import _
from skytemple_files.common.ppmdu_config.data import Pmd2Data

from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, GObject

from skytemple_randomizer.frontend.gtk.widgets import (
    RandomizeDialog,
    RandomizationSettingsWidget,
    BaseSettingsDialog,
    SettingsPage,
    WelcomePage,
)


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "stack_main.ui"))
class MainStack(Adw.Bin):
    __gtype_name__ = "StMainStack"

    header_bar = cast(Gtk.HeaderBar, Gtk.Template.Child())
    view_switcher = cast(Adw.ViewSwitcher, Gtk.Template.Child())
    switcher_bar = cast(Adw.ViewSwitcherBar, Gtk.Template.Child())
    page_start = cast(Adw.ViewStackPage, Gtk.Template.Child())
    page_monsters = cast(Adw.ViewStackPage, Gtk.Template.Child())
    page_dungeons = cast(Adw.ViewStackPage, Gtk.Template.Child())
    page_text = cast(Adw.ViewStackPage, Gtk.Template.Child())
    page_tweaks = cast(Adw.ViewStackPage, Gtk.Template.Child())
    button_settings_content = cast(Adw.ButtonContent, Gtk.Template.Child())

    input_rom_path: str | None
    rom: NintendoDSRom | None
    rom_static_data: Pmd2Data | None

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.input_rom_path = None
        self.rom = None
        self.rom_static_data = None

    def init_rom(
        self,
        rom_path: str,
        rom: NintendoDSRom,
        rom_static_data: Pmd2Data,
    ):
        self.input_rom_path = rom_path
        self.rom = rom
        self.rom_static_data = rom_static_data

        cast(WelcomePage, self.page_start.get_child()).set_input_rom(self.input_rom_path, self.rom_static_data)

        frontend = GtkFrontend.instance()
        frontend.init_rom(self.rom, self.rom_static_data)
        self.populate_settings()

    @GObject.Property(type=bool, default=False)
    def mobile_view(self):
        return self.switcher_bar.get_reveal()

    @mobile_view.setter  # type: ignore
    def mobile_view(self, value):
        if value:
            self.header_bar.set_title_widget(None)
            self.switcher_bar.set_reveal(True)
            self.button_settings_content.set_label("")
        else:
            self.header_bar.set_title_widget(self.view_switcher)
            self.switcher_bar.set_reveal(False)
            self.button_settings_content.set_label(_("Settings"))

    @Gtk.Template.Callback()
    def on_realize(self, *args):
        if sys.platform.startswith("darwin"):
            self.header_bar.set_decoration_layout("close,minimize,maximize:")

    @Gtk.Template.Callback()
    def on_button_randomize_clicked(self, *args):
        frontend = GtkFrontend.instance()
        assert self.rom is not None
        assert self.rom_static_data is not None
        assert self.input_rom_path is not None
        RandomizeDialog(
            self.input_rom_path,
            self.rom,
            self.rom_static_data,
            frontend.randomization_settings,
        ).present(GtkFrontend.instance().window)

    @Gtk.Template.Callback()
    def on_button_settings_clicked(self, *args):
        frontend = GtkFrontend.instance()
        dialog = BaseSettingsDialog(
            title=_("Settings"),
            content=SettingsPage(repopulate_randomization_settings=self.populate_settings),
            content_width=320,
        )
        dialog.populate_settings(GtkFrontend.instance().randomization_settings)
        dialog.present(frontend.window)

    @Gtk.Template.Callback()
    def on_button_help_clicked(self, *args):
        webbrowser.open_new_tab("https://wiki.skytemple.org/index.php/SkyTemple:UI-Link/skytemple-randomizer")

    @Gtk.Template.Callback()
    def on_button_load_rom_clicked(self, *args):
        def on_response(_, response):
            if response == "Yes":
                GtkFrontend.instance().application.show_start_stack(disable_recent=True)

        d = Adw.AlertDialog(
            body=_(
                "Your settings will be discarded and will be replaced by default settings matching the new ROM you open. Make sure to save your settings if you need them."
            ),
            heading=_("Close current ROM?"),
        )
        d.add_response("No", _("_No"))
        d.add_response("Yes", _("_Yes"))
        d.set_response_appearance("Yes", Adw.ResponseAppearance.DESTRUCTIVE)
        d.connect("response", on_response)
        d.present(GtkFrontend.instance().window)

    def populate_settings(self):
        frontend = GtkFrontend.instance()
        cast(RandomizationSettingsWidget, self.page_dungeons.get_child()).populate_settings(
            frontend.randomization_settings
        )
        cast(RandomizationSettingsWidget, self.page_monsters.get_child()).populate_settings(
            frontend.randomization_settings
        )
        cast(RandomizationSettingsWidget, self.page_text.get_child()).populate_settings(frontend.randomization_settings)
        cast(RandomizationSettingsWidget, self.page_tweaks.get_child()).populate_settings(
            frontend.randomization_settings
        )
