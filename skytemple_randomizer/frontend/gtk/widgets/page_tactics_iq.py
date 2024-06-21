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


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_tactics_iq.ui"))
class TacticsIqPage(Adw.PreferencesPage):
    __gtype_name__ = "StTacticsIqPage"
    row_randomize_iq_groups = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_randomize_iq_gain = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_randomize_iq_skills = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_keep_universal_skills = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_randomize_iq_skill_groups = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_randomize_tactics = cast(Adw.SwitchRow, Gtk.Template.Child())

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

        self.row_randomize_iq_groups.set_active(config["pokemon"]["iq_groups"])
        self.row_randomize_iq_gain.set_active(config["iq"]["randomize_iq_gain"])
        self.row_randomize_iq_skills.set_active(config["iq"]["randomize_iq_skills"])
        self.row_keep_universal_skills.set_active(config["iq"]["keep_universal_skills"])
        self.row_randomize_iq_skill_groups.set_active(config["iq"]["randomize_iq_groups"])
        self.row_randomize_tactics.set_active(config["iq"]["randomize_tactics"])

        self._suppress_signals = False

    @Gtk.Template.Callback()
    def on_row_randomize_iq_groups_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["pokemon"]["iq_groups"] = self.row_randomize_iq_groups.get_active()

    @Gtk.Template.Callback()
    def on_row_randomize_iq_gain_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["iq"]["randomize_iq_gain"] = self.row_randomize_iq_gain.get_active()

    @Gtk.Template.Callback()
    def on_row_randomize_iq_skills_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["iq"]["randomize_iq_skills"] = self.row_randomize_iq_skills.get_active()

    @Gtk.Template.Callback()
    def on_row_keep_universal_skills_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["iq"]["keep_universal_skills"] = self.row_keep_universal_skills.get_active()

    @Gtk.Template.Callback()
    def on_row_randomize_iq_skill_groups_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["iq"]["randomize_iq_groups"] = self.row_randomize_iq_skill_groups.get_active()

    @Gtk.Template.Callback()
    def on_row_randomize_tactics_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["iq"]["randomize_tactics"] = self.row_randomize_tactics.get_active()
