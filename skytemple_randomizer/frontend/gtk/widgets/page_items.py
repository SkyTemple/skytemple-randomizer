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
from skytemple_files.common.types.file_types import FileType

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, GLib

from skytemple_randomizer.frontend.gtk.widgets import RandomizationSettingsWidget
from skytemple_randomizer.lists import DEFAULTITEMPOOL
from skytemple_randomizer.string_provider import StringProvider, StringType

ITEM_FILE = "BALANCE/item_p.bin"


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_items.ui"))
class ItemsPage(Adw.PreferencesPage):
    __gtype_name__ = "StItemsPage"

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

        items: dict[int, tuple[bool, str]] = {}

        def load_thread():
            string_provider = StringProvider(rom, frontend.input_rom_static_data)

            item_p = FileType.ITEM_P.deserialize(rom.getFileByName(ITEM_FILE))

            for i, entry in enumerate(item_p.item_list):
                items[i] = (
                    i in self.pool(),
                    string_provider.get_value(StringType.ITEM_NAMES, i),
                )

            GLib.idle_add(finish_load)

        def finish_load():
            for idx, (activated, name) in items.items():
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
        return self.randomization_settings["dungeons"]["items_enabled"]

    def set_pool(self, value: list[int]):
        assert self.randomization_settings is not None
        self.randomization_settings["dungeons"]["items_enabled"] = value

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
        self.set_pool(list(DEFAULTITEMPOOL))
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

    def help_pool(self, *args) -> str:
        return _("Only these items will spawn on dungeon floors.")

    def pool_filter(self, row: Adw.SwitchRow):
        if self.search_text == "":
            match = True
        else:
            match = self.search_text in f"{row.get_title()} {row.get_subtitle()}".lower()
        return match
