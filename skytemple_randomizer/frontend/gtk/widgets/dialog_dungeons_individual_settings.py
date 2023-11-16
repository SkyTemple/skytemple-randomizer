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

import os
import sys
from typing import cast, Optional

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, GObject


@Gtk.Template(
    filename=os.path.join(MAIN_PATH, "dialog_dungeons_individual_settings.ui")
)
class DungeonsIndividualSettingsDialog(Adw.Window):
    __gtype_name__ = "StDungeonsIndividualSettingsDialog"

    header_bar = cast(Adw.HeaderBar, Gtk.Template.Child())
    content = cast(Adw.Bin, Gtk.Template.Child())

    @Gtk.Template.Callback()
    def on_realize(self, *args):
        if sys.platform.startswith("darwin"):
            self.header_bar.set_decoration_layout("close:")

        close_esc = Gtk.Shortcut(
            trigger=Gtk.ShortcutTrigger.parse_string("Escape|<Control>w"),
            action=Gtk.NamedAction(action_name="window.close"),
        )
        self.add_shortcut(close_esc)

    def populate_settings(self, config: RandomizerConfig):
        pass
