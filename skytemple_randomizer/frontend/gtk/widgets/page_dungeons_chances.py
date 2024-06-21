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


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_dungeons_chances.ui"))
class DungeonsChancesPage(Adw.PreferencesPage):
    __gtype_name__ = "StDungeonsChancesPage"
    row_random_weather_chance = cast(Adw.SpinRow, Gtk.Template.Child())
    row_max_mh_chance = cast(Adw.SpinRow, Gtk.Template.Child())
    row_max_hs_chance = cast(Adw.SpinRow, Gtk.Template.Child())
    row_max_ks_chance = cast(Adw.SpinRow, Gtk.Template.Child())
    row_max_sticky_chance = cast(Adw.SpinRow, Gtk.Template.Child())

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

        self.row_random_weather_chance.set_value(config["dungeons"]["random_weather_chance"].value)
        self.row_max_mh_chance.set_value(config["dungeons"]["max_mh_chance"].value)
        self.row_max_hs_chance.set_value(config["dungeons"]["max_hs_chance"].value)
        self.row_max_ks_chance.set_value(config["dungeons"]["max_ks_chance"].value)
        self.row_max_sticky_chance.set_value(config["dungeons"]["max_sticky_chance"].value)

        self._suppress_signals = False

    @Gtk.Template.Callback()
    def on_row_random_weather_chance_notify_value(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["random_weather_chance"].value = int(
            self.row_random_weather_chance.get_value()
        )

    @Gtk.Template.Callback()
    def on_row_max_mh_chance_notify_value(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["max_mh_chance"].value = int(self.row_max_mh_chance.get_value())

    @Gtk.Template.Callback()
    def on_row_max_hs_chance_notify_value(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["max_hs_chance"].value = int(self.row_max_hs_chance.get_value())

    @Gtk.Template.Callback()
    def on_row_max_ks_chance_notify_value(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["max_ks_chance"].value = int(self.row_max_ks_chance.get_value())

    @Gtk.Template.Callback()
    def on_row_max_sticky_chance_notify_value(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["max_sticky_chance"].value = int(self.row_max_sticky_chance.get_value())
