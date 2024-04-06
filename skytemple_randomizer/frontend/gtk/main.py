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
import sys

from ndspy.rom import NintendoDSRom
from skytemple_files.common.ppmdu_config.data import Pmd2Data

from skytemple_randomizer.frontend.gtk.init_locale import init_locale

init_locale()

try:
    import gi
except ImportError:
    if __name__ == "__main__":
        print(
            "Failed to import gi. Did you install the Randomizer with the 'gtk' extra or install PyGObject manually?",
            file=sys.stderr,
        )
        exit(1)
    raise

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import logging
import os
import sys

from skytemple_icons import icons
from skytemple_randomizer.data_dir import data_dir

from gi.repository import Adw, Gtk, GLib, Gdk, Gio

Gtk.init()
Adw.init()

from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.widgets import AppWindow

if getattr(sys, "frozen", False):
    # Running via PyInstaller. Fix SSL configuration
    os.environ["SSL_CERT_FILE"] = os.path.join(
        os.path.dirname(sys.executable), "certifi", "cacert.pem"
    )

SKYTEMPLE_DEV = "SKYTEMPLE_DEV" in os.environ


class MainApp(Adw.Application):
    development_mode: bool

    def __init__(self):
        # Load Builder and Window
        app_id = (
            "org.skytemple.Randomizer.Devel"
            if SKYTEMPLE_DEV
            else "org.skytemple.Randomizer"
        )
        super().__init__(application_id=app_id, flags=Gio.ApplicationFlags.HANDLES_OPEN)
        self.connect("open", self.on_open)
        GLib.set_application_name("SkyTemple Randomizer")
        frontend = GtkFrontend.instance()
        frontend.application = self
        self.development_mode = SKYTEMPLE_DEV

    def do_activate(self, file: str | None = None) -> None:
        window = AppWindow(application=self)
        frontend = GtkFrontend.instance()
        frontend.window = window
        self.show_start_stack()
        if file is not None:
            window.stack_item_start.load_rom(file)
        window.present()

    def on_open(self, _, files: list[Gio.File], *args):
        self.do_activate(files[0].get_path())

    def show_start_stack(self, disable_recent: bool = False):
        frontend = GtkFrontend.instance()
        frontend.window.stack_item_start.init_recent(disable_recent)
        frontend.window.content_stack.set_visible_child(
            frontend.window.stack_item_start
        )

    def show_main_stack(
        self,
        rom_path: str,
        rom: NintendoDSRom,
        rom_static_data: Pmd2Data,
    ):
        frontend = GtkFrontend.instance()
        frontend.window.stack_item_main.init_rom(rom_path, rom, rom_static_data)
        frontend.window.content_stack.set_visible_child(frontend.window.stack_item_main)


def main(argv: list[str] | None = None):
    if argv is None:
        argv = sys.argv
    if sys.platform.startswith("win"):
        # Solve issue #12
        try:
            from skytemple_files.common.platform_utils.win import win_set_error_mode

            win_set_error_mode()
        except BaseException:
            # This really shouldn't fail, but it's not important enough to crash over
            pass

    display = Gdk.Display.get_default()
    assert display is not None
    itheme = Gtk.IconTheme.get_for_display(display)
    itheme.add_search_path(os.path.abspath(icons()))
    itheme.add_search_path(os.path.abspath(os.path.join(data_dir(), "icons")))

    # Load CSS
    style_provider = Gtk.CssProvider()
    style_provider.load_from_path(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), "skytemple_randomizer.css")
        )
    )
    default_display = Gdk.Display.get_default()
    if default_display is not None:
        Gtk.StyleContext.add_provider_for_display(
            default_display,
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    # Load main window + controller
    app = MainApp()
    sys.exit(app.run(argv))


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
