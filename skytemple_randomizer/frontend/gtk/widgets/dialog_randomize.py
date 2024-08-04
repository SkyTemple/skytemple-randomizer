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

import ctypes
import os
import random
import sys
import traceback
from functools import partial
from math import floor
from typing import cast

from ndspy.rom import NintendoDSRom
from skytemple_files.common.i18n_util import _
from skytemple_files.common.ppmdu_config.data import Pmd2Data

from skytemple_randomizer.config import RandomizerConfig, version, get_effective_seed
from skytemple_randomizer.data_dir import data_dir
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, Gio, GLib

from skytemple_randomizer.frontend.gtk.ui_util import open_dir
from skytemple_randomizer.randomizer_thread import RandomizerThread
from skytemple_randomizer.status import Status


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "dialog_randomize.ui"))
class RandomizeDialog(Adw.Dialog):
    __gtype_name__ = "StRandomizeDialog"

    header_bar = cast(Adw.HeaderBar, Gtk.Template.Child())
    content = cast(Adw.Bin, Gtk.Template.Child())
    status_stack = cast(Gtk.Stack, Gtk.Template.Child())
    status_start_page = cast(Gtk.StackPage, Gtk.Template.Child())
    start_button = cast(Gtk.Button, Gtk.Template.Child())
    status_status_page = cast(Gtk.StackPage, Gtk.Template.Child())
    status_row = cast(Adw.ActionRow, Gtk.Template.Child())
    status_icon = cast(Adw.Bin, Gtk.Template.Child())
    progress_bar = cast(Gtk.ProgressBar, Gtk.Template.Child())
    metadata_source = cast(Adw.ActionRow, Gtk.Template.Child())
    metadata_output = cast(Adw.ActionRow, Gtk.Template.Child())
    metadata_region_value = cast(Gtk.Label, Gtk.Template.Child())
    metadata_version_value = cast(Gtk.Label, Gtk.Template.Child())
    metadata_seed_value = cast(Gtk.Label, Gtk.Template.Child())
    box_source_output = cast(Gtk.ListBox, Gtk.Template.Child())

    input_rom_path: str
    rom: NintendoDSRom
    rom_static_data: Pmd2Data
    randomization_settings: RandomizerConfig
    seed: int | str
    output_file: Gio.File | None
    _is_currently_randomizing: bool
    _randomizer: RandomizerThread | None

    def __init__(
        self,
        input_rom_path: str,
        rom: NintendoDSRom,
        rom_static_data: Pmd2Data,
        randomization_settings: RandomizerConfig,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.input_rom_path = input_rom_path
        self.rom = rom
        self.rom_static_data = rom_static_data
        self.randomization_settings = randomization_settings
        self.seed = get_effective_seed(self.randomization_settings["seed"])
        self.output_file = None
        self._is_currently_randomizing = False
        self._randomizer = None

        self.metadata_source.set_subtitle(self.input_rom_path)
        self.metadata_region_value.set_label(self.rom_static_data.game_edition)
        self.metadata_version_value.set_label(version())
        self.metadata_seed_value.set_label(str(self.seed))

        if "RUNNING_IN_FLATPAK" in os.environ:
            # Currently the file info in the dialog is useless, see:
            # https://github.com/flatpak/xdg-desktop-portal/issues/475
            self.box_source_output.hide()
            self.set_content_height(380)

    @Gtk.Template.Callback()
    def on_close_attempt(self, *args):
        if not self._is_currently_randomizing:
            self.force_close()
            return

        def on_response(_, response):
            if response == "Yes":
                self.force_cancel_randomization()
                self.force_close()

        d = Adw.AlertDialog(
            body=_("This will stop the randomization process and allow you to change settings again."),
            heading=_("Cancel randomization?"),
        )
        d.add_response("No", _("_No"))
        d.add_response("Yes", _("_Yes"))
        d.set_response_appearance("Yes", Adw.ResponseAppearance.DESTRUCTIVE)
        d.connect("response", on_response)
        d.present(GtkFrontend.instance().window)

    @Gtk.Template.Callback()
    def on_realize(self, *args):
        if sys.platform.startswith("darwin"):
            self.header_bar.set_decoration_layout("close:")

    @Gtk.Template.Callback()
    def on_start_button_clicked(self, *args):
        frontend = GtkFrontend.instance()
        nds_filter = Gtk.FileFilter()
        nds_filter.add_suffix("nds")
        nds_filter.add_mime_type("application/x-nintendo-ds-rom")
        documents_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if documents_dir is not None:
            default_dir = Gio.File.new_for_path(documents_dir)
            dialog_for_file = Gtk.FileDialog(
                initial_folder=default_dir,
                default_filter=nds_filter,
                initial_name="randomized_rom.nds",
            )
        else:
            dialog_for_file = Gtk.FileDialog(default_filter=nds_filter, initial_name="randomized_rom.nds")
        dialog_for_file.save(frontend.window, None, self.do_save)

    def do_save(self, dialog, result):
        try:
            file = dialog.save_finish(result)
        except Exception as e:
            if not isinstance(e, GLib.GError) or "dismissed" not in str(e).lower():
                GtkFrontend.instance().display_error(
                    _("Error while opening file ({}).").format(e),
                    cast(Gtk.Window, self.get_root()),
                )
            return
        if not file.get_path().lower().endswith(".nds"):
            GtkFrontend.instance().display_error(
                _("The path of the ROM file needs to end in '.nds'."),
                cast(Gtk.Window, self.get_root()),
            )
            return
        self.output_file = file

        # Adjust UI
        self._is_currently_randomizing = True
        self.status_stack.set_visible_child(self.status_status_page.get_child())
        self.metadata_output.set_subtitle(self.output_file.get_path())  # type: ignore
        self.metadata_output.set_sensitive(True)
        self.metadata_output.add_css_class("property")
        self.status_row.set_title(_("Randomizing... ({}%)").format(0))

        # Configure and start randomizer
        status = Status()
        status.subscribe(lambda a, b: GLib.idle_add(partial(self.on_update_status, a, b)))
        random.seed(self.seed)
        randomizer = RandomizerThread(
            status,
            self.rom,
            self.randomization_settings,
            str(self.seed),
            GtkFrontend.instance(),
        )
        randomizer.start()
        self._randomizer = randomizer

        GLib.timeout_add(100, self.check_done)

    @Gtk.Template.Callback()
    def on_metadata_source_button_clicked(self, *args):
        open_dir(os.path.dirname(self.metadata_source.get_subtitle()))  # type: ignore

    @Gtk.Template.Callback()
    def on_metadata_output_button_clicked(self, *args):
        open_dir(os.path.dirname(self.metadata_output.get_subtitle()))  # type: ignore

    def on_update_status(self, progress: int, description: str):
        assert self._randomizer is not None
        self.progress_bar.set_fraction((progress - 1) / self._randomizer.total_steps)
        if description != Status.DONE_SPECIAL_STR:
            abs_progress = floor((progress - 1) / self._randomizer.total_steps * 100)
            self.status_row.set_title(_("Randomizing... ({}%)").format(abs_progress))
            self.status_row.set_subtitle(description)

    def force_cancel_randomization(self):
        if self._randomizer is None:
            return
        thread_id = self._randomizer.get_thread_id()
        if thread_id is None:
            return
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), 0)
            raise ValueError("Failed to stop thread")

    def check_done(self):
        assert self._randomizer is not None
        if not self._randomizer.is_done():
            return True
        self._is_currently_randomizing = False
        if self._randomizer.error:
            status_img_path = os.path.join(data_dir(), "duskako_sad.png")
            traceback_str = "".join(traceback.format_exception(*self._randomizer.error))
            self.status_row.set_title(_("Randomizing failed!"))
            self.status_row.set_subtitle(_("Error: {}").format(traceback_str))
            self.status_row.set_subtitle_selectable(True)
            self.status_row.add_css_class("error")
        else:
            assert self.output_file is not None
            out_path = self.output_file.get_path()
            assert out_path is not None
            self.rom.saveToFile(out_path, updateDeviceCapacity=True)
            status_img_path = os.path.join(data_dir(), "duskako_happy.png")
            self.status_row.set_title(_("Randomizing complete!"))
            self.status_row.set_subtitle("")
            self.status_row.add_css_class("success")

        image = Gtk.Image.new_from_file(status_img_path)
        image.set_size_request(40, 40)
        self.status_icon.set_child(image)

        return False
