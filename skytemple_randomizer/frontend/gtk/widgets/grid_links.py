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
import webbrowser

from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk

from skytemple_randomizer.frontend.gtk.ui_util import show_about_dialog


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "grid_links.ui"))
class LinksGrid(Gtk.Grid):
    __gtype_name__ = "StLinksGrid"

    @Gtk.Template.Callback()
    def on_button_wiki_clicked(self, *args):
        webbrowser.open_new_tab("https://wiki.skytemple.org/index.php/SkyTemple:UI-Link/skytemple-randomizer")

    @Gtk.Template.Callback()
    def on_button_discord_clicked(self, *args):
        webbrowser.open_new_tab("https://discord.gg/skytemple")

    @Gtk.Template.Callback()
    def on_button_skytemple_clicked(self, *args):
        webbrowser.open_new_tab("https://skytemple.org")

    @Gtk.Template.Callback()
    def on_about_button_clicked(self, *args):
        show_about_dialog(GtkFrontend.instance().window)
