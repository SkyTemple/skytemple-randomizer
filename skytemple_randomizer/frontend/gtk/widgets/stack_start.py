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
import struct
import sys
import webbrowser
from typing import cast

from ndspy.rom import NintendoDSRom
from skytemple_files.common.i18n_util import _
from skytemple_files.common.util import get_ppmdu_config_for_rom
from skytemple_files.common.version_util import get_event_banner

from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Gdk, GdkPixbuf, Adw, GLib, Gio


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "stack_start.ui"))
class StartStack(Adw.Bin):
    __gtype_name__ = "StStartStack"

    header_bar = cast(Gtk.HeaderBar, Gtk.Template.Child())
    banner_info_wrapper = cast(Adw.Clamp, Gtk.Template.Child())
    banner_info = cast(Gtk.Box, Gtk.Template.Child())
    button_load_last_rom = cast(Gtk.Button, Gtk.Template.Child())
    button_load_rom = cast(Gtk.Button, Gtk.Template.Child())

    disable_recent: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_recent(False)
        self._check_for_banner()

    def init_recent(self, disable_recent: bool):
        self.disable_recent = disable_recent
        recent_rom = GtkFrontend.instance().settings.get_recent_rom()
        if self.disable_recent or recent_rom is None:
            self.button_load_last_rom.hide()
            self.button_load_rom.add_css_class("suggested-action")
            self.button_load_rom.add_css_class("title-2")
            self.button_load_rom.set_label(_("Load ROM"))
        else:
            self.button_load_last_rom.show()
            self.button_load_rom.remove_css_class("suggested-action")
            self.button_load_rom.remove_css_class("title-2")
            self.button_load_last_rom.set_label(
                _("Load {}").format(  # TRANSLATORS: Load abc.nds (= load a file)
                    os.path.basename(recent_rom)
                )
            )
            self.button_load_rom.set_label(_("Load another ROM"))

    @Gtk.Template.Callback()
    def on_realize(self, *args):
        if sys.platform.startswith("darwin"):
            self.header_bar.set_decoration_layout("close,minimize,maximize:")

    @Gtk.Template.Callback()
    def on_button_load_last_rom_clicked(self, *args):
        self.load_rom(GtkFrontend.instance().settings.get_recent_rom())

    @Gtk.Template.Callback()
    def on_button_load_rom_clicked(self, *args):
        frontend = GtkFrontend.instance()
        nds_filter = Gtk.FileFilter()
        nds_filter.add_suffix("nds")
        nds_filter.add_mime_type("application/x-nintendo-ds-rom")
        documents_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if documents_dir is not None:
            default_dir = Gio.File.new_for_path(documents_dir)
            dialog_for_file = Gtk.FileDialog(initial_folder=default_dir, default_filter=nds_filter)
        else:
            dialog_for_file = Gtk.FileDialog(default_filter=nds_filter)
        dialog_for_file.open(frontend.window, None, self.on_file_loaded)

    def on_file_loaded(self, dialog, result):
        try:
            file: Gio.File = dialog.open_finish(result)
        except Exception as e:
            if not isinstance(e, GLib.GError) or "dismissed" not in str(e).lower():
                GtkFrontend.instance().display_error(
                    _("Failed to load ROM: Error while opening file ({}).").format(e),
                    cast(Gtk.Window, self.get_root()),
                )
            return
        path = file.get_path()
        assert path is not None
        GtkFrontend.instance().settings.set_recent_rom(path)
        self.load_rom(path)

    def load_rom(self, path: str):
        try:
            rom = NintendoDSRom.fromFile(path)
            static_data = get_ppmdu_config_for_rom(rom)
        except struct.error:
            GtkFrontend.instance().display_error(
                _("Failed to load ROM:")
                + " "
                + _('Are you sure you provided a ROM? A ROM usually has the file extension ".nds".'),
                cast(Gtk.Window, self.get_root()),
            )
        except Exception as e:
            GtkFrontend.instance().display_error(
                _("Failed to load ROM:") + str(e),
                cast(Gtk.Window, self.get_root()),
            )
            return
        GtkFrontend.instance().application.show_main_stack(path, rom, static_data)

    def _check_for_banner(self):
        try:
            # uncomment the following line to test banner.
            # import skytemple_files.common.version_util; skytemple_files.common.version_util.RELEASE_WEB = "https://raw.githubusercontent.com/SkyTemple/release-info/17d9087293f9c11a2353dd60e878bd78874496fc/"
            img_banner, url = get_event_banner()
            if img_banner is not None:
                input_stream = Gio.MemoryInputStream.new_from_data(img_banner, None)
                pixbuf = GdkPixbuf.Pixbuf.new_from_stream(input_stream, None)
                assert pixbuf is not None
                image = Gtk.Picture.new_for_pixbuf(pixbuf)
                image.set_can_shrink(True)
                image.set_hexpand(True)
                image.set_size_request(0, 70)

                def open_web(*args):
                    if url is not None:
                        webbrowser.open_new_tab(url)

                def cursor_change_enter(*args):
                    self.banner_info.set_cursor_from_name("pointer")

                def cursor_change_leave(*args):
                    self.banner_info.set_cursor_from_name("default")

                click_gesture = Gtk.GestureClick()
                click_gesture.set_button(Gdk.BUTTON_PRIMARY)
                click_gesture.connect("pressed", open_web)
                self.banner_info.add_controller(click_gesture)
                motion_controller = Gtk.EventControllerMotion()
                motion_controller.connect("enter", cursor_change_enter)
                motion_controller.connect("leave", cursor_change_leave)
                self.banner_info.add_controller(motion_controller)
                self.banner_info.append(image)
                self.banner_info_wrapper.show()
                return
        except Exception:
            pass
        # else/except:
        self.banner_info_wrapper.hide()
