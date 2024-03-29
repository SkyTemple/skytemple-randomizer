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

from skytemple_randomizer.config import RandomizerConfig, ItemAlgorithm
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.ui_util import set_default_dialog_size
from skytemple_randomizer.frontend.gtk.widgets import (
    BaseSettingsDialog,
    ItemsCategoriesPage,
    ExplorerRankPage,
    MusicPage,
    PatchesPage,
    RandomizationSettingsWindow,
    ItemsPage,
    SubpageStackEntry,
)


@Gtk.Template(filename=os.path.join(MAIN_PATH, "page_tweaks.ui"))
class TweaksPage(Adw.PreferencesPage):
    __gtype_name__ = "StTweaksPage"
    row_item_randomization_algorithm = cast(Adw.ComboRow, Gtk.Template.Child())
    row_randomize_global_items = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_item_pool = cast(Adw.ActionRow, Gtk.Template.Child())
    row_download_sprites = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_patches = cast(Adw.ActionRow, Gtk.Template.Child())
    row_music = cast(Adw.ActionRow, Gtk.Template.Child())
    row_explorer_rank = cast(Adw.ActionRow, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    _suppress_signals: bool

    @Gtk.Template.Callback()
    def on_signal_for_dialog(self, w: Gtk.Widget, *args):
        dialog: RandomizationSettingsWindow | None = None
        if w == self.row_item_pool:
            page_it = ItemsPage()
            page_it_cat = ItemsCategoriesPage()
            dialog = BaseSettingsDialog(
                title=_("Allowed Items"),
                content=(
                    SubpageStackEntry(
                        child=page_it,
                        name="items",
                        title=_("Allowed Items"),
                        icon_name="skytemple-e-item-symbolic",
                    ),
                    SubpageStackEntry(
                        child=page_it_cat,
                        name="items_categories",
                        title=_("Category Weights"),
                        icon_name="skytemple-e-item-symbolic",
                    ),
                ),
            )
        if w == self.row_patches:
            dialog = BaseSettingsDialog(
                title=self.row_patches.get_title(),
                content=PatchesPage(),
            )
        if w == self.row_music:
            dialog = BaseSettingsDialog(
                title=self.row_music.get_title(),
                content=MusicPage(),
            )
        if w == self.row_explorer_rank:
            dialog = BaseSettingsDialog(
                title=self.row_explorer_rank.get_title(),
                content=ExplorerRankPage(),
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
    def on_row_item_randomization_algorithm_notify_selected(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["item"]["algorithm"] = ItemAlgorithm(
            self.row_item_randomization_algorithm.get_selected()
        )

    @Gtk.Template.Callback()
    def on_row_randomize_global_items_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["item"]["global_items"] = (
            self.row_randomize_global_items.get_active()
        )

    @Gtk.Template.Callback()
    def on_row_download_sprites_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["improvements"]["download_portraits"] = (
            self.row_download_sprites.get_active()
        )

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config
        self.row_item_randomization_algorithm.set_selected(
            config["item"]["algorithm"].value
        )
        self.row_randomize_global_items.set_active(config["item"]["global_items"])
        self.row_download_sprites.set_active(
            config["improvements"]["download_portraits"]
        )
        self._suppress_signals = False
