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

from skytemple_randomizer.frontend.gtk.widgets import (
    BaseSettingsDialog,
    ItemsCategoriesDialog,
    ExplorerRankPage,
    MusicPage,
    PatchesPage,
    RandomizationSettingsWindow,
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

    @Gtk.Template.Callback()
    def on_signal_for_dialog(self, w: Gtk.Widget, *args):
        dialog: RandomizationSettingsWindow | None = None
        if w == self.row_item_pool:
            dialog = ItemsCategoriesDialog(
                title=_("Item Pool"),
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
            width, height = frontend.window.get_default_size()
            dialog.set_default_size(round(width * 0.8), round(height * 0.8))
            dialog.populate_settings(frontend.randomization_settings)
            dialog.set_transient_for(frontend.window)
            dialog.set_application(frontend.application)
            dialog.present()
            return False

    @Gtk.Template.Callback()
    def on_row_item_randomization_algorithm_notify_selected(*args):
        pass

    @Gtk.Template.Callback()
    def on_row_randomize_global_items_notify_active(*args):
        pass

    @Gtk.Template.Callback()
    def on_row_download_sprites_notify_active(self, *args):
        pass

    def populate_settings(self, config: RandomizerConfig):
        pass
