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

from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, GObject


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "popover_help.ui"))
class HelpPopover(Gtk.Popover):
    __gtype_name__ = "StHelpPopover"

    label_widget = cast(Gtk.Label, Gtk.Template.Child())
    _label: str = ""

    def __init__(self, *, label: str | None = None, **kwargs):
        super().__init__(**kwargs)
        if label:
            self.label = label  # type: ignore

    @Gtk.Template.Callback()
    def on_realize(self, *args):
        self.label_widget.set_label(self.label)  # type: ignore

    @GObject.Property(type=str)
    def label(self):
        return self._label

    @label.setter  # type: ignore
    def label(self, value):
        self._label = value
        if self.get_realized():
            self.label_widget.set_label(self.label)  # type: ignore
