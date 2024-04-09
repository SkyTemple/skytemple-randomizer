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

from gi.repository import Gtk, Gio, GObject

from skytemple_randomizer.frontend.abstract import PortraitDebugLine
from skytemple_randomizer.frontend.gtk.init_locale import LocalePatchedGtkTemplate
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Adw


class PortraitDebugModelRow(GObject.Object):
    def __init__(self, line: PortraitDebugLine):
        super().__init__()
        self.status = line.status
        self.monster_idx = line.monster_idx
        self.monster_name = line.monster_name
        self.form_idx = line.form_idx
        self.form_name = line.form_name
        self.traceback = line.traceback

    status = GObject.Property(type=str)
    monster_idx = GObject.Property(type=str)
    monster_name = GObject.Property(type=str)
    form_idx = GObject.Property(type=str)
    form_name = GObject.Property(type=str)
    traceback = GObject.Property(type=str)


@LocalePatchedGtkTemplate(filename=os.path.join(MAIN_PATH, "window_portrait_debug.ui"))
class PortraitDebugWindow(Adw.Window):
    __gtype_name__ = "PortraitDebugWindow"

    column_view = cast(Gtk.ColumnView, Gtk.Template.Child())
    col1_ok = cast(Gtk.ColumnViewColumn, Gtk.Template.Child())
    col2_monster_id = cast(Gtk.ColumnViewColumn, Gtk.Template.Child())
    col3_monster_name = cast(Gtk.ColumnViewColumn, Gtk.Template.Child())
    col4_form_id = cast(Gtk.ColumnViewColumn, Gtk.Template.Child())
    col5_form_name = cast(Gtk.ColumnViewColumn, Gtk.Template.Child())
    col6_traceback = cast(Gtk.ColumnViewColumn, Gtk.Template.Child())

    model: Gio.ListStore

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = Gio.ListStore(item_type=PortraitDebugModelRow)

        f = self.col1_ok.get_factory()
        assert f is not None
        f.connect("setup", self._on_factory_setup)
        f.connect("bind", self._on_factory_bind, "status")

        f = self.col2_monster_id.get_factory()
        assert f is not None
        f.connect("setup", self._on_factory_setup)
        f.connect("bind", self._on_factory_bind, "monster_idx")

        f = self.col3_monster_name.get_factory()
        assert f is not None
        f.connect("setup", self._on_factory_setup)
        f.connect("bind", self._on_factory_bind, "form_name")

        f = self.col4_form_id.get_factory()
        assert f is not None
        f.connect("setup", self._on_factory_setup)
        f.connect("bind", self._on_factory_bind, "form_idx")

        f = self.col5_form_name.get_factory()
        assert f is not None
        f.connect("setup", self._on_factory_setup)
        f.connect("bind", self._on_factory_bind, "form_name")

        f = self.col6_traceback.get_factory()
        assert f is not None
        f.connect("setup", self._on_factory_setup)
        f.connect("bind", self._on_factory_bind, "traceback")

        self.column_view.set_model(Gtk.SingleSelection(model=self.model))

    @staticmethod
    def _on_factory_setup(_factory, list_item):
        label = Gtk.Label()
        list_item.set_child(label)

    @staticmethod
    def _on_factory_bind(_factory, list_item, what):
        label_widget = list_item.get_child()
        obj = list_item.get_item()
        label_widget.set_label(str(getattr(obj, what)))

    def clear_debugs(self):
        self.model.remove_all()

    def add_debug(self, item: PortraitDebugLine):
        self.model.append(PortraitDebugModelRow(item))
