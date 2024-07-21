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
import pathlib
import sys
from typing import TypeVar

from gi.repository import GObject, Gtk, Adw
from gi.repository.Gio import AppInfo
from skytemple_files.common.i18n_util import _

from skytemple_randomizer.config import version

T = TypeVar("T", bound=GObject.Object)
X = TypeVar("X")


def show_about_dialog(parent: Gtk.Widget):
    CREDITS = """Project Lead:
Marco "Capypara" Köpcke https://github.com/theCapypara

Contributors:
Aikku93 (via tilequant) https://github.com/aikku93
techticks (MacOS packaging) https://github.com/tech-ticks
marius851000 (via skytemple-rust) https://github.com/marius851000
UsernameFodder (via pmdsky-debug) https://reddit.com/u/UsernameFodder
Frostbyte (via patches + contributions) https://github.com/Frostbyte0x70
Anonymous (via patches + contributions)
Cipnit (via CTC patch) https://www.pokecommunity.com/member.php?u=751556
Adex (via patches + JP support) https://github.com/Adex-8x
Darkaim (JP support)
Laioxy (JP support via pmdsky-debug) https://github.com/Laioxy
in2erval (code contributions) https://github.com/in2erval
Please see GitHub for more minor contributors.

Lead Hackers:
Frostbyte https://github.com/Frostbyte0x70
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

    about_dialog = Adw.AboutDialog(
        application_icon="skytemple_randomizer",
        application_name="SkyTemple Randomizer",
        artists=[
            "Charburst (Logo and Illustrations) https://twitter.com/Charburst_",
            "Aviivix (UI Icons) https://twitter.com/aviivix",
            "Edael (Duskako Sprites) https://twitter.com/Exodus_Drake",
        ],
        comments=_("Application to randomize the ROM of Pokémon Mystery Dungeon Explorers of Sky."),
        developers=CREDITS.splitlines(),
        issue_url="https://github.com/SkyTemple/skytemple-randomizer",
        license_type=Gtk.License.GPL_3_0,
        support_url="https://wiki.skytemple.org",
        version=version(),
        website="https://skytemple.org",
    )
    about_dialog.present(parent)


def open_dir(directory):
    """Cross-platform open directory"""
    if sys.platform == "win32":
        os.startfile(directory)
    else:
        AppInfo.launch_default_for_uri(pathlib.Path(directory).as_uri())
