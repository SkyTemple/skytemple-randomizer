#  Copyright 2020-2023 Capypara and the SkyTemple Contributors
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

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('GtkSource', '5')

import logging
import os
import sys
from typing import Callable

from skytemple_icons import icons
from skytemple_randomizer.config import data_dir
from skytemple_randomizer.frontend.abstract import AbstractFrontend

from gi.repository import Adw, Gtk, GLib, Gdk


if getattr(sys, 'frozen', False):
    # Running via PyInstaller. Fix SSL configuration
    os.environ["SSL_CERT_FILE"] = os.path.join(
        os.path.dirname(sys.executable), "certifi", "cacert.pem"
    )


class GtkFrontend(AbstractFrontend):
    def idle_add(self, fn: Callable):
        GLib.idle_add(fn)


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "skytemple_randomizer.ui"))
class MainWindow(Adw.ApplicationWindow):
    __gtype_name__ = "main_window"


class MainApp(Adw.Application):
    def __init__(self):
        # Load Builder and Window
        super().__init__(application_id="org.skytemple.Randomizer")
        GLib.set_application_name("SkyTemple Randomizer")

    def do_activate(self) -> None:
        window = MainWindow(application=self)
        window.present()


def main():
    path = os.path.abspath(os.path.dirname(__file__))

    if sys.platform.startswith('win'):
        # Solve issue #12
        try:
            from skytemple_files.common.platform_utils.win import win_set_error_mode
            win_set_error_mode()
        except BaseException:
            # This really shouldn't fail, but it's not important enough to crash over
            pass

    if sys.platform.startswith('darwin'):
        # The search path is wrong if SkyTemple is executed as an .app bundle
        if getattr(sys, 'frozen', False):
            path = os.path.dirname(sys.executable)

    display = Gdk.Display.get_default()
    assert display is not None
    itheme = Gtk.IconTheme.get_for_display(display)
    itheme.add_search_path(os.path.abspath(icons()))
    itheme.add_search_path(os.path.abspath(os.path.join(data_dir(), "icons")))

    # Load CSS
    style_provider = Gtk.CssProvider()
    style_provider.load_from_path(os.path.join(path, "skytemple_randomizer.css"))
    Gtk.StyleContext.add_provider_for_display(display, style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    # Load main window + controller
    app = MainApp()
    sys.exit(app.run(sys.argv))


if __name__ == '__main__':
    # TODO: At the moment doesn't support any cli arguments.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
