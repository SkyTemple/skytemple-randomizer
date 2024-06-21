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

from skytemple_files.common.i18n_util import _

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_music.ui"))
class MusicPage(Adw.PreferencesPage):
    __gtype_name__ = "StMusicPage"
    row_topmenu_music = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_overworld_music = cast(Adw.SwitchRow, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    _suppress_signals: bool

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.randomization_settings = None
        self._suppress_signals = False

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config

        self.row_topmenu_music.set_active(config["starters_npcs"]["topmenu_music"])
        self.row_overworld_music.set_active(config["starters_npcs"]["overworld_music"])

        self._suppress_signals = False

    @Gtk.Template.Callback()
    def on_row_topmenu_music_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["starters_npcs"]["topmenu_music"] = self.row_topmenu_music.get_active()

    @Gtk.Template.Callback()
    def on_row_overworld_music_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["starters_npcs"]["overworld_music"] = self.row_overworld_music.get_active()

    def help_text(self) -> str:
        return _(
            "Dungeon music randomization can be enabled or disabled with the dungeon layout randomization setting."
        )
