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
import platform
import sys

if getattr(sys, "frozen", False):
    # All UI files are copied into the root.
    system = platform.system()
    if system == "Windows":
        MAIN_PATH = os.path.join(os.path.dirname(sys.executable), "_internal")
    elif system == "Darwin":
        MAIN_PATH = os.path.join(os.path.dirname(sys.executable), "..", "Resources")
    else:
        MAIN_PATH = os.path.dirname(sys.executable)
else:
    MAIN_PATH = os.path.join(os.path.dirname(__file__), "widgets")
