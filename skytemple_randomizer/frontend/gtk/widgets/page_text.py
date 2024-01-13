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

import os
from typing import cast

from skytemple_files.common.i18n_util import _

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.ui_util import set_default_dialog_size
from skytemple_randomizer.frontend.gtk.widgets import (
    PersonalityQuizPage,
    TextPool,
    RandomizationSettingsWindow,
    TextPoolPage,
    BaseSettingsDialog,
    SubpageStackEntry,
)


@Gtk.Template(filename=os.path.join(MAIN_PATH, "page_text.ui"))
class TextPage(Adw.PreferencesPage):
    __gtype_name__ = "StTextPage"

    row_personality_quiz = cast(Adw.SwitchRow, Gtk.Template.Child())
    button_randomize_personality_quiz = cast(Gtk.Button, Gtk.Template.Child())
    row_location_names = cast(Adw.SwitchRow, Gtk.Template.Child())
    button_randomize_location_names = cast(Gtk.Button, Gtk.Template.Child())
    row_chapter_titles = cast(Adw.SwitchRow, Gtk.Template.Child())
    button_randomize_chapter_titles = cast(Gtk.Button, Gtk.Template.Child())
    row_randomize_main_text = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_randomize_story_dialogue = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_enable_instant_text = cast(Adw.SwitchRow, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    _suppress_signals: bool

    @Gtk.Template.Callback()
    def on_signal_for_dialog(self, w: Gtk.Widget, *args):
        dialog: RandomizationSettingsWindow | None = None
        if w == self.button_randomize_personality_quiz:
            page1_pp = PersonalityQuizPage(parent_page=self)
            dialog = BaseSettingsDialog(
                title=self.row_personality_quiz.get_title(),
                content=page1_pp,
                getter=page1_pp.get_enabled,
                setter=page1_pp.set_enabled,
            )
        if w == self.button_randomize_location_names:
            page1_ln = TextPoolPage(pool=TextPool.LOCATIONS_A, parent_page=self)
            page2_ln = TextPoolPage(pool=TextPool.LOCATIONS_B, parent_page=self)
            dialog = BaseSettingsDialog(
                title=self.row_location_names.get_title(),
                content=(
                    SubpageStackEntry(
                        child=page1_ln,
                        name="first_word",
                        title=_("1st Word"),
                        icon_name="skytemple-e-dungeon-floor-symbolic",
                    ),
                    SubpageStackEntry(
                        child=page2_ln,
                        name="second_word",
                        title=_("2nd Word"),
                        icon_name="skytemple-e-dungeon-floor-symbolic",
                    ),
                ),
                getter=page1_ln.get_enabled,
                setter=page1_ln.set_enabled,
            )
        if w == self.button_randomize_chapter_titles:
            page_ct = TextPoolPage(pool=TextPool.CHAPTER_TITLES, parent_page=self)
            dialog = BaseSettingsDialog(
                title=self.row_chapter_titles.get_title(),
                content=page_ct,
                getter=page_ct.get_enabled,
                setter=page_ct.set_enabled,
            )

        if dialog is not None:
            frontend = GtkFrontend.instance()
            set_default_dialog_size(dialog, frontend.window)
            dialog.populate_settings(frontend.randomization_settings)
            dialog.set_transient_for(frontend.window)
            dialog.set_application(frontend.application)
            dialog.present()
            return False

    @Gtk.Template.Callback()
    def on_row_personality_quiz_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["quiz"][
            "randomize"
        ] = self.row_personality_quiz.get_active()

    @Gtk.Template.Callback()
    def on_row_location_names_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["locations"][
            "randomize"
        ] = self.row_location_names.get_active()

    @Gtk.Template.Callback()
    def on_row_chapter_titles_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["chapters"][
            "randomize"
        ] = self.row_chapter_titles.get_active()

    @Gtk.Template.Callback()
    def on_row_randomize_main_text_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["text"][
            "main"
        ] = self.row_randomize_main_text.get_active()

    @Gtk.Template.Callback()
    def on_row_randomize_story_dialogue_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["text"][
            "story"
        ] = self.row_randomize_story_dialogue.get_active()

    @Gtk.Template.Callback()
    def on_row_enable_instant_text_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["text"][
            "instant"
        ] = self.row_enable_instant_text.get_active()

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config
        self.row_personality_quiz.set_active(config["quiz"]["randomize"])
        self.row_location_names.set_active(config["locations"]["randomize"])
        self.row_chapter_titles.set_active(config["chapters"]["randomize"])
        self.row_randomize_main_text.set_active(config["text"]["main"])
        self.row_randomize_story_dialogue.set_active(config["text"]["story"])
        self.row_enable_instant_text.set_active(config["text"]["instant"])
        self._suppress_signals = False
