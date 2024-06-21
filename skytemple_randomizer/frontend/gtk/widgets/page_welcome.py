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

from skytemple_files.common.ppmdu_config.data import Pmd2Data

from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_welcome.ui"))
class WelcomePage(Adw.Bin):
    __gtype_name__ = "StWelcomePage"

    current_rom_name = cast(Gtk.Label, Gtk.Template.Child())

    def set_input_rom(self, path: str, static_data: Pmd2Data):
        self.current_rom_name.set_text(f"{os.path.basename(path)} ({static_data.game_edition})")
