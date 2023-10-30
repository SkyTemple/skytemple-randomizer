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

from skytemple_randomizer.frontend.gtk.init_locale import init_locale

init_locale()

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('GtkSource', '5')

import logging
import os
import sys

from skytemple_icons import icons
from skytemple_randomizer.data_dir import data_dir

from gi.repository import Adw, Gtk, GLib, Gdk, GtkSource  # noqa

from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.widgets import MainWindow


if getattr(sys, 'frozen', False):
    # Running via PyInstaller. Fix SSL configuration
    os.environ["SSL_CERT_FILE"] = os.path.join(
        os.path.dirname(sys.executable), "certifi", "cacert.pem"
    )


class MainApp(Adw.Application):
    def __init__(self):
        # Load Builder and Window
        super().__init__(application_id="org.skytemple.Randomizer")
        GLib.set_application_name("SkyTemple Randomizer")
        frontend = GtkFrontend.instance()
        frontend.application = self

    def do_activate(self) -> None:
        window = MainWindow(application=self)
        window.present()


def main(argv):
    if sys.platform.startswith('win'):
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

    # Load main window + controller
    app = MainApp()
    sys.exit(app.run(argv))


if __name__ == '__main__':
    GtkSource.init()
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main(sys.argv)
