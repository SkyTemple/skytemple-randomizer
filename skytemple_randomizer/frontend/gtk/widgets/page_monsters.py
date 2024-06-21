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
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.widgets import (
    BaseSettingsDialog,
    MonstersAbilitiesPage,
    MovesetsPage,
    TacticsIqPage,
    MonstersPoolPage,
    MonstersPoolType,
    RandomizationSettingsWindow,
    TextPoolPage,
    TextPool,
)
from skytemple_randomizer.frontend.gtk.widgets.page_moves_pool import MovesPoolPage


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_monsters.ui"))
class MonstersPage(Adw.PreferencesPage):
    __gtype_name__ = "StMonstersPage"
    row_allowed_monsters = cast(Adw.ActionRow, Gtk.Template.Child())
    row_randomize_starters = cast(Adw.SwitchRow, Gtk.Template.Child())
    button_randomize_starters = cast(Gtk.Button, Gtk.Template.Child())
    row_randomize_npcs = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_randomize_abilities = cast(Adw.SwitchRow, Gtk.Template.Child())
    button_randomize_abilities = cast(Gtk.Button, Gtk.Template.Child())
    row_randomize_movesets = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_randomize_tms_hms = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_randomize_typings = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_tactics_iq = cast(Adw.ActionRow, Gtk.Template.Child())
    row_move_pool = cast(Adw.ActionRow, Gtk.Template.Child())
    row_blind_moves = cast(Adw.SwitchRow, Gtk.Template.Child())
    button_blind_moves = cast(Adw.SwitchRow, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    _suppress_signals: bool

    @Gtk.Template.Callback()
    def on_signal_for_dialog(self, w: Gtk.Widget, *args):
        dialog: RandomizationSettingsWindow | None = None
        if w == self.row_randomize_movesets:
            page_mo = MovesetsPage(parent_page=self)
            dialog = BaseSettingsDialog(
                title=self.row_randomize_movesets.get_title(),
                content=page_mo,
                content_width=512,
            )
        if w == self.row_move_pool:
            page_mop = MovesPoolPage(parent_page=self)
            dialog = BaseSettingsDialog(
                title=self.row_move_pool.get_title(),
                content=page_mop,
                search_callback=page_mop.on_search_changed,
                help_callback=page_mop.help_pool,
            )
        if w == self.row_allowed_monsters:
            page_am = MonstersPoolPage(type=MonstersPoolType.ALL, parent_page=self)
            dialog = BaseSettingsDialog(
                title=self.row_allowed_monsters.get_title(),
                content=page_am,
                help_callback=page_am.help_pool_all,
                search_callback=page_am.on_search_changed,
                end_button_factory=page_am.create_window_end_buttons,
            )
        if w == self.button_randomize_starters:
            page_pl = MonstersPoolPage(type=MonstersPoolType.STARTERS, parent_page=self)
            dialog = BaseSettingsDialog(
                title=self.row_randomize_starters.get_title(),
                content=page_pl,
                getter=page_pl.get_enabled,
                setter=page_pl.set_enabled,
                help_callback=page_pl.help_pool_starters,
                search_callback=page_pl.on_search_changed,
                end_button_factory=page_pl.create_window_end_buttons,
            )
        if w == self.button_randomize_abilities:
            page_ab = MonstersAbilitiesPage(parent_page=self)
            dialog = BaseSettingsDialog(
                title=self.row_randomize_abilities.get_title(),
                content=page_ab,
                search_callback=page_ab.on_search_changed,
                getter=page_ab.get_enabled,
                setter=page_ab.set_enabled,
            )
        if w == self.row_tactics_iq:
            dialog = BaseSettingsDialog(
                title=_("Tactics & IQ"),
                content=TacticsIqPage(),
                content_width=512,
            )
        if w == self.button_blind_moves:
            page_bt = TextPoolPage(pool=TextPool.BLIND_MOVE_NAMES, parent_page=self)
            dialog = BaseSettingsDialog(
                title=_('Move Names for "Blind Moves" Mode'),
                content=page_bt,
                getter=page_bt.get_enabled,
                setter=page_bt.set_enabled,
                end_button_factory=page_bt.create_window_end_buttons,
                help_callback=_("A lot of names from the default list are from fantasynamegenerators.com."),
                content_width=512,
            )

        if dialog is not None:
            frontend = GtkFrontend.instance()
            dialog.populate_settings(frontend.randomization_settings)
            dialog.present(frontend.window)
            return False

    @Gtk.Template.Callback()
    def on_row_randomize_starters_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["starters_npcs"]["starters"] = self.row_randomize_starters.get_active()

    @Gtk.Template.Callback()
    def on_row_randomize_npcs_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["starters_npcs"]["npcs"] = self.row_randomize_npcs.get_active()

    @Gtk.Template.Callback()
    def on_row_randomize_abilities_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["pokemon"]["abilities"] = self.row_randomize_abilities.get_active()

    @Gtk.Template.Callback()
    def on_row_randomize_typings_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["pokemon"]["typings"] = self.row_randomize_typings.get_active()

    @Gtk.Template.Callback()
    def on_row_randomize_tms_hms_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["pokemon"]["tms_hms"] = self.row_randomize_tms_hms.get_active()

    @Gtk.Template.Callback()
    def on_row_blind_moves_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["pokemon"]["blind_moves"]["enable"] = self.row_blind_moves.get_active()

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config
        self.row_randomize_starters.set_active(config["starters_npcs"]["starters"])
        self.row_randomize_npcs.set_active(config["starters_npcs"]["npcs"])
        self.row_randomize_abilities.set_active(config["pokemon"]["abilities"])
        self.row_randomize_typings.set_active(config["pokemon"]["typings"])
        self.row_blind_moves.set_active(config["pokemon"]["blind_moves"]["enable"])
        self._suppress_signals = False
