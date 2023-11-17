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
import sys
from dataclasses import dataclass
from typing import cast, Callable

from skytemple_randomizer.config import RandomizerConfig
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw

from skytemple_randomizer.frontend.gtk.widgets import RandomizationSettingsWidget


@dataclass
class SubpageStackEntry:
    child: RandomizationSettingsWidget
    name: str
    title: str
    icon_name: str


@Gtk.Template(filename=os.path.join(MAIN_PATH, "base_dialog_settings.ui"))
class BaseSettingsDialog(Adw.Window):
    __gtype_name__ = "StBaseSettingsDialog"

    header_bar = cast(Adw.HeaderBar, Gtk.Template.Child())
    content = cast(Adw.Bin, Gtk.Template.Child())
    _children: list[RandomizationSettingsWidget]
    _getter: Callable[[], bool] | None
    _setter: Callable[[bool], None] | None

    def __init__(
        self,
        *args,
        content: RandomizationSettingsWidget | tuple[SubpageStackEntry, ...],
        getter: Callable[[], bool] | None = None,
        setter: Callable[[bool], None] | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if isinstance(content, tuple):
            self._children = []
            # Make a ViewStack with ViewStack pages and add a view switcher to the title bar
            stack = Adw.ViewStack(vexpand=True)
            for entry in content:
                stack.add_titled_with_icon(
                    cast(Gtk.Widget, entry.child),
                    entry.name,
                    entry.title,
                    entry.icon_name,
                )
                self._children.append(entry.child)
            view_switcher = Adw.ViewSwitcher(
                stack=stack, policy=Adw.ViewSwitcherPolicy.WIDE
            )
            self.header_bar.set_title_widget(view_switcher)
        else:
            self.content.set_child(cast(Gtk.Widget, content))
            self._children = [content]

        self._getter = getter
        self._setter = setter

    @Gtk.Template.Callback()
    def on_realize(self, *args):
        if sys.platform.startswith("darwin"):
            self.header_bar.set_decoration_layout("close:")

        close_esc = Gtk.Shortcut(
            trigger=Gtk.ShortcutTrigger.parse_string("Escape|<Control>w"),
            action=Gtk.NamedAction(action_name="window.close"),
        )
        self.add_shortcut(close_esc)

    def populate_settings(self, config: RandomizerConfig):
        for child in self._children:
            child.populate_settings(config)

        if self._getter is not None and self._setter is not None:
            # Add a switch to toggle the feature on and off
            def switch_notify_active(*args):
                self._setter(switch.get_active())  # type: ignore
                self.content.set_sensitive(switch.get_active())

            switch = Gtk.Switch(active=self._getter())
            self.content.set_sensitive(switch.get_active())
            switch.connect("notify::active", switch_notify_active)
            self.header_bar.pack_start(switch)
