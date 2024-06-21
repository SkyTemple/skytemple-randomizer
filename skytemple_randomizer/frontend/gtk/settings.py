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
import configparser
import logging
import os
from typing import Optional

from skytemple_files.common.project_file_manager import ProjectFileManager
from skytemple_files.common.util import open_utf8

CONFIG_FILE_NAME = "randomizer.ini"

SECT_WINDOW = "Window"

KEY_WINDOW_SIZE_X = "width"
KEY_WINDOW_SIZE_Y = "height"
KEY_WINDOW_IS_MAX = "is_max"
KEY_RECENT_ROM = "recent_rom"

logger = logging.getLogger(__name__)


class SkyTempleRandomizerSettingsStoreGtk:
    def __init__(self):
        self.config_dir = os.path.join(ProjectFileManager.shared_config_dir())
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, CONFIG_FILE_NAME)
        self.loaded_config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            try:
                with open_utf8(self.config_file, "r") as f:
                    self.loaded_config.read_file(f)
            except BaseException as err:
                logger.error("Error reading config, falling back to default.", exc_info=err)

    def get_window_size(self) -> Optional[tuple[int, int]]:
        if SECT_WINDOW in self.loaded_config:
            if (
                KEY_WINDOW_SIZE_X in self.loaded_config[SECT_WINDOW]
                and KEY_WINDOW_SIZE_Y in self.loaded_config[SECT_WINDOW]
            ):
                return int(self.loaded_config[SECT_WINDOW][KEY_WINDOW_SIZE_X]), int(
                    self.loaded_config[SECT_WINDOW][KEY_WINDOW_SIZE_Y]
                )
        return None

    def set_window_width(self, dim: int):
        if SECT_WINDOW not in self.loaded_config:
            self.loaded_config[SECT_WINDOW] = {}
        self.loaded_config[SECT_WINDOW][KEY_WINDOW_SIZE_X] = str(dim)
        self._save()

    def set_window_height(self, dim: int):
        if SECT_WINDOW not in self.loaded_config:
            self.loaded_config[SECT_WINDOW] = {}
        self.loaded_config[SECT_WINDOW][KEY_WINDOW_SIZE_Y] = str(dim)
        self._save()

    def get_window_maximized(self) -> bool:
        if SECT_WINDOW in self.loaded_config:
            if (
                KEY_WINDOW_IS_MAX in self.loaded_config[SECT_WINDOW]
                and self.loaded_config[SECT_WINDOW][KEY_WINDOW_IS_MAX] == "True"
            ):
                return True
        return False

    def set_window_maximized(self, value: bool):
        if SECT_WINDOW not in self.loaded_config:
            self.loaded_config[SECT_WINDOW] = {}
        self.loaded_config[SECT_WINDOW][KEY_WINDOW_IS_MAX] = str(value)
        self._save()

    def get_recent_rom(self) -> Optional[str]:
        if SECT_WINDOW in self.loaded_config:
            if KEY_RECENT_ROM in self.loaded_config[SECT_WINDOW]:
                return self.loaded_config[SECT_WINDOW][KEY_RECENT_ROM]
        return None

    def set_recent_rom(self, value: str):
        if SECT_WINDOW not in self.loaded_config:
            self.loaded_config[SECT_WINDOW] = {}
        self.loaded_config[SECT_WINDOW][KEY_RECENT_ROM] = value
        self._save()

    def _save(self):
        with open_utf8(self.config_file, "w") as f:
            self.loaded_config.write(f)
