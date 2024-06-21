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
from enum import Enum, auto
from functools import partial
from threading import Thread
from typing import cast

from range_typed_integers import u16
from skytemple_files.common.i18n_util import _
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import MONSTER_MD
from skytemple_files.patch.patches import Patcher

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, GLib

from skytemple_randomizer.frontend.gtk.widgets import RandomizationSettingsWidget
from skytemple_randomizer.lists import DEFAULTMONSTERPOOL
from skytemple_randomizer.string_provider import StringProvider, StringType


class MonstersPoolType(Enum):
    ALL = auto()
    STARTERS = auto()


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_monsters_pool.ui"))
class MonstersPoolPage(Adw.PreferencesPage):
    __gtype_name__ = "StMonstersPoolPage"

    stack = cast(Gtk.Stack, Gtk.Template.Child())
    spinner = cast(Gtk.Spinner, Gtk.Template.Child())
    pool_list = cast(Gtk.ListBox, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    parent_page: RandomizationSettingsWidget
    pool_type: MonstersPoolType
    search_text: str
    rows: dict[u16, Adw.SwitchRow]
    _suppress_signals: bool

    def __init__(
        self,
        *args,
        type: MonstersPoolType,
        parent_page: RandomizationSettingsWidget,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parent_page = parent_page
        self.pool_type = type
        self.randomization_settings = None
        self.search_text = ""
        self.rows = {}
        self._suppress_signals = False

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config

        frontend = GtkFrontend.instance()
        rom = frontend.input_rom

        monster_bases: dict[u16, tuple[bool, str]] = {}

        def load_thread():
            string_provider = StringProvider(rom, frontend.input_rom_static_data)
            patcher = Patcher(rom, frontend.input_rom_static_data)

            b_attr = "md_index_base"
            if is_applied(patcher, "ExpandPokeList"):
                b_attr = "entid"

            monster_md = FileType.MD.deserialize(rom.getFileByName(MONSTER_MD))

            for entry in monster_md.entries:
                baseid = getattr(entry, b_attr)
                monster_bases[baseid] = (
                    baseid in self.pool(),
                    string_provider.get_value(StringType.POKEMON_NAMES, baseid),
                )

            GLib.idle_add(finish_load)

        def finish_load():
            for baseid, (activated, name) in monster_bases.items():
                row = Adw.SwitchRow(title=name, subtitle=f"#{baseid:03}", active=activated)
                self.pool_list.append(row)
                self.rows[baseid] = row
                row.connect("notify::active", partial(self.on_row_notify_active, baseid))
            self.stack.set_visible_child(self.pool_list)

        self.pool_list.set_filter_func(self.pool_filter)
        self._suppress_signals = False

        Thread(target=load_thread).start()

    def get_enabled(self) -> bool:
        assert self.randomization_settings is not None
        if self.pool_type == MonstersPoolType.STARTERS:
            return self.randomization_settings["starters_npcs"]["starters"]
        return False

    def set_enabled(self, state: bool):
        assert self.randomization_settings is not None
        if self.pool_type == MonstersPoolType.STARTERS:
            self.randomization_settings["starters_npcs"]["starters"] = state
            if self.parent_page:
                self.parent_page.populate_settings(self.randomization_settings)

    def pool(self) -> list[u16]:
        assert self.randomization_settings is not None
        if self.pool_type == MonstersPoolType.STARTERS:
            return self.randomization_settings["pokemon"]["starters_enabled"]
        else:
            return self.randomization_settings["pokemon"]["monsters_enabled"]

    def set_pool(self, value: list[u16]):
        assert self.randomization_settings is not None
        if self.pool_type == MonstersPoolType.STARTERS:
            self.randomization_settings["pokemon"]["starters_enabled"] = value
        else:
            self.randomization_settings["pokemon"]["monsters_enabled"] = value

    def on_row_notify_active(self, idx: int, switch_row: Adw.SwitchRow, *args):
        if self._suppress_signals:
            return
        v = u16(idx)
        pool = self.pool()
        if switch_row.get_active():
            if v not in pool:
                pool.append(v)
        else:
            pool.remove(v)

    def on_search_changed(self, search_entry: Gtk.SearchEntry):
        if self._suppress_signals:
            return
        self.search_text = search_entry.get_text().strip().lower()
        self.pool_list.invalidate_filter()

    def on_button_reset_clicked(self, *args):
        self._suppress_signals = True
        assert self.randomization_settings is not None
        self.set_pool(cast(list[u16], list(DEFAULTMONSTERPOOL)))
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

    def on_button_copy_clicked(self, *args):
        self._suppress_signals = True
        assert self.randomization_settings is not None
        if self.pool_type == MonstersPoolType.STARTERS:
            other_pool = self.randomization_settings["pokemon"]["monsters_enabled"]
        else:
            other_pool = self.randomization_settings["pokemon"]["starters_enabled"]
        self.set_pool(list(other_pool))
        pool = self.pool()
        for baseid, row in self.rows.items():
            row.set_active(baseid in pool)
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
        if self.pool_type == MonstersPoolType.STARTERS:
            copy_text = _('Copy from "Allowed Pokémon"')
        else:
            copy_text = _("Copy from Starters")
        button_copy = Gtk.Button(icon_name="skytemple-import-symbolic", tooltip_text=copy_text)
        button_copy.connect("clicked", self.on_button_copy_clicked)
        box.append(button_reset)
        box.append(button_none)
        box.append(button_copy)
        return box

    def help_pool_all(self, *args) -> str:
        return _("Only the Pokémon selected will be used for any randomization option.")

    def help_pool_starters(self, *args) -> str:
        return _(
            'Only the Pokémon selected can appear as random starter options.\nThey also need to be in the list of "Allowed Pokémon".'
        )

    def pool_filter(self, row: Adw.SwitchRow):
        if self.search_text == "":
            match = True
        else:
            match = self.search_text in f"{row.get_title()} {row.get_subtitle()}".lower()
        return match


def is_applied(patcher: Patcher, patch: str) -> bool:
    try:
        return patcher.is_applied(patch)
    except NotImplementedError:
        return False
