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
import webbrowser
from typing import cast

import packaging.version
from gi.repository import Gtk, Adw
from skytemple_files.common.version_util import check_newest_release, ReleaseType

from skytemple_randomizer.config import version
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "banner_update_info.ui"))
class UpdateInfoBanner(Adw.Bin):
    __gtype_name__ = "StUpdateInfoBanner"

    update_info = cast(Adw.Banner, Gtk.Template.Child())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._check_for_updates()

    @Gtk.Template.Callback()
    def on_update_info_button_clicked(self, *args):
        webbrowser.open_new_tab("https://download.skytemple.org/randomizer/latest")

    def _check_for_updates(self):
        try:
            ver = version()
            if ver == "dev":
                return
            new_version = check_newest_release(ReleaseType.SKYTEMPLE_RANDOMIZER)
            if packaging.version.parse(ver) < packaging.version.parse(new_version):
                self.update_info.set_title(self.update_info.get_title().replace("{version}", new_version))
                return
        except Exception:
            pass
        # else/except:
        self.update_info.set_revealed(False)
