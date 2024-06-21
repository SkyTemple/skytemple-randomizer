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
from threading import Thread
from typing import cast

from skytemple_files.common.i18n_util import _
from skytemple_files.data.md.protocol import Ability

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, GLib

from skytemple_randomizer.frontend.gtk.widgets import RandomizationSettingsWidget
from skytemple_randomizer.lists import DEFAULTABILITYPOOL
from skytemple_randomizer.string_provider import StringProvider, StringType


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_monsters_abilities.ui"))
class MonstersAbilitiesPage(Adw.PreferencesPage):
    __gtype_name__ = "StMonstersAbilitiesPage"

    stack = cast(Gtk.Stack, Gtk.Template.Child())
    spinner = cast(Gtk.Spinner, Gtk.Template.Child())
    pool_list = cast(Gtk.ListBox, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    parent_page: RandomizationSettingsWidget
    search_text: str
    rows: dict[int, Adw.SwitchRow]
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
        rom = frontend.input_rom

        abilities: dict[int, tuple[bool, str]] = {}

        def load_thread():
            string_provider = StringProvider(rom, frontend.input_rom_static_data)

            for ability in Ability:
                name = _("Unused") + f" 0x{ability.value:0x}"
                if ability.value < 124:
                    name = string_provider.get_value(StringType.ABILITY_NAMES, ability.value)
                abilities[ability.value] = (
                    ability.value in self.pool(),
                    name,
                )

            GLib.idle_add(finish_load)

        def finish_load():
            for idx, (activated, name) in abilities.items():
                row = Adw.SwitchRow(title=name, subtitle=f"#{idx:03}", active=activated)
                self.pool_list.append(row)
                self.rows[idx] = row
                row.connect("notify::active", partial(self.on_row_notify_active, idx))
            self.stack.set_visible_child(self.pool_list)

        self.pool_list.set_filter_func(self.pool_filter)
        self._suppress_signals = False

        Thread(target=load_thread).start()

    def pool(self) -> list[int]:
        assert self.randomization_settings is not None
        return self.randomization_settings["pokemon"]["abilities_enabled"]

    def set_pool(self, value: list[int]):
        assert self.randomization_settings is not None
        self.randomization_settings["pokemon"]["abilities_enabled"] = value

    def on_row_notify_active(self, idx: int, switch_row: Adw.SwitchRow, *args):
        if self._suppress_signals:
            return
        pool = self.pool()
        if switch_row.get_active():
            if idx not in pool:
                pool.append(idx)
        else:
            pool.remove(idx)

    def on_search_changed(self, search_entry: Gtk.SearchEntry):
        if self._suppress_signals:
            return
        self.search_text = search_entry.get_text().strip().lower()
        self.pool_list.invalidate_filter()

    def on_button_reset_clicked(self, *args):
        self._suppress_signals = True
        assert self.randomization_settings is not None
        self.set_pool(cast(list[int], list(DEFAULTABILITYPOOL)))
        pool = self.pool()
        for baseid, row in self.rows.items():
            row.set_active(baseid in pool)
        self._suppress_signals = False

    def on_button_none_clicked(self, *args):
        self._suppress_signals = True
        for row in self.rows.values():
            row.set_active(False)
        self.pool().clear()
        self._suppress_signals = False

    def create_window_end_buttons(self) -> Gtk.Widget:
        box = Gtk.Box(spacing=5)
        button_reset = Gtk.Button(
            icon_name="skytemple-view-refresh-symbolic",
            tooltip_text=_("Reset to Default"),
        )
        button_reset.connect("clicked", self.on_button_reset_clicked)
        button_none = Gtk.Button(icon_name="skytemple-edit-delete-symbolic", tooltip_text=_("Select None"))
        button_none.connect("clicked", self.on_button_none_clicked)
        box.append(button_reset)
        box.append(button_none)
        return box

    def pool_filter(self, row: Adw.SwitchRow):
        if self.search_text == "":
            match = True
        else:
            match = self.search_text in f"{row.get_title()} {row.get_subtitle()}".lower()
        return match

    def get_enabled(self) -> bool:
        assert self.randomization_settings is not None
        return self.randomization_settings["pokemon"]["abilities"]

    def set_enabled(self, state: bool):
        assert self.randomization_settings is not None
        self.randomization_settings["pokemon"]["abilities"] = state
        if self.parent_page:
            self.parent_page.populate_settings(self.randomization_settings)
