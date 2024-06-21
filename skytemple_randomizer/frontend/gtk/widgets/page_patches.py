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
from skytemple_files.patch.handler.disarm_one_room_mh import DisarmOneRoomMHPatchHandler
from skytemple_files.patch.handler.fix_memory_softlock import (
    FixMemorySoftlockPatchHandler,
)
from skytemple_files.patch.handler.move_shortcuts import MoveShortcutsPatch
from skytemple_files.patch.handler.unused_dungeon_chance import UnusedDungeonChancePatch

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.widgets import HelpPopover


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "page_patches.ui"))
class PatchesPage(Adw.PreferencesPage):
    __gtype_name__ = "StPatchesPage"
    row_patch_moveshortcuts = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_patch_unuseddungeonchance = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_patch_totalteamcontrol = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_patch_disarm_monster_houses = cast(Adw.SwitchRow, Gtk.Template.Child())
    row_patch_fixmemorysoftlock = cast(Adw.SwitchRow, Gtk.Template.Child())
    help_popover_patch_moveshortcuts = cast(HelpPopover, Gtk.Template.Child())
    help_popover_patch_unuseddungeonchance = cast(HelpPopover, Gtk.Template.Child())
    help_popover_patch_totalteamcontrol = cast(HelpPopover, Gtk.Template.Child())
    help_popover_patch_disarm_monster_houses = cast(HelpPopover, Gtk.Template.Child())
    help_popover_patch_fixmemorysoftlock = cast(HelpPopover, Gtk.Template.Child())

    randomization_settings: RandomizerConfig | None
    _suppress_signals: bool

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.randomization_settings = None
        self._suppress_signals = False

    def populate_settings(self, config: RandomizerConfig):
        self._suppress_signals = True
        self.randomization_settings = config

        self.row_patch_moveshortcuts.set_active(config["improvements"]["patch_moveshortcuts"])
        self.row_patch_unuseddungeonchance.set_active(config["improvements"]["patch_unuseddungeonchance"])
        self.row_patch_totalteamcontrol.set_active(config["improvements"]["patch_totalteamcontrol"])
        self.row_patch_disarm_monster_houses.set_active(config["improvements"]["patch_disarm_monster_houses"])
        self.row_patch_fixmemorysoftlock.set_active(config["improvements"]["patch_fixmemorysoftlock"])

        move_shortcut_patch = MoveShortcutsPatch()
        unused_dungeon_patch = UnusedDungeonChancePatch()
        disarm_one_room_mh_patch = DisarmOneRoomMHPatchHandler()
        fix_memory_softlock_patch = FixMemorySoftlockPatchHandler()

        self.help_popover_patch_moveshortcuts.set_property(
            "label",
            _("Installs the patch '{}' by {}:\n{}").format(
                move_shortcut_patch.name,
                move_shortcut_patch.author,
                move_shortcut_patch.description,
            ),
        )
        self.help_popover_patch_unuseddungeonchance.set_property(
            "label",
            _("Installs the patch '{}' by {}:\n{}").format(
                unused_dungeon_patch.name,
                unused_dungeon_patch.author,
                unused_dungeon_patch.description,
            ),
        )
        self.help_popover_patch_totalteamcontrol.set_property(
            "label",
            _(
                "Installs patches that allow you to control your team members manually in dungeons. Press Start to toggle. Patch by Cipnit."
            ),
        )
        self.help_popover_patch_disarm_monster_houses.set_property(
            "label",
            _("Installs the patch '{}' by {}:\n{}").format(
                disarm_one_room_mh_patch.name,
                disarm_one_room_mh_patch.author,
                disarm_one_room_mh_patch.description,
            ),
        )
        self.help_popover_patch_fixmemorysoftlock.set_property(
            "label",
            _("Installs the patch '{}' by {}:\n{}").format(
                fix_memory_softlock_patch.name,
                fix_memory_softlock_patch.author,
                fix_memory_softlock_patch.description,
            ),
        )

        self._suppress_signals = False

    @Gtk.Template.Callback()
    def on_row_patch_moveshortcuts_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["improvements"]["patch_moveshortcuts"] = self.row_patch_moveshortcuts.get_active()

    @Gtk.Template.Callback()
    def on_row_patch_unuseddungeonchance_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["improvements"]["patch_unuseddungeonchance"] = (
            self.row_patch_unuseddungeonchance.get_active()
        )

    @Gtk.Template.Callback()
    def on_row_patch_totalteamcontrol_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["improvements"]["patch_totalteamcontrol"] = (
            self.row_patch_totalteamcontrol.get_active()
        )

    @Gtk.Template.Callback()
    def on_row_patch_disarm_monster_houses_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["improvements"]["patch_disarm_monster_houses"] = (
            self.row_patch_disarm_monster_houses.get_active()
        )

    @Gtk.Template.Callback()
    def on_row_patch_fixmemorysoftlock_notify_active(self, *args):
        if self._suppress_signals:
            return
        assert self.randomization_settings is not None
        self.randomization_settings["improvements"]["patch_fixmemorysoftlock"] = (
            self.row_patch_fixmemorysoftlock.get_active()
        )
