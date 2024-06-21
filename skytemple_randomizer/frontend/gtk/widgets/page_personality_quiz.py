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
from typing import Callable, cast

from skytemple_randomizer.config import RandomizerConfig, QuizMode
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.widgets import RandomizationSettingsWidget


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_personality_quiz.ui"))
class PersonalityQuizPage(Adw.PreferencesPage):
    __gtype_name__ = "StPersonalityQuizPage"
    row_mode = cast(Adw.ComboRow, Gtk.Template.Child())
    row_randomize = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_include_vanilla_questions = cast(Adw.SwitchRow, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    parent_page: RandomizationSettingsWidget
    on_change_quiz_active: Callable[[bool], None]
    _suppress_signals: bool

    def __init__(
        self,
        *args,
        parent_page: RandomizationSettingsWidget,
        on_change_quiz_active: Callable[[bool], None],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parent_page = parent_page
        self.randomization_settings = None
        self.on_change_quiz_active = on_change_quiz_active
        self._suppress_signals = False

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config
        self.row_mode.set_selected(config["quiz"]["mode"].value)
        self.row_randomize.set_active(config["quiz"]["randomize"])
        self.row_include_vanilla_questions.set_active(config["quiz"]["include_vanilla_questions"])
        self._suppress_signals = False

    @Gtk.Template.Callback()
    def on_row_mode_notify_selected(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["quiz"]["mode"] = QuizMode(self.row_mode.get_selected())

    @Gtk.Template.Callback()
    def on_row_randomize_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["quiz"]["randomize"] = self.row_randomize.get_active()
        self.on_change_quiz_active(self.row_randomize.get_active())

    @Gtk.Template.Callback()
    def on_row_include_vanilla_questions_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["quiz"]["include_vanilla_questions"] = (
            self.row_include_vanilla_questions.get_active()
        )
