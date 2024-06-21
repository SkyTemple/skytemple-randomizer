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

import csv
import os
from enum import Enum, auto
from functools import partial
from typing import cast, Sequence

from skytemple_files.common.i18n_util import _
from skytemple_files.common.util import open_utf8

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.hacks import force_adw_entry_row_no_title
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, GLib, Gio

from skytemple_randomizer.frontend.gtk.widgets import RandomizationSettingsWidget


class TextPool(Enum):
    CHAPTER_TITLES = auto()
    LOCATIONS_A = auto()
    LOCATIONS_B = auto()
    BLIND_ITEM_NAMES = auto()
    BLIND_MOVE_NAMES = auto()

    def csv_name(self):
        if self == TextPool.CHAPTER_TITLES:
            return "chapter_titles.csv"
        if self == TextPool.LOCATIONS_A:
            return "location_part1.csv"
        if self == TextPool.LOCATIONS_B:
            return "location_part2.csv"
        if self == TextPool.BLIND_ITEM_NAMES:
            return "blind_items.csv"
        if self == TextPool.BLIND_MOVE_NAMES:
            return "blind_moves.csv"
        raise KeyError(self)


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_text_pool.ui"))
class TextPoolPage(Adw.PreferencesPage):
    __gtype_name__ = "StTextPoolPage"
    pool_list = cast(Gtk.ListBox, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    parent_page: RandomizationSettingsWidget
    pool: TextPool
    _suppress_signals: bool

    def __init__(self, *args, pool: TextPool, parent_page: RandomizationSettingsWidget, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_page = parent_page
        self.pool = pool
        self.randomization_settings = None
        self._suppress_signals = False

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config

        self.reload()

        self._suppress_signals = False

    def reload(self):
        self.pool_list.remove_all()
        for text in self.get_pool():
            self.pool_list.append(self._make_entry(text))

    @Gtk.Template.Callback()
    def on_button_add_text_clicked(self, *args):
        self.add_to_pool("")
        self.pool_list.append(self._make_entry(""))

    def on_button_remove_text_clicked(self, text: Adw.EntryRow, *args):
        index = text.get_index()
        self.remove_from_pool(index)
        self.pool_list.remove(text)

    def on_text_changed(self, text: Adw.EntryRow, *args):
        self.update_in_pool(text.get_index(), text.get_text())

    def _make_entry(self, value: str) -> Adw.EntryRow:
        row_text = Adw.EntryRow()
        force_adw_entry_row_no_title(row_text)
        row_text.set_text(value)
        row_text.connect("changed", self.on_text_changed)

        remove_button = Gtk.Button(icon_name="skytemple-list-remove-symbolic", tooltip_text=_("Remove Text"))
        remove_button.add_css_class("flat")
        remove_button.connect("clicked", partial(self.on_button_remove_text_clicked, row_text))

        row_text.add_suffix(remove_button)
        return row_text

    def get_enabled(self) -> bool:
        assert self.randomization_settings is not None
        if self.pool == TextPool.CHAPTER_TITLES:
            return self.randomization_settings["chapters"]["randomize"]
        elif self.pool == TextPool.LOCATIONS_A or self.pool == TextPool.LOCATIONS_B:
            return self.randomization_settings["locations"]["randomize"]
        elif self.pool == TextPool.BLIND_MOVE_NAMES:
            return self.randomization_settings["pokemon"]["blind_moves"]["enable"]
        elif self.pool == TextPool.BLIND_ITEM_NAMES:
            return self.randomization_settings["item"]["blind_items"]["enable"]
        else:
            raise KeyError(self.pool)

    def set_enabled(self, state: bool):
        assert self.randomization_settings is not None
        if self.pool == TextPool.CHAPTER_TITLES:
            self.randomization_settings["chapters"]["randomize"] = state
        elif self.pool == TextPool.LOCATIONS_A or self.pool == TextPool.LOCATIONS_B:
            self.randomization_settings["locations"]["randomize"] = state
        elif self.pool == TextPool.BLIND_MOVE_NAMES:
            self.randomization_settings["pokemon"]["blind_moves"]["enable"] = state
        elif self.pool == TextPool.BLIND_ITEM_NAMES:
            self.randomization_settings["item"]["blind_items"]["enable"] = state
        else:
            raise KeyError(self.pool)
        if self.parent_page:
            self.parent_page.populate_settings(self.randomization_settings)

    def on_button_import_clicked(self, *args):
        frontend = GtkFrontend.instance()
        csv_filter = Gtk.FileFilter()
        csv_filter.add_suffix("csv")
        csv_filter.add_mime_type("text/csv")
        documents_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if documents_dir is not None:
            default_dir = Gio.File.new_for_path(documents_dir)
            dialog_for_file = Gtk.FileDialog(initial_folder=default_dir, default_filter=csv_filter)

        else:
            dialog_for_file = Gtk.FileDialog(default_filter=csv_filter)
        dialog_for_file.open(frontend.window, None, self.on_import_file_loaded)

    def on_import_file_loaded(self, dialog, result):
        try:
            file: Gio.File = dialog.open_finish(result)
        except Exception as e:
            if not isinstance(e, GLib.GError) or "dismissed" not in str(e).lower():
                GtkFrontend.instance().display_error(
                    _("Failed to import: Error while opening file ({}).").format(e),
                    cast(Gtk.Window, self.get_root()),
                )
            return

        path = file.get_path()
        assert path is not None

        try:
            with open_utf8(path) as csv_file:
                csv_reader = csv.reader(csv_file)
                questions = [q[0] for q in csv_reader]
                self.set_pool(questions)
                self.reload()

        except Exception as e:
            GtkFrontend.instance().display_error(
                _(
                    "Failed to import. Make sure your CSV matches the same format as with the export button. Details: {}"
                ).format(e),
                cast(Gtk.Window, self.get_root()),
            )

    def on_button_export_clicked(self, *args):
        frontend = GtkFrontend.instance()
        csv_filter = Gtk.FileFilter()
        csv_filter.add_suffix("csv")
        csv_filter.add_mime_type("text/csv")
        documents_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if documents_dir is not None:
            default_dir = Gio.File.new_for_path(documents_dir)
            dialog_for_file = Gtk.FileDialog(
                initial_folder=default_dir,
                default_filter=csv_filter,
                initial_name=self.pool.csv_name(),
            )
        else:
            dialog_for_file = Gtk.FileDialog(default_filter=csv_filter, initial_name=self.pool.csv_name())
        dialog_for_file.save(frontend.window, None, self.on_export_file_saved)

    def on_export_file_saved(self, dialog, result):
        frontend = GtkFrontend.instance()
        try:
            file = dialog.save_finish(result)
        except Exception as e:
            if not isinstance(e, GLib.GError) or "dismissed" not in str(e).lower():
                frontend.display_error(
                    _("Failed to export: Error while opening file ({}).").format(e),
                    cast(Gtk.Window, self.get_root()),
                )
            return

        path = file.get_path()
        assert path is not None

        try:
            with open_utf8(path, "w", newline="") as result_file:
                wr = csv.writer(
                    result_file,
                )
                wr.writerows(((x,) for x in self.get_pool()))
        except Exception as e:
            GtkFrontend.instance().display_error(
                _("Failed to export. Details: {}").format(e),
                cast(Gtk.Window, self.get_root()),
            )

    @staticmethod
    def raw_create_window_end_buttons() -> tuple[Gtk.Button, Gtk.Button, Gtk.Widget]:
        box = Gtk.Box(spacing=5)
        button_import = Gtk.Button(
            icon_name="skytemple-import-symbolic",
            tooltip_text=_("Import from CSV"),
        )
        button_export = Gtk.Button(
            icon_name="skytemple-export-symbolic",
            tooltip_text=_("Export to CSV"),
        )
        box.append(button_import)
        box.append(button_export)
        return button_import, button_export, box

    def create_window_end_buttons(self) -> Gtk.Widget:
        button_import, button_export, w = self.raw_create_window_end_buttons()
        button_import.connect("clicked", self.on_button_import_clicked)
        button_export.connect("clicked", self.on_button_export_clicked)
        return w

    def get_pool(self) -> Sequence[str]:
        assert self.randomization_settings is not None
        if self.pool == TextPool.CHAPTER_TITLES:
            return self.randomization_settings["chapters"]["text"].split("\n")
        elif self.pool == TextPool.LOCATIONS_A:
            return self.randomization_settings["locations"]["first"].split("\n")
        elif self.pool == TextPool.LOCATIONS_B:
            return self.randomization_settings["locations"]["second"].split("\n")
        elif self.pool == TextPool.BLIND_MOVE_NAMES:
            return self.randomization_settings["pokemon"]["blind_moves"]["names"].split("\n")
        elif self.pool == TextPool.BLIND_ITEM_NAMES:
            return self.randomization_settings["item"]["blind_items"]["names"].split("\n")
        else:
            raise KeyError(self.pool)

    def set_pool(self, pool: list[str]):
        assert self.randomization_settings is not None
        if self.pool == TextPool.CHAPTER_TITLES:
            self.randomization_settings["chapters"]["text"] = "\n".join(pool)
        elif self.pool == TextPool.LOCATIONS_A:
            self.randomization_settings["locations"]["first"] = "\n".join(pool)
        elif self.pool == TextPool.LOCATIONS_B:
            self.randomization_settings["locations"]["second"] = "\n".join(pool)
        elif self.pool == TextPool.BLIND_MOVE_NAMES:
            self.randomization_settings["pokemon"]["blind_moves"]["names"] = "\n".join(pool)
        elif self.pool == TextPool.BLIND_ITEM_NAMES:
            self.randomization_settings["item"]["blind_items"]["names"] = "\n".join(pool)
        else:
            raise KeyError(self.pool)

    def add_to_pool(self, line: str):
        pool = list(self.get_pool())
        pool.append(line)
        self.set_pool(pool)

    def update_in_pool(self, i: int, line: str):
        pool = list(self.get_pool())
        pool[i] = line
        self.set_pool(pool)

    def remove_from_pool(self, i: int):
        pool = list(self.get_pool())
        del pool[i]
        self.set_pool(pool)
