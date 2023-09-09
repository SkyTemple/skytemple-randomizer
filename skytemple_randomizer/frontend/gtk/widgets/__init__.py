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

# Make sure the imports are ordered in a way that they don't cause circular imports.
from skytemple_randomizer.frontend.gtk.widgets.dialog_randomize import RandomizeDialog
from skytemple_randomizer.frontend.gtk.widgets.page_dungeons import DungeonsPage
from skytemple_randomizer.frontend.gtk.widgets.page_monsters import MonstersPage
from skytemple_randomizer.frontend.gtk.widgets.page_text import TextPage
from skytemple_randomizer.frontend.gtk.widgets.page_tweaks import TweaksPage
from skytemple_randomizer.frontend.gtk.widgets.page_welcome import WelcomePage
from skytemple_randomizer.frontend.gtk.widgets.dialog_settings import SettingsDialog
from skytemple_randomizer.frontend.gtk.widgets.window_main import MainWindow


__all__ = [
    "RandomizeDialog", "SettingsDialog", "DungeonsPage", "MonstersPage", "TextPage",
    "TweaksPage", "WelcomePage", "MainWindow"
]
