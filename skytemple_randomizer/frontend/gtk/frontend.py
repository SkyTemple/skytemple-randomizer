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

import os.path
from typing import Callable, TYPE_CHECKING

from gi.repository import GLib, Gtk, Adw
from ndspy.rom import NintendoDSRom
from skytemple_files.common.i18n_util import _
from skytemple_files.common.ppmdu_config.data import Pmd2Data

from skytemple_randomizer.config import RandomizerConfig, ConfigFileLoader
from skytemple_randomizer.data_dir import data_dir
from skytemple_randomizer.frontend.abstract import AbstractFrontend, PortraitDebugLine
from skytemple_randomizer.frontend.gtk.settings import (
    SkyTempleRandomizerSettingsStoreGtk,
)
from skytemple_randomizer.frontend.gtk.widgets.window_portrait_debug import (
    PortraitDebugWindow,
)

if TYPE_CHECKING:
    from skytemple_randomizer.frontend.gtk.main import MainApp
    from skytemple_randomizer.frontend.gtk.widgets import AppWindow


class GtkFrontend(AbstractFrontend):
    __INSTANCE: GtkFrontend | None = None

    __settings: SkyTempleRandomizerSettingsStoreGtk | None
    __randomization_settings: RandomizerConfig | None
    __application: MainApp | None
    __window: AppWindow | None
    __portrait_debug_window: PortraitDebugWindow | None
    __input_rom: NintendoDSRom | None
    __input_rom_static_data: Pmd2Data | None

    def __init__(self):
        self.__settings = None
        self.__randomization_settings = None
        self.__window = None
        self.__portrait_debug_window = None
        self.__application = None
        self.__input_rom = None
        self.__input_rom_static_data = None

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

    def init_rom(self, rom: NintendoDSRom, rom_static_data: Pmd2Data | None = None):
        # TODO: Support different default configs based on region?
        self.__input_rom = rom
        self.__input_rom_static_data = rom_static_data
        self.__randomization_settings = ConfigFileLoader.load(os.path.join(data_dir(), "default.json"))

    @property
    def randomization_settings(self) -> RandomizerConfig:
        assert self.__randomization_settings is not None
        return self.__randomization_settings

    @randomization_settings.setter
    def randomization_settings(self, value):
        self.__randomization_settings = value

    @property
    def window(self) -> AppWindow:
        assert self.__window is not None
        return self.__window

    @window.setter
    def window(self, value):
        self.__window = value

    @property
    def portrait_debug_window(self) -> PortraitDebugWindow:
        assert self.__portrait_debug_window is not None
        return self.__portrait_debug_window

    @portrait_debug_window.setter
    def portrait_debug_window(self, value):
        self.__portrait_debug_window = value

    @property
    def application(self) -> MainApp:
        assert self.__application is not None
        return self.__application

    @application.setter
    def application(self, value):
        self.__application = value

    @property
    def input_rom(self) -> NintendoDSRom:
        assert self.__input_rom is not None
        return self.__input_rom

    @property
    def input_rom_static_data(self) -> Pmd2Data:
        assert self.__input_rom_static_data is not None
        return self.__input_rom_static_data

    def display_error(self, error: str, parent: Gtk.Window):
        d = Adw.AlertDialog(
            body=error,
            heading=_("Error"),
        )
        d.add_response("OK", _("_OK"))
        d.present(GtkFrontend.instance().window)

    def idle_add(self, fn: Callable):
        GLib.idle_add(fn)

    def portrait_debug__clear(self):
        if self.__portrait_debug_window is not None:
            self.__portrait_debug_window.clear_debugs()

    def portrait_debug__add(self, line: PortraitDebugLine):
        if self.__portrait_debug_window is not None:
            self.__portrait_debug_window.add_debug(line)
