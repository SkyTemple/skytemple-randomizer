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
from threading import Thread
from typing import cast

from skytemple_files.common.i18n_util import _
from skytemple_files.common.util import get_binary_from_rom
from skytemple_files.hardcoded.dungeons import HardcodedDungeons

from skytemple_randomizer.config import RandomizerConfig, DungeonSettingsConfig
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, GLib

from skytemple_randomizer.string_provider import StringProvider, StringType
from skytemple_randomizer.frontend.gtk.widgets import DungeonsSettingsPage


@Gtk.Template(filename=os.path.join(MAIN_PATH, "page_dungeons_individual_settings.ui"))
class DungeonsIndividualSettingsPage(Adw.PreferencesPage):
    __gtype_name__ = "StDungeonsIndividualSettingsPage"

    stack = cast(Gtk.Stack, Gtk.Template.Child())
    spinner = cast(Gtk.Spinner, Gtk.Template.Child())
    pool_list = cast(Gtk.ListBox, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    parent_page: DungeonsSettingsPage
    search_text: str
    rows: dict[int, Adw.ExpanderRow]
    _suppress_signals: bool

    def __init__(
        self,
        *args,
        parent_page: DungeonsSettingsPage,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parent_page = parent_page
        self.randomization_settings = None
        self.search_text = ""
        self.rows = {}
        self._suppress_signals = False

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config

        frontend = GtkFrontend.instance()
        rom = frontend.input_rom
        static_data = frontend.input_rom_static_data

        dungeons: dict[int, tuple[DungeonSettingsConfig, str, str]] = {}
        configs = config["dungeons"]["settings"]

        def load_thread():
            string_provider = StringProvider(rom, frontend.input_rom_static_data)

            dungeon_list = HardcodedDungeons.get_dungeon_list(
                get_binary_from_rom(rom, static_data.bin_sections.arm9),
                static_data,
            )

            for i, dungeon in enumerate(dungeon_list):
                dungeons[i] = (
                    self._get_or_default(configs, i),
                    string_provider.get_value(StringType.DUNGEON_NAMES_MAIN, i),
                    string_provider.get_value(StringType.DUNGEON_NAMES_SELECTION, i),
                )

            GLib.idle_add(finish_load)

        def finish_load():
            for i, (config, name1, name2) in dungeons.items():
                row = self._make_row(i, config, name1, name2)
                self.pool_list.append(row)
                self.rows[i] = row
            self._suppress_signals = False
            self.stack.set_visible_child(self.pool_list)

        self.pool_list.set_filter_func(self.pool_filter)

        Thread(target=load_thread).start()

    def on_search_changed(self, search_entry: Gtk.SearchEntry):
        if self._suppress_signals:
            return
        self.search_text = search_entry.get_text().strip().lower()
        self.pool_list.invalidate_filter()

    def help_pool(self, *args) -> str:
        return _(
            "Here you can decide which dungeons you want to have affected by the randomization and whether or "
            "randomize weather or not.\nYou can also disable Monster Houses for dungeons (recommended for early "
            "game). Additionally you can force dungeons to be unlocked.\nPlease note that entering story dungeons "
            "prematurely can mess with the game's story progression."
        )

    def pool_filter(self, row: Adw.SwitchRow):
        if self.search_text == "":
            match = True
        else:
            match = (
                self.search_text in f"{row.get_title()} {row.get_subtitle()}".lower()
            )
        return match

    @staticmethod
    def _get_or_default(
        configs: dict[int, DungeonSettingsConfig], i: int
    ) -> DungeonSettingsConfig:
        if i not in configs:
            configs[i] = {
                "randomize": False,
                "unlock": False,
                "randomize_weather": False,
                "monster_houses": False,
                "enemy_iq": False,
            }
        return configs[i]

    def on_row_randomize_notify_active(
        self, idx: int, switch_row: Adw.SwitchRow, *args
    ):
        if self.randomization_settings is None or self._suppress_signals:
            return
        self.randomization_settings["dungeons"]["settings"][idx]["randomize"] = (
            switch_row.get_active()
        )

    def on_row_randomize_weather_notify_active(
        self, idx: int, switch_row: Adw.SwitchRow, *args
    ):
        if self.randomization_settings is None or self._suppress_signals:
            return
        self.randomization_settings["dungeons"]["settings"][idx][
            "randomize_weather"
        ] = switch_row.get_active()

    def on_row_monster_houses_notify_active(
        self, idx: int, switch_row: Adw.SwitchRow, *args
    ):
        if self.randomization_settings is None or self._suppress_signals:
            return
        self.randomization_settings["dungeons"]["settings"][idx]["monster_houses"] = (
            switch_row.get_active()
        )

    def on_row_enemy_iq_notify_active(self, idx: int, switch_row: Adw.SwitchRow, *args):
        if self.randomization_settings is None or self._suppress_signals:
            return
        self.randomization_settings["dungeons"]["settings"][idx]["enemy_iq"] = (
            switch_row.get_active()
        )

    def on_row_unlock_notify_active(self, idx: int, switch_row: Adw.SwitchRow, *args):
        if self.randomization_settings is None or self._suppress_signals:
            return
        self.randomization_settings["dungeons"]["settings"][idx]["unlock"] = (
            switch_row.get_active()
        )

    def _make_row(self, i: int, config: DungeonSettingsConfig, name1: str, name2: str):
        row = Adw.ExpanderRow(title=name1, subtitle=f"{name2} #{i:03}")

        row_randomize = Adw.SwitchRow(title=_("Randomize"), active=config["randomize"])
        row_randomize.connect(
            "notify::active", partial(self.on_row_randomize_notify_active, i)
        )
        row.add_row(row_randomize)

        row_randomize_weather = Adw.SwitchRow(
            title=_("Randomize Weather"), active=config["randomize_weather"]
        )
        row_randomize_weather.connect(
            "notify::active", partial(self.on_row_randomize_weather_notify_active, i)
        )
        row.add_row(row_randomize_weather)

        row_monster_houses = Adw.SwitchRow(
            title=_("Spawn Monster Houses"), active=config["monster_houses"]
        )
        row_monster_houses.connect(
            "notify::active", partial(self.on_row_monster_houses_notify_active, i)
        )
        row.add_row(row_monster_houses)

        row_enemy_iq = Adw.SwitchRow(title=_("Randomize IQ"), active=config["enemy_iq"])
        row_enemy_iq.connect(
            "notify::active", partial(self.on_row_enemy_iq_notify_active, i)
        )
        row.add_row(row_enemy_iq)

        row_unlock = Adw.SwitchRow(title=_("Unlock at Start"), active=config["unlock"])
        row_unlock.connect(
            "notify::active", partial(self.on_row_unlock_notify_active, i)
        )
        row.add_row(row_unlock)

        return row
