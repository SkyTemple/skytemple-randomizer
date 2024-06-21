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
from functools import partial
from threading import Thread
from typing import cast

from skytemple_files.common.i18n_util import _
from skytemple_files.common.util import get_binary_from_rom, open_utf8
from skytemple_files.hardcoded.dungeons import HardcodedDungeons

from skytemple_randomizer.config import RandomizerConfig, DungeonSettingsConfig
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, GLib, Gio

from skytemple_randomizer.string_provider import StringProvider, StringType

# This may seem silly, but we need to do it like this for gettext.
NOT_LOCALIZED_DUNGEON_ID = "ID"
NOT_LOCALIZED_DUNGEON_NAME = "Dungeon Name"
NOT_LOCALIZED_TITLE_UNLOCK_AT_START = "Unlock at Start"
TITLE_UNLOCK_AT_START = _("Unlock at Start")
NOT_LOCALIZED_TITLE_RANDOMIZE_IQ = "Randomize IQ"
TITLE_RANDOMIZE_IQ = _("Randomize IQ")
NOT_LOCALIZED_TITLE_RANDOMIZER_MONSTER_HOUSES = "Spawn Monster Houses"
TITLE_RANDOMIZER_MONSTER_HOUSES = _("Spawn Monster Houses")
NOT_LOCALIZED_TITLE_RANDOMIZE_WEATHER = "Randomize Weather"
TITLE_RANDOMIZE_WEATHER = _("Randomize Weather")
NOT_LOCALIZED_TITLE_RANDOMIZE = "Randomize"
TITLE_RANDOMIZE = _("Randomize")


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_dungeons_individual_settings.ui"))
class DungeonsIndividualSettingsPage(Adw.PreferencesPage):
    __gtype_name__ = "StDungeonsIndividualSettingsPage"

    stack = cast(Gtk.Stack, Gtk.Template.Child())
    spinner = cast(Gtk.Spinner, Gtk.Template.Child())
    pool_list = cast(Gtk.ListBox, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    search_text: str
    rows: dict[int, Adw.ExpanderRow]
    rows__randomize: dict[int, Adw.SwitchRow]
    rows__randomize_weather: dict[int, Adw.SwitchRow]
    rows__monster_houses: dict[int, Adw.SwitchRow]
    rows__randomize_iq: dict[int, Adw.SwitchRow]
    rows__unlock: dict[int, Adw.SwitchRow]
    _suppress_signals: bool

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.randomization_settings = None
        self.search_text = ""
        self.rows = {}
        self.rows__randomize = {}
        self.rows__randomize_weather = {}
        self.rows__monster_houses = {}
        self.rows__randomize_iq = {}
        self.rows__unlock = {}
        self._suppress_signals = False

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config

        frontend = GtkFrontend.instance()
        rom = frontend.input_rom
        static_data = frontend.input_rom_static_data

        dungeons: dict[int, tuple[DungeonSettingsConfig, str, str]] = {}
        configs = config["dungeons"]["settings"]

        def load_thread():
            string_provider = StringProvider(rom, frontend.input_rom_static_data)

            dungeon_list = HardcodedDungeons.get_dungeon_list(
                get_binary_from_rom(rom, static_data.bin_sections.arm9),
                static_data,
            )

            for i, dungeon in enumerate(dungeon_list):
                dungeons[i] = (
                    self._get_or_default(configs, i),
                    string_provider.get_value(StringType.DUNGEON_NAMES_MAIN, i),
                    string_provider.get_value(StringType.DUNGEON_NAMES_SELECTION, i),
                )

            GLib.idle_add(finish_load)

        def finish_load():
            for i, (config, name1, name2) in dungeons.items():
                row = self._make_row(i, config, name1, name2)
                self.pool_list.append(row)
            self._suppress_signals = False
            self.stack.set_visible_child(self.pool_list)

        self.pool_list.set_filter_func(self.pool_filter)

        Thread(target=load_thread).start()

    def on_search_changed(self, search_entry: Gtk.SearchEntry):
        if self._suppress_signals:
            return
        self.search_text = search_entry.get_text().strip().lower()
        self.pool_list.invalidate_filter()

    def help_pool(self, *args) -> str:
        return _(
            "Here you can decide which dungeons you want to have affected by the randomization and whether or "
            "randomize weather or not.\nYou can also disable Monster Houses for dungeons (recommended for early "
            "game). Additionally you can force dungeons to be unlocked.\nPlease note that entering story dungeons "
            "prematurely can mess with the game's story progression."
        )

    def pool_filter(self, row: Adw.SwitchRow):
        if self.search_text == "":
            match = True
        else:
            match = self.search_text in f"{row.get_title()} {row.get_subtitle()}".lower()
        return match

    @staticmethod
    def _get_or_default(configs: dict[int, DungeonSettingsConfig], i: int) -> DungeonSettingsConfig:
        if i not in configs:
            configs[i] = {
                "randomize": False,
                "unlock": False,
                "randomize_weather": False,
                "monster_houses": False,
                "enemy_iq": False,
            }
        return configs[i]

    def on_row_randomize_notify_active(self, idx: int, switch_row: Adw.SwitchRow, *args):
        if self.randomization_settings is None or self._suppress_signals:
            return
        self.randomization_settings["dungeons"]["settings"][idx]["randomize"] = switch_row.get_active()

    def on_row_randomize_weather_notify_active(self, idx: int, switch_row: Adw.SwitchRow, *args):
        if self.randomization_settings is None or self._suppress_signals:
            return
        self.randomization_settings["dungeons"]["settings"][idx]["randomize_weather"] = switch_row.get_active()

    def on_row_monster_houses_notify_active(self, idx: int, switch_row: Adw.SwitchRow, *args):
        if self.randomization_settings is None or self._suppress_signals:
            return
        self.randomization_settings["dungeons"]["settings"][idx]["monster_houses"] = switch_row.get_active()

    def on_row_enemy_iq_notify_active(self, idx: int, switch_row: Adw.SwitchRow, *args):
        if self.randomization_settings is None or self._suppress_signals:
            return
        self.randomization_settings["dungeons"]["settings"][idx]["enemy_iq"] = switch_row.get_active()

    def on_row_unlock_notify_active(self, idx: int, switch_row: Adw.SwitchRow, *args):
        if self.randomization_settings is None or self._suppress_signals:
            return
        self.randomization_settings["dungeons"]["settings"][idx]["unlock"] = switch_row.get_active()

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
                csv_reader = csv.DictReader(csv_file)
                for row_id, setting in enumerate(csv_reader):
                    if NOT_LOCALIZED_DUNGEON_ID not in setting:
                        raise ValueError(_("Missing dungeon ID in CSV"))
                    idx = int(setting[NOT_LOCALIZED_DUNGEON_ID])
                    assert self.randomization_settings is not None
                    self.randomization_settings["dungeons"]["settings"][idx] = {
                        "randomize": bool(int(setting[NOT_LOCALIZED_TITLE_RANDOMIZE])),
                        "unlock": bool(int(setting[NOT_LOCALIZED_TITLE_UNLOCK_AT_START])),
                        "randomize_weather": bool(int(setting[NOT_LOCALIZED_TITLE_RANDOMIZE_WEATHER])),
                        "monster_houses": bool(int(setting[NOT_LOCALIZED_TITLE_RANDOMIZER_MONSTER_HOUSES])),
                        "enemy_iq": bool(int(setting[NOT_LOCALIZED_TITLE_RANDOMIZE_IQ])),
                    }
                    new_current = self.randomization_settings["dungeons"]["settings"][idx]
                    self._suppress_signals = True
                    self.rows__randomize[idx].set_active(new_current["randomize"])
                    self.rows__unlock[idx].set_active(new_current["unlock"])
                    self.rows__randomize_weather[idx].set_active(new_current["randomize_weather"])
                    self.rows__monster_houses[idx].set_active(new_current["monster_houses"])
                    self.rows__randomize_iq[idx].set_active(new_current["enemy_iq"])
                    self._suppress_signals = False

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
                initial_name="dungon_settings.csv",
            )
        else:
            dialog_for_file = Gtk.FileDialog(default_filter=csv_filter, initial_name="dungon_settings.csv")
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

        string_provider = StringProvider(frontend.input_rom, frontend.input_rom_static_data)

        try:
            with open_utf8(path, "w", newline="") as result_file:
                wr = csv.DictWriter(
                    result_file,
                    fieldnames=[
                        NOT_LOCALIZED_DUNGEON_ID,
                        NOT_LOCALIZED_DUNGEON_NAME,
                        NOT_LOCALIZED_TITLE_RANDOMIZE,
                        NOT_LOCALIZED_TITLE_RANDOMIZE_WEATHER,
                        NOT_LOCALIZED_TITLE_RANDOMIZER_MONSTER_HOUSES,
                        NOT_LOCALIZED_TITLE_RANDOMIZE_IQ,
                        NOT_LOCALIZED_TITLE_UNLOCK_AT_START,
                    ],
                )
                assert self.randomization_settings is not None
                wr.writeheader()
                current = self.randomization_settings["dungeons"]["settings"]
                for idx, settings in current.items():
                    wr.writerow(
                        {
                            NOT_LOCALIZED_DUNGEON_ID: str(idx),
                            NOT_LOCALIZED_DUNGEON_NAME: string_provider.get_value(StringType.DUNGEON_NAMES_MAIN, idx),
                            NOT_LOCALIZED_TITLE_RANDOMIZE: ("1" if settings["randomize"] else "0"),
                            NOT_LOCALIZED_TITLE_RANDOMIZE_WEATHER: ("1" if settings["randomize_weather"] else "0"),
                            NOT_LOCALIZED_TITLE_RANDOMIZER_MONSTER_HOUSES: ("1" if settings["monster_houses"] else "0"),
                            NOT_LOCALIZED_TITLE_RANDOMIZE_IQ: ("1" if settings["enemy_iq"] else "0"),
                            NOT_LOCALIZED_TITLE_UNLOCK_AT_START: ("1" if settings["unlock"] else "0"),
                        }
                    )
        except Exception as e:
            GtkFrontend.instance().display_error(
                _("Failed to export. Details: {}").format(e),
                cast(Gtk.Window, self.get_root()),
            )

    def create_window_end_buttons(self) -> Gtk.Widget:
        box = Gtk.Box(spacing=5)
        button_import = Gtk.Button(icon_name="skytemple-import-symbolic", tooltip_text=_("Import from CSV"))
        button_import.connect("clicked", self.on_button_import_clicked)
        button_export = Gtk.Button(icon_name="skytemple-export-symbolic", tooltip_text=_("Export to CSV"))
        button_export.connect("clicked", self.on_button_export_clicked)
        box.append(button_import)
        box.append(button_export)
        return box

    def _make_row(self, i: int, config: DungeonSettingsConfig, name1: str, name2: str):
        row = Adw.ExpanderRow(title=name1, subtitle=f"{name2} #{i:03}")

        row_randomize = Adw.SwitchRow(title=TITLE_RANDOMIZE, active=config["randomize"])
        row_randomize.connect("notify::active", partial(self.on_row_randomize_notify_active, i))
        row.add_row(row_randomize)

        row_randomize_weather = Adw.SwitchRow(title=TITLE_RANDOMIZE_WEATHER, active=config["randomize_weather"])
        row_randomize_weather.connect("notify::active", partial(self.on_row_randomize_weather_notify_active, i))
        row.add_row(row_randomize_weather)

        row_monster_houses = Adw.SwitchRow(title=TITLE_RANDOMIZER_MONSTER_HOUSES, active=config["monster_houses"])
        row_monster_houses.connect("notify::active", partial(self.on_row_monster_houses_notify_active, i))
        row.add_row(row_monster_houses)

        row_enemy_iq = Adw.SwitchRow(title=TITLE_RANDOMIZE_IQ, active=config["enemy_iq"])
        row_enemy_iq.connect("notify::active", partial(self.on_row_enemy_iq_notify_active, i))
        row.add_row(row_enemy_iq)

        row_unlock = Adw.SwitchRow(title=TITLE_UNLOCK_AT_START, active=config["unlock"])
        row_unlock.connect("notify::active", partial(self.on_row_unlock_notify_active, i))
        row.add_row(row_unlock)

        self.rows__randomize[i] = row_randomize
        self.rows__randomize_weather[i] = row_randomize_weather
        self.rows__monster_houses[i] = row_monster_houses
        self.rows__randomize_iq[i] = row_enemy_iq
        self.rows__unlock[i] = row_unlock
        self.rows[i] = row
        return row
