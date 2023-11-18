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
from typing import TypeVar, Any
from collections.abc import Iterable

from gi.repository import GObject, Gtk, Adw
from skytemple_files.common.i18n_util import _

from skytemple_randomizer.config import version
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend

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


def set_default_dialog_size(dialog: Gtk.Window, parent: Gtk.Window, height=None):
    p_width, p_height = parent.get_default_size()
    a_height = round(p_height * 0.8)
    if height is not None:
        a_height = min(a_height, height)
    dialog.set_default_size(min(p_width, max(round(p_width * 0.8), 420)), a_height)


def show_about_dialog():
    CREDITS = """Project Lead:
Marco "Capypara" Köpcke https://github.com/theCapypara

Contributors:
Aikku93 (via tilequant) https://github.com/aikku93
techticks (MacOS packaging) https://github.com/tech-ticks
marius851000 (via skytemple-rust) https://github.com/marius851000
UsernameFodder (via pmdsky-debug) https://reddit.com/u/UsernameFodder
End45 (via patches) https://github.com/End45
Anonymous (via patches + contributions)
Cipnit (via CTC patch) https://www.pokecommunity.com/member.php?u=751556
Adex (via patches + JP support) https://github.com/Adex-8x
Darkaim (JP support)
Laioxy (JP support via pmdsky-debug) https://github.com/Laioxy
Please see GitHub for more minor contributors.

Lead Hackers:
End45 https://github.com/End45
UsernameFodder https://reddit.com/u/UsernameFodder
Anonymous
psy_commando https://github.com/psyCommando

Hackers:
evandixon https://github.com/evandixon
MegaMinerd
Nerketur

Special Thanks:
Everyone testing and documenting SkyTemple, the SkyTemple Discord mods (former and current) and everyone making hacks, organizing hack jams or creating community content!

Especially thank you DasK, Audino, Keldaan and MaxSchersey!"""

    about_dialog = Adw.AboutWindow(
        application_icon="skytemple_randomizer",
        application_name="SkyTemple Randomizer",
        artists=[
            "Charburst (Logo and Illustrations) https://twitter.com/Charburst_",
            "Aviivix (UI Icons) https://twitter.com/aviivix",
            "Edael (Duskako Sprites) https://twitter.com/Exodus_Drake",
        ],
        comments=_(
            "Application to randomize the ROM of Pokémon Mystery Dungeon Explorers of Sky."
        ),
        developers=CREDITS.splitlines(),
        issue_url="https://github.com/SkyTemple/skytemple-randomizer",
        license_type=Gtk.License.GPL_3_0,
        support_url="https://wiki.skytemple.org",
        version=version(),
        website="https://skytemple.org",
        application=GtkFrontend.instance().application,
        destroy_with_parent=True,
        modal=True,
        resizable=True,
        transient_for=GtkFrontend.instance().window,
    )
    about_dialog.present()
