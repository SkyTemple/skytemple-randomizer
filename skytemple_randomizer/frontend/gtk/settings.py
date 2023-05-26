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
import configparser
import logging
import os
from typing import Optional

from skytemple_files.common.project_file_manager import ProjectFileManager
from skytemple_files.common.util import open_utf8

CONFIG_FILE_NAME = 'randomizer.ini'

SECT_GENERAL = 'General'

KEY_HASH_LAST_DISMISSED_BANNER = 'hash_last_dismissed_banner'

logger = logging.getLogger(__name__)


class SkyTempleRandomizerSettingsStoreGtk:
    def __init__(self):
        self.config_dir = os.path.join(ProjectFileManager.shared_config_dir())
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, CONFIG_FILE_NAME)
        self.loaded_config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            try:
                with open_utf8(self.config_file, 'r') as f:
                    self.loaded_config.read_file(f)
            except BaseException as err:
                logger.error("Error reading config, falling back to default.", exc_info=err)

    def get_hash_last_dismissed_banner(self) -> Optional[str]:
        if SECT_GENERAL in self.loaded_config:
            if KEY_HASH_LAST_DISMISSED_BANNER in self.loaded_config[SECT_GENERAL]:
                return self.loaded_config[SECT_GENERAL][KEY_HASH_LAST_DISMISSED_BANNER]
        return None

    def set_hash_last_dismissed_banner(self, val: str):
        if SECT_GENERAL not in self.loaded_config:
            self.loaded_config[SECT_GENERAL] = {}
        self.loaded_config[SECT_GENERAL][KEY_HASH_LAST_DISMISSED_BANNER] = val
        self._save()

    def _save(self):
        with open_utf8(self.config_file, 'w') as f:
            self.loaded_config.write(f)
