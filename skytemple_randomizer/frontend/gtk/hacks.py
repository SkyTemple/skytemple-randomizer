"""Hacks that could easily break and should ideally not be relied upon."""

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
from gi.repository import Adw


def force_adw_entry_row_no_title(row: Adw.EntryRow):
    try:
        child = row.get_child()
        if child is not None:
            for child in child:  # type: ignore
                if child.get_buildable_id() == "editable_area":  # type: ignore
                    for child in child:  # type: ignore
                        if child.get_buildable_id() == "title":  # type: ignore
                            child.hide()  # type: ignore
    except Exception:
        pass
