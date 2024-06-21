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
from functools import partial
from typing import cast

from skytemple_files.common.i18n_util import _
from skytemple_files.common.util import open_utf8

from skytemple_randomizer.config import RandomizerConfig, QuizQuestion
from skytemple_randomizer.export_quiz_xml import (
    export_personality_quiz_xml,
    import_personality_quiz_xml,
)
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.hacks import force_adw_entry_row_no_title
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, GLib, Gio

from skytemple_randomizer.frontend.gtk.widgets.base_dialog_settings import MAIN_PAGE_TAG


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_personality_quiz_questions.ui"))
class PersonalityQuizQuestionsPage(Adw.PreferencesPage):
    __gtype_name__ = "StPersonalityQuizQuestionsPage"
    pool_list = cast(Gtk.ListBox, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    navigation_view: Adw.NavigationView | None
    _suppress_signals: bool

    def __init__(
        self,
        navigation_view: Adw.NavigationView | None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.randomization_settings = None
        self.navigation_view = navigation_view
        self._suppress_signals = False

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config

        self.reload()

        self._suppress_signals = False

    def reload(self):
        if self.randomization_settings is not None:
            self.pool_list.remove_all()
            for i, question in enumerate(self.randomization_settings["quiz"]["questions"]):
                row = self._make_row(question)
                self.pool_list.append(row)

    def _make_row(self, question: QuizQuestion):
        def on_activated(*args):
            if self.randomization_settings is not None:
                settings_for_question = self._make_settings_page(
                    row.get_index(),
                    self.randomization_settings["quiz"]["questions"][row.get_index()],
                    row,
                )
                if self.navigation_view is not None:
                    self.navigation_view.push(settings_for_question)

        row = Adw.ActionRow(title=question["question"], activatable=True)
        row.connect("activated", on_activated)
        img = Gtk.Image(icon_name="go-next-symbolic")
        img.add_css_class("dim-label")
        row.add_suffix(img)
        return row

    def _make_settings_page(self, i, question: QuizQuestion, question_row: Adw.ActionRow):
        page = Adw.NavigationPage(title=_("Edit Question"))
        toolbar_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        content_page = Adw.PreferencesPage()
        question_group = Adw.PreferencesGroup()
        question_remove_button = self._make_remove_question_button(i, question_row)

        def on_question_text_changed(*args):
            contents = text.get_buffer().get_text(
                text.get_buffer().get_start_iter(),
                text.get_buffer().get_end_iter(),
                False,
            )
            if self.randomization_settings is not None:
                self.randomization_settings["quiz"]["questions"][i]["question"] = contents
            question_row.set_title(contents)

        def on_question_state_flags_changed(e: Gtk.Widget, flags: Gtk.StateFlags):
            focused = not not (flags & Gtk.StateFlags.FOCUSED)
            if focused:
                question_preference_row.add_css_class("skytemple-randomizer--row-focused")
            else:
                question_preference_row.remove_css_class("skytemple-randomizer--row-focused")

            # Sometimes this event is not called for TextView when focused is lost. This is an awful
            # hack, but we poll every 100ms to see if maybe the focus did move away:
            def did_move_away():
                focused = not not (e.get_state_flags() & Gtk.StateFlags.FOCUSED)
                if not focused:
                    question_preference_row.remove_css_class("skytemple-randomizer--row-focused")
                    return False
                return True

            GLib.timeout_add(100, did_move_away)

        question_preference_row = Adw.PreferencesRow()
        question_element = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            margin_start=10,
            margin_end=10,
            margin_top=5,
            margin_bottom=5,
        )
        label = Gtk.Label(label=_("Question"), halign=Gtk.Align.START)
        label.add_css_class("subtitle")
        question_element.append(label)
        text = Gtk.TextView(buffer=Gtk.TextBuffer(text=question["question"]), accepts_tab=False)
        text.add_css_class("skytemple-randomizer__text-view-as-row")
        text.get_buffer().connect("changed", on_question_text_changed)
        question_element.append(text)
        text.connect(
            "state_flags_changed",
            on_question_state_flags_changed,
        )
        question_preference_row.set_child(question_element)
        question_group.add(question_preference_row)

        answers_group = Adw.PreferencesGroup(title=_("Answers"))
        add_button = self._make_add_answer_button(i, answers_group)
        answers_group.set_header_suffix(add_button)

        for answer in question["answers"]:
            row_answer = Adw.EntryRow(title=_("Answer"))
            force_adw_entry_row_no_title(row_answer)
            row_answer.set_text(answer)
            row_answer.connect("changed", partial(self._on_answer_changed, i))
            remove_button = self._make_remove_answer_button(i, answers_group, row_answer)
            row_answer.add_suffix(remove_button)
            answers_group.add(row_answer)

        header.pack_end(question_remove_button)
        toolbar_view.add_top_bar(header)
        content_page.add(question_group)
        content_page.add(answers_group)
        toolbar_view.set_content(content_page)
        page.set_child(toolbar_view)

        # sometimes small bug with rendering text
        def fix_text():
            question_element.queue_resize()
            question_element.queue_draw()
            return False

        GLib.timeout_add(100, fix_text)

        return page

    @Gtk.Template.Callback()
    def on_button_add_question_clicked(self, *args):
        if self.randomization_settings is None:
            return
        i = len(self.randomization_settings["quiz"]["questions"])
        question: QuizQuestion = {
            "question": "",
            "answers": [],
        }
        row = self._make_row(question)
        self.pool_list.append(row)
        self.pool_list.select_row(row)
        settings_for_question = self._make_settings_page(i, question, row)
        if self.navigation_view is not None:
            self.navigation_view.push(settings_for_question)
        self.randomization_settings["quiz"]["questions"].append(question)

    def _make_remove_question_button(self, i: int, question_row: Adw.ActionRow) -> Gtk.Button:
        def on_clicked(*args):
            self.pool_list.remove(question_row)
            if self.navigation_view:
                self.navigation_view.pop()
            if self.randomization_settings is not None:
                del self.randomization_settings["quiz"]["questions"][i]

        button = Gtk.Button(
            icon_name="skytemple-edit-delete-symbolic",
            tooltip_text=_("Remove Question"),
        )
        button.connect("clicked", on_clicked)
        return button

    def _make_add_answer_button(self, question_i: int, group_answers: Adw.PreferencesGroup) -> Gtk.Button:
        def on_clicked(*args):
            row_answer = Adw.EntryRow(title=_("Answer"))
            force_adw_entry_row_no_title(row_answer)
            remove_button = self._make_remove_answer_button(question_i, group_answers, row_answer)
            row_answer.add_suffix(remove_button)
            row_answer.grab_focus()
            row_answer.connect("changed", partial(self._on_answer_changed, question_i))
            group_answers.add(row_answer)
            if self.randomization_settings is not None:
                self.randomization_settings["quiz"]["questions"][question_i]["answers"].append("")

        button = Gtk.Button(icon_name="skytemple-list-add-symbolic", tooltip_text=_("Add Answer"))
        button.add_css_class("flat")
        button.connect("clicked", on_clicked)
        return button

    def _make_remove_answer_button(
        self,
        question_i: int,
        group_answers: Adw.PreferencesGroup,
        row_answer: Adw.EntryRow,
    ) -> Gtk.Button:
        def on_clicked(*args):
            index = row_answer.get_index()
            group_answers.remove(row_answer)
            if self.randomization_settings is not None:
                del self.randomization_settings["quiz"]["questions"][question_i]["answers"][index]

        button = Gtk.Button(icon_name="skytemple-list-remove-symbolic", tooltip_text=_("Remove Answer"))
        button.add_css_class("flat")
        button.connect("clicked", on_clicked)
        return button

    def _on_answer_changed(self, question_i: int, row: Adw.EntryRow):
        answer_index = row.get_index()
        if self.randomization_settings is not None:
            self.randomization_settings["quiz"]["questions"][question_i]["answers"][answer_index] = row.get_text()

    def on_button_import_clicked(self, *args):
        frontend = GtkFrontend.instance()
        csv_filter = Gtk.FileFilter()
        csv_filter.add_suffix("xml")
        csv_filter.add_mime_type("text/xml")
        documents_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if documents_dir is not None:
            default_dir = Gio.File.new_for_path(documents_dir)
            dialog_for_file = Gtk.FileDialog(initial_folder=default_dir, default_filter=csv_filter)

        else:
            dialog_for_file = Gtk.FileDialog(default_filter=csv_filter)
        dialog_for_file.open(frontend.window, None, self.on_import_file_loaded)

    def on_import_file_loaded(self, dialog, result):
        try:
            file: Gio.File = dialog.open_finish(result)
        except Exception as e:
            if not isinstance(e, GLib.GError) or "dismissed" not in str(e).lower():
                GtkFrontend.instance().display_error(
                    _("Failed to import: Error while opening file ({}).").format(e),
                    cast(Gtk.Window, self.get_root()),
                )
            return

        path = file.get_path()
        assert path is not None
        assert self.randomization_settings is not None

        try:
            with open_utf8(path) as xml_file:
                if self.navigation_view:
                    self.navigation_view.pop_to_tag(MAIN_PAGE_TAG)
                self.randomization_settings["quiz"]["questions"] = import_personality_quiz_xml(xml_file)
                self.reload()
        except Exception as e:
            GtkFrontend.instance().display_error(
                _(
                    "Failed to import. Make sure your XML matches the same format as with the export button. Details: {}"
                ).format(e),
                cast(Gtk.Window, self.get_root()),
            )

    def on_button_export_clicked(self, *args):
        frontend = GtkFrontend.instance()
        csv_filter = Gtk.FileFilter()
        csv_filter.add_suffix("xml")
        csv_filter.add_mime_type("text/xml")
        documents_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if documents_dir is not None:
            default_dir = Gio.File.new_for_path(documents_dir)
            dialog_for_file = Gtk.FileDialog(
                initial_folder=default_dir,
                default_filter=csv_filter,
                initial_name="personality_quiz_questions.xml",
            )
        else:
            dialog_for_file = Gtk.FileDialog(default_filter=csv_filter, initial_name="personality_quiz_questions.xml")
        dialog_for_file.save(frontend.window, None, self.on_export_file_saved)

    def on_export_file_saved(self, dialog, result):
        frontend = GtkFrontend.instance()
        try:
            file = dialog.save_finish(result)
        except Exception as e:
            if not isinstance(e, GLib.GError) or "dismissed" not in str(e).lower():
                frontend.display_error(
                    _("Failed to export: Error while opening file ({}).").format(e),
                    cast(Gtk.Window, self.get_root()),
                )
            return

        path = file.get_path()
        assert path is not None
        assert self.randomization_settings is not None

        try:
            with open_utf8(path, "w", newline="") as xml_file:
                export_personality_quiz_xml(self.randomization_settings["quiz"]["questions"], xml_file)
        except Exception as e:
            GtkFrontend.instance().display_error(
                _("Failed to export. Details: {}").format(e),
                cast(Gtk.Window, self.get_root()),
            )

    def create_window_end_buttons(self) -> Gtk.Widget:
        box = Gtk.Box(spacing=5)
        button_import = Gtk.Button(
            icon_name="skytemple-import-symbolic",
            tooltip_text=_("Import questions from XML"),
        )
        button_import.connect("clicked", self.on_button_import_clicked)
        button_export = Gtk.Button(
            icon_name="skytemple-export-symbolic",
            tooltip_text=_("Export questions to XML"),
        )
        button_export.connect("clicked", self.on_button_export_clicked)
        box.append(button_import)
        box.append(button_export)
        return box
