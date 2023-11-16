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

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.widgets import (
    PersonalityQuizDialog,
    LocationNamesTextPools,
    ChapterTitlesTextPool,
    RandomizationSettingsWindow,
    TextPoolDialog,
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

    @Gtk.Template.Callback()
    def on_signal_for_dialog(self, w: Gtk.Widget, *args):
        dialog: RandomizationSettingsWindow | None = None
        if w == self.button_randomize_personality_quiz:
            dialog = PersonalityQuizDialog(
                title=self.row_personality_quiz.get_title(),
            )
        if w == self.button_randomize_location_names:
            dialog = TextPoolDialog(
                title=self.row_location_names.get_title(),
                pools=LocationNamesTextPools(),
            )
        if w == self.button_randomize_chapter_titles:
            dialog = TextPoolDialog(
                title=self.row_chapter_titles.get_title(),
                pools=ChapterTitlesTextPool(),
            )

        if dialog is not None:
            frontend = GtkFrontend.instance()
            width, height = frontend.window.get_default_size()
            dialog.set_default_size(round(width * 0.8), round(height * 0.8))
            dialog.populate_settings(frontend.randomization_settings)
            dialog.set_transient_for(frontend.window)
            dialog.set_application(frontend.application)
            dialog.present()
            return False

    @Gtk.Template.Callback()
    def on_row_personality_quiz_notify_active(self, *args):
        pass

    @Gtk.Template.Callback()
    def on_row_location_names_notify_active(self, *args):
        pass

    @Gtk.Template.Callback()
    def on_row_chapter_titles_notify_active(self, *args):
        pass

    @Gtk.Template.Callback()
    def on_row_randomize_main_text_notify_active(self, *args):
        pass

    @Gtk.Template.Callback()
    def on_row_randomize_story_dialogue_notify_active(self, *args):
        pass

    @Gtk.Template.Callback()
    def on_row_enable_instant_text_notify_active(self, *args):
        pass

    def populate_settings(self, config: RandomizerConfig):
        pass
