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
from typing import cast

from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.widgets import StartStack, MainStack


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "window_app.ui"))
class AppWindow(Adw.ApplicationWindow):
    __gtype_name__ = "StAppWindow"

    content_stack = cast(Gtk.Stack, Gtk.Template.Child())
    stack_item_start = cast(StartStack, Gtk.Template.Child())
    stack_item_main = cast(MainStack, Gtk.Template.Child())

    @Gtk.Template.Callback()
    def on_realize(self, *args):
        frontend = GtkFrontend.instance()
        window_size = frontend.settings.get_window_size()
        if window_size is not None:
            self.set_default_size(*window_size)
        if frontend.settings.get_window_maximized():
            self.maximize()
        else:
            self.unmaximize()
        if frontend.application.development_mode:
            self.add_css_class("devel")

    @Gtk.Template.Callback()
    def on_main_window_notify_default_width(self, *args):
        if not self.is_maximized() and self.get_width() > 0:
            GtkFrontend.instance().settings.set_window_width(self.get_width())

    @Gtk.Template.Callback()
    def on_main_window_notify_default_height(self, *args):
        if not self.is_maximized() and self.get_height() > 0:
            GtkFrontend.instance().settings.set_window_height(self.get_height())

    @Gtk.Template.Callback()
    def on_main_window_notify_maximized(self, *args):
        GtkFrontend.instance().settings.set_window_maximized(self.is_maximized())
