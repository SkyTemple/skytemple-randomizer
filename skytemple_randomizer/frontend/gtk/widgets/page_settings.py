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

import json
import os
from typing import Callable, cast

from skytemple_files.common.i18n_util import _

from skytemple_randomizer.config import (
    RandomizerConfig,
    ConfigFileLoader,
    EnumJsonEncoder,
    deep_typeddict_to_dict,
)
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, GLib, Gio


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_settings.ui"))
class SettingsPage(Adw.Bin):
    __gtype_name__ = "StSettingsPage"

    toast_overlay = cast(Adw.ToastOverlay, Gtk.Template.Child())
    row_seed = cast(Adw.EntryRow, Gtk.Template.Child())
    row_native_file_handlers = cast(Adw.SwitchRow, Gtk.Template.Child())

    repopulate_randomization_settings: Callable[[], None]
    randomization_settings: RandomizerConfig | None

    def __init__(
        self,
        *args,
        repopulate_randomization_settings: Callable[[], None],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.randomization_settings = None
        self.repopulate_randomization_settings = repopulate_randomization_settings
        self._suppress_signals = False

    @Gtk.Template.Callback()
    def on_row_seed_changed(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["seed"] = self.row_seed.get_text()

    @Gtk.Template.Callback()
    def on_row_native_file_handlers_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["starters_npcs"]["native_file_handlers"] = (
            self.row_native_file_handlers.get_active()
        )

    @Gtk.Template.Callback()
    def on_button_load_clicked(self, *args):
        frontend = GtkFrontend.instance()
        json_filter = Gtk.FileFilter()
        json_filter.add_suffix("json")
        json_filter.add_mime_type("application/json")
        documents_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if documents_dir is not None:
            default_dir = Gio.File.new_for_path(documents_dir)
            dialog_for_file = Gtk.FileDialog(initial_folder=default_dir, default_filter=json_filter)
        else:
            dialog_for_file = Gtk.FileDialog(default_filter=json_filter)
        dialog_for_file.open(frontend.window, None, self.on_file_loaded)

    def on_file_loaded(self, dialog, result):
        try:
            file: Gio.File = dialog.open_finish(result)
        except Exception as e:
            if not isinstance(e, GLib.GError) or "dismissed" not in str(e).lower():
                GtkFrontend.instance().display_error(
                    _("Failed to load settings: Error while opening file ({}).").format(e),
                    cast(Gtk.Window, self.get_root()),
                )
            return
        path = file.get_path()
        assert path is not None
        frontend = GtkFrontend.instance()
        try:
            frontend.randomization_settings = ConfigFileLoader.load(path)
        except Exception as e:
            frontend.display_error(
                _("The config file you tried to import is invalid:\n{}:\n{}").format(e.__class__.__name__, e),
                cast(Gtk.Window, self.get_root()),
            )
            return
        self.populate_settings(frontend.randomization_settings)
        self.repopulate_randomization_settings()
        toast = Adw.Toast(
            title=_("Settings loaded!"),
            timeout=3,
        )
        self.toast_overlay.add_toast(toast)

    @Gtk.Template.Callback()
    def on_button_save_clicked(self, *args):
        frontend = GtkFrontend.instance()
        json_filter = Gtk.FileFilter()
        json_filter.add_suffix("json")
        json_filter.add_mime_type("application/json")
        documents_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if documents_dir is not None:
            default_dir = Gio.File.new_for_path(documents_dir)
            dialog_for_file = Gtk.FileDialog(
                initial_folder=default_dir,
                default_filter=json_filter,
                initial_name="settings.json",
            )
        else:
            dialog_for_file = Gtk.FileDialog(default_filter=json_filter, initial_name="settings.json")
        dialog_for_file.save(frontend.window, None, self.do_save)

    def do_save(self, dialog, result):
        try:
            file = dialog.save_finish(result)
        except Exception as e:
            if not isinstance(e, GLib.GError) or "dismissed" not in str(e).lower():
                GtkFrontend.instance().display_error(
                    _("Failed to save settings: Error while opening file ({}).").format(e),
                    cast(Gtk.Window, self.get_root()),
                )
            return
        if not file.get_path().lower().endswith(".json"):
            GtkFrontend.instance().display_error(
                _("The path of the settings file needs to end in '.json'."),
                cast(Gtk.Window, self.get_root()),
            )
            return
        contents = json.dumps(
            deep_typeddict_to_dict(self.randomization_settings),
            indent=4,
            cls=EnumJsonEncoder,
            ensure_ascii=False,
        ).encode("utf-8")
        file.replace_contents_async(
            contents,
            etag=None,
            make_backup=False,
            flags=Gio.FileCreateFlags.NONE,
            cancellable=None,
            callback=self.after_save,
        )

    def after_save(self, file, result):
        file.replace_contents_finish(result)
        toast = Adw.Toast(
            title=_("Settings saved!"),
            timeout=3,
        )
        self.toast_overlay.add_toast(toast)

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.row_seed.set_text(config["seed"])
        self.row_native_file_handlers.set_active(config["starters_npcs"]["native_file_handlers"])
        self.randomization_settings = config
        self._suppress_signals = False
