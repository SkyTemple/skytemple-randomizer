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
from typing import TypeVar, Iterable, Any

from gi.repository import GObject, Gtk

T = TypeVar("T", bound=GObject.Object)
X = TypeVar("X")
UI_ASSERT = "SKYTEMPLE_UI_ASSERT" in os.environ


def builder_get_assert(builder: Gtk.Builder, typ: type[T], name: str) -> T:
    obj = builder.get_object(name)
    if UI_ASSERT:
        assert isinstance(obj, typ)
        return obj
    else:
        return obj  # type: ignore


def builder_get_assert_exist(builder: Gtk.Builder, typ: type[T], name: str) -> T:
    obj = builder.get_object(name)
    if obj is None:
        raise ValueError(f"UI element '{obj}' not found.")
    if UI_ASSERT:
        assert isinstance(obj, typ)
        return obj
    else:
        return obj  # type: ignore


def iter_maybe(x: Iterable[X] | None) -> Iterable[X]:
    if x is None:
        return ()
    return x


def iter_tree_model(model: Gtk.TreeModel) -> Any:
    # TODO: This works but isn't supported by the typestubs.
    return model  # type: ignore
