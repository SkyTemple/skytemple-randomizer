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
from typing import cast

from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw


@Gtk.Template(filename=os.path.join(MAIN_PATH, "page_dungeons.ui"))
class DungeonsPage(Adw.PreferencesPage):
    __gtype_name__ = "StDungeonsPage"
    row_dungeon_mode = cast(Adw.ComboRow, Gtk.Template.Child())
    row_randomization_settings = cast(Adw.ActionRow, Gtk.Template.Child())
    row_chance_thresholds = cast(Adw.ActionRow, Gtk.Template.Child())
    row_per_dungeon_settings = cast(Adw.ActionRow, Gtk.Template.Child())

    @Gtk.Template.Callback()
    def on_signal_for_dialog(self, w: Gtk.Widget, *args):
        pass

    @Gtk.Template.Callback()
    def on_row_dungeon_mode_starters_notify_selected(self, *args):
        pass
