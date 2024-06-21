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
from functools import partial
from numbers import Number
from threading import Thread
from typing import cast

from skytemple_files.common.i18n_util import _

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, GLib

from skytemple_randomizer.frontend.gtk.widgets import RandomizationSettingsWidget
from skytemple_randomizer.lists import DEFAULITEMCATWEIGHTPOOL


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_items_categories.ui"))
class ItemsCategoriesPage(Adw.PreferencesPage):
    __gtype_name__ = "StItemsCategoriesPage"

    stack = cast(Gtk.Stack, Gtk.Template.Child())
    spinner = cast(Gtk.Spinner, Gtk.Template.Child())
    pool_list = cast(Gtk.ListBox, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    parent_page: RandomizationSettingsWidget
    search_text: str
    rows: dict[int, Adw.SpinRow]
    _suppress_signals: bool

    def __init__(
        self,
        *args,
        parent_page: RandomizationSettingsWidget,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parent_page = parent_page
        self.randomization_settings = None
        self.search_text = ""
        self.rows = {}
        self._suppress_signals = False

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config

        frontend = GtkFrontend.instance()
        static_data = frontend.input_rom_static_data

        cats: dict[int, tuple[Number, str]] = {}

        def load_thread():
            for i, entry in static_data.dungeon_data.item_categories.items():
                # Skip irrelevant
                if i in [7, 11, 12, 13, 14, 15]:
                    continue
                val = config["item"]["weights"][i] if i in config["item"]["weights"] else 0
                cats[i] = (
                    cast(Number, val),
                    entry.name_localized,
                )

            GLib.idle_add(finish_load)

        def finish_load():
            for idx, (value, name) in cats.items():
                row = Adw.SpinRow(
                    title=name,
                    digits=1,
                    climb_rate=1,
                    adjustment=Gtk.Adjustment(lower=0, upper=1000, step_increment=0.1),
                    value=float(cast(float, value)),
                )
                row.add_css_class("skytemple-randomizer--progress")
                self.pool_list.append(row)
                self.rows[idx] = row
                row.connect("notify::value", partial(self.on_row_notify_value, idx))
            self.stack.set_visible_child(self.pool_list)

        self.pool_list.set_filter_func(self.pool_filter)
        self._suppress_signals = False

        Thread(target=load_thread).start()

    def on_row_notify_value(self, idx: int, row: Adw.SpinRow, *args):
        if self.randomization_settings is None or self._suppress_signals:
            return
        self.randomization_settings["item"]["weights"][idx] = cast(Number, row.get_value())

    def on_search_changed(self, search_entry: Gtk.SearchEntry):
        if self._suppress_signals:
            return
        self.search_text = search_entry.get_text().strip().lower()
        self.pool_list.invalidate_filter()

    def on_button_reset_clicked(self, *args):
        self._suppress_signals = True
        assert self.randomization_settings is not None
        self.randomization_settings["item"]["weights"] = cast(dict[int, Number], DEFAULITEMCATWEIGHTPOOL).copy()
        for i, row in self.rows.items():
            val = (
                self.randomization_settings["item"]["weights"][i]
                if i in self.randomization_settings["item"]["weights"]
                else 0
            )
            row.set_value(float(val))  # type: ignore
        self._suppress_signals = False

    def on_button_none_clicked(self, *args):
        self._suppress_signals = True
        assert self.randomization_settings is not None
        for row in self.rows.values():
            row.set_value(0)
        for key in self.randomization_settings["item"]["weights"].keys():
            self.randomization_settings["item"]["weights"][key] = cast(Number, 0)
        self._suppress_signals = False

    def help_pool(self, *args) -> str:
        return _(
            "Controls weight biases when randomizing items.\nA higher multiplier compared to other categories means that items from that category are more likely to spawn than others.\n\nThis only applies to the 'Balanced' item algorithm!"
        )

    def pool_filter(self, row: Adw.SwitchRow):
        if self.search_text == "":
            match = True
        else:
            match = self.search_text in f"{row.get_title()} {row.get_subtitle()}".lower()
        return match
