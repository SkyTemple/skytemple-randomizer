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

from typing import Callable, Optional

from gi.repository import GLib, Gtk

from skytemple_randomizer.frontend.abstract import AbstractFrontend
from skytemple_randomizer.frontend.gtk.settings import SkyTempleRandomizerSettingsStoreGtk


class GtkFrontend(AbstractFrontend):
    __INSTANCE: Optional[GtkFrontend] = None

    __settings: Optional[SkyTempleRandomizerSettingsStoreGtk]
    application: Optional[Gtk.Application]
    window: Optional[Gtk.ApplicationWindow]

    def __init__(self):
        self.__settings = None
        self.application = None

    @classmethod
    def instance(cls) -> GtkFrontend:
        if cls.__INSTANCE is None:
            cls.__INSTANCE = cls()
        return cls.__INSTANCE

    @property
    def settings(self):
        if self.__settings is None:
            self.__settings = SkyTempleRandomizerSettingsStoreGtk()
        return self.__settings

    def idle_add(self, fn: Callable):
        GLib.idle_add(fn)
