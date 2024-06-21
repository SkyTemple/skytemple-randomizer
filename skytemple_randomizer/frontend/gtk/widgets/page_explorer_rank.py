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

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_explorer_rank.ui"))
class ExplorerRankPage(Adw.PreferencesPage):
    __gtype_name__ = "StExplorerRankPage"
    row_explorer_rank_unlocks = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_explorer_rank_rewards = cast(Adw.SwitchRow, Gtk.Template.Child())

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

        self.row_explorer_rank_unlocks.set_active(config["starters_npcs"]["explorer_rank_unlocks"])
        self.row_explorer_rank_rewards.set_active(config["starters_npcs"]["explorer_rank_rewards"])

        self._suppress_signals = False

    @Gtk.Template.Callback()
    def on_row_explorer_rank_unlocks_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["starters_npcs"]["explorer_rank_unlocks"] = (
            self.row_explorer_rank_unlocks.get_active()
        )

    @Gtk.Template.Callback()
    def on_row_explorer_rank_rewards_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["starters_npcs"]["explorer_rank_rewards"] = (
            self.row_explorer_rank_rewards.get_active()
        )
