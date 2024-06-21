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
from typing import cast, Union

from skytemple_files.common.i18n_util import _

from skytemple_randomizer.config import RandomizerConfig, ItemAlgorithm
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.widgets import (
    BaseSettingsDialog,
    ItemsCategoriesPage,
    ExplorerRankPage,
    MusicPage,
    PatchesPage,
    RandomizationSettingsWindow,
    ItemsPage,
    SubpageStackEntry,
    TextPoolPage,
    TextPool,
)


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_tweaks.ui"))
class TweaksPage(Adw.PreferencesPage):
    __gtype_name__ = "StTweaksPage"
    row_item_randomization_algorithm = cast(Adw.ComboRow, Gtk.Template.Child())
    row_randomize_global_items = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_item_pool = cast(Adw.ActionRow, Gtk.Template.Child())
    row_download_sprites = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_patches = cast(Adw.ActionRow, Gtk.Template.Child())
    row_music = cast(Adw.ActionRow, Gtk.Template.Child())
    row_explorer_rank = cast(Adw.ActionRow, Gtk.Template.Child())
    row_blind_items = cast(Adw.SwitchRow, Gtk.Template.Child())
    button_blind_items = cast(Adw.SwitchRow, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    _suppress_signals: bool

    @Gtk.Template.Callback()
    def on_signal_for_dialog(self, w: Gtk.Widget, *args):
        dialog: RandomizationSettingsWindow | None = None
        if w == self.row_item_pool:
            dialog = self._make_item_pool_dialogs()
        if w == self.row_patches:
            dialog = BaseSettingsDialog(
                title=self.row_patches.get_title(),
                content=PatchesPage(),
                content_width=512,
            )
        if w == self.row_music:
            page_mu = MusicPage()
            dialog = BaseSettingsDialog(
                title=self.row_music.get_title(),
                content=page_mu,
                help_callback=page_mu.help_text,
                content_width=512,
            )
        if w == self.row_explorer_rank:
            dialog = BaseSettingsDialog(
                title=self.row_explorer_rank.get_title(),
                content=ExplorerRankPage(),
                content_width=512,
            )
        if w == self.button_blind_items:
            page_bt = TextPoolPage(pool=TextPool.BLIND_ITEM_NAMES, parent_page=self)
            dialog = BaseSettingsDialog(
                title=_('Item Names for "Blind Items" Mode'),
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
        self.randomization_settings["item"]["global_items"] = self.row_randomize_global_items.get_active()

    @Gtk.Template.Callback()
    def on_row_download_sprites_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["improvements"]["download_portraits"] = self.row_download_sprites.get_active()

    @Gtk.Template.Callback()
    def on_row_blind_items_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["item"]["blind_items"]["enable"] = self.row_blind_items.get_active()

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config
        self.row_item_randomization_algorithm.set_selected(config["item"]["algorithm"].value)
        self.row_randomize_global_items.set_active(config["item"]["global_items"])
        self.row_download_sprites.set_active(config["improvements"]["download_portraits"])
        self.row_blind_items.set_active(config["item"]["blind_items"]["enable"])
        self._suppress_signals = False

    def _make_item_pool_dialogs(self) -> BaseSettingsDialog:
        dialog = None

        def on_button_reset_clicked(*args):
            assert dialog is not None
            active = dialog.get_active_page()
            if active is None:
                return
            active_c = cast(Union[ItemsPage, ItemsCategoriesPage], active)
            active_c.on_button_reset_clicked()

        def on_button_none_clicked(*args):
            assert dialog is not None
            active = dialog.get_active_page()
            if active is None:
                return
            active_c = cast(Union[ItemsPage, ItemsCategoriesPage], active)
            active_c.on_button_none_clicked()

        def on_stack_switch_page(new_page: Gtk.Widget):
            assert dialog is not None
            new_page_c = cast(Union[ItemsPage, ItemsCategoriesPage], new_page)
            dialog.set_help_popover_text(new_page_c.help_pool())

        def end_button_factory() -> Gtk.Widget:
            box = Gtk.Box(spacing=5)
            button_reset = Gtk.Button(
                icon_name="skytemple-view-refresh-symbolic",
                tooltip_text=_("Reset to Default"),
            )
            button_reset.connect("clicked", on_button_reset_clicked)
            button_none = Gtk.Button(
                icon_name="skytemple-edit-delete-symbolic",
                tooltip_text=_("Select None"),
            )
            button_none.connect("clicked", on_button_none_clicked)
            box.append(button_reset)
            box.append(button_none)
            return box

        page_it = ItemsPage(parent_page=self)
        page_it_cat = ItemsCategoriesPage(parent_page=self)
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
            search_callback=page_it.on_search_changed,
            help_callback=page_it.help_pool,
            end_button_factory=end_button_factory,
        )
        dialog.connect_on_stack_switch_signal(on_stack_switch_page)
        return dialog
