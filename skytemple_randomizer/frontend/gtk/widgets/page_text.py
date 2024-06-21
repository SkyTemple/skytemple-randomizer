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
from skytemple_files.common.ppmdu_config.data import GAME_REGION_JP

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.widgets import (
    PersonalityQuizPage,
    TextPool,
    RandomizationSettingsWindow,
    TextPoolPage,
    BaseSettingsDialog,
    SubpageStackEntry,
    PersonalityQuizQuestionsPage,
)


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_text.ui"))
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
    row_text_replacement_algorithm = cast(Adw.ComboRow, Gtk.Template.Child())
    group_full_text_randomization = cast(Adw.PreferencesGroup, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    _suppress_signals: bool

    @Gtk.Template.Callback()
    def on_signal_for_dialog(self, w: Gtk.Widget, *args):
        dialog: RandomizationSettingsWindow | None = None
        if w == self.button_randomize_personality_quiz:

            def on_change_quiz_active(active):
                self._suppress_signals = True
                self.row_personality_quiz.set_active(active)
                page1_pp_qs.set_sensitive(active)
                self._suppress_signals = False

            page1_pp = PersonalityQuizPage(
                parent_page=self,
                on_change_quiz_active=on_change_quiz_active,
            )
            page1_pp_qs = PersonalityQuizQuestionsPage(
                navigation_view=None, sensitive=self.row_personality_quiz.get_active()
            )
            dialog = BaseSettingsDialog(
                title=self.row_personality_quiz.get_title(),
                content=(
                    SubpageStackEntry(
                        child=page1_pp,
                        name="settings",
                        title=_("Settings"),
                        icon_name="skytemple-e-actor-symbolic",
                    ),
                    SubpageStackEntry(
                        child=page1_pp_qs,
                        name="questions",
                        title=_("Questions"),
                        icon_name="skytemple-e-actor-symbolic",
                    ),
                ),
                end_button_factory=page1_pp_qs.create_window_end_buttons,
                content_width=512,
            )
            page1_pp_qs.navigation_view = cast(BaseSettingsDialog, dialog).navigation_view
        if w == self.button_randomize_location_names:
            dialog = self._make_location_names_dialog()
        if w == self.button_randomize_chapter_titles:
            page_ct = TextPoolPage(pool=TextPool.CHAPTER_TITLES, parent_page=self)
            dialog = BaseSettingsDialog(
                title=self.row_chapter_titles.get_title(),
                content=page_ct,
                getter=page_ct.get_enabled,
                setter=page_ct.set_enabled,
                end_button_factory=page_ct.create_window_end_buttons,
                content_width=512,
            )

        if dialog is not None:
            frontend = GtkFrontend.instance()
            dialog.populate_settings(frontend.randomization_settings)
            dialog.present(frontend.window)
            return False

    @Gtk.Template.Callback()
    def on_row_personality_quiz_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["quiz"]["randomize"] = self.row_personality_quiz.get_active()

    @Gtk.Template.Callback()
    def on_row_location_names_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["locations"]["randomize"] = self.row_location_names.get_active()

    @Gtk.Template.Callback()
    def on_row_chapter_titles_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["chapters"]["randomize"] = self.row_chapter_titles.get_active()

    @Gtk.Template.Callback()
    def on_row_randomize_main_text_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["text"]["main"] = self.row_randomize_main_text.get_active()

    @Gtk.Template.Callback()
    def on_row_randomize_story_dialogue_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["text"]["story"] = self.row_randomize_story_dialogue.get_active()

    @Gtk.Template.Callback()
    def on_row_enable_instant_text_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["text"]["instant"] = self.row_enable_instant_text.get_active()

    @Gtk.Template.Callback()
    def on_row_text_replacement_algorithm_notify_selected(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["starters_npcs"]["npcs_use_smart_replace"] = (
            self.row_text_replacement_algorithm.get_selected() == 0
        )

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config
        self.row_personality_quiz.set_active(config["quiz"]["randomize"])
        self.row_location_names.set_active(config["locations"]["randomize"])
        self.row_chapter_titles.set_active(config["chapters"]["randomize"])
        self.row_randomize_main_text.set_active(config["text"]["main"])
        self.row_randomize_story_dialogue.set_active(config["text"]["story"])
        self.row_enable_instant_text.set_active(config["text"]["instant"])
        replacement_algo = 0 if self.randomization_settings["starters_npcs"]["npcs_use_smart_replace"] else 1
        self.row_text_replacement_algorithm.set_selected(replacement_algo)
        self._suppress_signals = False

        # The JP ROM does not support these yet:
        if GtkFrontend.instance().input_rom_static_data.game_region == GAME_REGION_JP:
            self.group_full_text_randomization.hide()
        else:
            self.group_full_text_randomization.show()

    def _make_location_names_dialog(self):
        dialog = None

        page1_ln = TextPoolPage(pool=TextPool.LOCATIONS_A, parent_page=self)
        page2_ln = TextPoolPage(pool=TextPool.LOCATIONS_B, parent_page=self)

        def on_button_import_clicked(*args):
            assert dialog is not None
            active = dialog.get_active_page()
            if active is None:
                return
            active_c = cast(TextPoolPage, active)
            active_c.on_button_import_clicked()

        def on_button_export_clicked(*args):
            assert dialog is not None
            active = dialog.get_active_page()
            if active is None:
                return
            active_c = cast(TextPoolPage, active)
            active_c.on_button_export_clicked()

        def end_button_factory():
            button_import, button_export, w = TextPoolPage.raw_create_window_end_buttons()
            button_import.connect("clicked", on_button_import_clicked)
            button_export.connect("clicked", on_button_export_clicked)
            return w

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
            end_button_factory=end_button_factory,
        )
        return dialog
