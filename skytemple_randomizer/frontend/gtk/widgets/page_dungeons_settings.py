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

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_dungeons_settings.ui"))
class DungeonsSettingsPage(Adw.PreferencesPage):
    __gtype_name__ = "StDungeonsSettingsPage"
    row_layouts = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_weather = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_items = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_monsters = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_traps = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_fixed_rooms = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_min_floor_change_percent = cast(Adw.SpinRow, Gtk.Template.Child())
    row_max_floor_change_percent = cast(Adw.SpinRow, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    _suppress_signals: bool

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.randomization_settings = None
        self._suppress_signals = False

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config

        self.row_layouts.set_active(config["dungeons"]["layouts"])
        self.row_weather.set_active(config["dungeons"]["weather"])
        self.row_items.set_active(config["dungeons"]["items"])
        self.row_monsters.set_active(config["dungeons"]["pokemon"])
        self.row_traps.set_active(config["dungeons"]["traps"])
        self.row_fixed_rooms.set_active(config["dungeons"]["fixed_rooms"])
        self.row_min_floor_change_percent.set_value(config["dungeons"]["min_floor_change_percent"].value)
        self.row_max_floor_change_percent.set_value(config["dungeons"]["max_floor_change_percent"].value)

        self._suppress_signals = False

    @Gtk.Template.Callback()
    def on_row_layouts_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["layouts"] = self.row_layouts.get_active()

    @Gtk.Template.Callback()
    def on_row_weather_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["weather"] = self.row_weather.get_active()

    @Gtk.Template.Callback()
    def on_row_items_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["items"] = self.row_items.get_active()

    @Gtk.Template.Callback()
    def on_row_monsters_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["pokemon"] = self.row_monsters.get_active()

    @Gtk.Template.Callback()
    def on_row_traps_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["traps"] = self.row_traps.get_active()

    @Gtk.Template.Callback()
    def on_row_fixed_rooms_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["fixed_rooms"] = self.row_fixed_rooms.get_active()

    @Gtk.Template.Callback()
    def on_row_min_floor_change_percent_notify_value(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["min_floor_change_percent"].value = int(
            self.row_min_floor_change_percent.get_value()
        )

    @Gtk.Template.Callback()
    def on_row_max_floor_change_percent_notify_value(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["max_floor_change_percent"].value = int(
            self.row_max_floor_change_percent.get_value()
        )
