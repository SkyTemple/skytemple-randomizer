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

import os.path
from typing import Callable, Optional

from gi.repository import GLib, Gtk, Adw
from skytemple_files.common.i18n_util import _

from skytemple_randomizer.config import RandomizerConfig, ConfigFileLoader
from skytemple_randomizer.data_dir import data_dir
from skytemple_randomizer.frontend.abstract import AbstractFrontend
from skytemple_randomizer.frontend.gtk.settings import (
    SkyTempleRandomizerSettingsStoreGtk,
)


class GtkFrontend(AbstractFrontend):
    __INSTANCE: Optional[GtkFrontend] = None

    __settings: Optional[SkyTempleRandomizerSettingsStoreGtk]
    __randomization_settings: Optional[RandomizerConfig]
    __application: Optional[Gtk.Application]
    __window: Optional[Gtk.ApplicationWindow]

    def __init__(self):
        self.__settings = None
        self.__randomization_settings = None
        self.__window = None
        self.__application = None

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

    @property
    def randomization_settings(self) -> RandomizerConfig:
        if self.__randomization_settings is None:
            self.__randomization_settings = ConfigFileLoader.load(
                os.path.join(data_dir(), "default.json")
            )
        return self.__randomization_settings

    @randomization_settings.setter
    def randomization_settings(self, value):
        self.__randomization_settings = value

    @property
    def window(self):
        v = self.__window
        assert v is not None
        return self.__window

    @window.setter
    def window(self, value):
        self.__window = value

    @property
    def application(self):
        v = self.__application
        assert v is not None
        return self.__application

    @application.setter
    def application(self, value):
        self.__application = value

    def display_error(self, error: str, parent: Gtk.Window):
        d = Adw.MessageDialog(
            body=error,
            application=self.application,
            modal=True,
            heading=_("Error"),
            transient_for=parent,
        )
        d.add_response("OK", _("_OK"))
        d.present()

    def idle_add(self, fn: Callable):
        GLib.idle_add(fn)
