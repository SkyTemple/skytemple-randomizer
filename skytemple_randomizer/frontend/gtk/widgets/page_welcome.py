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

import hashlib
import os
import webbrowser
from typing import Optional, cast

import packaging.version
from skytemple_files.common.version_util import check_newest_release, ReleaseType, get_event_banner

from skytemple_randomizer.config import version
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend
from skytemple_randomizer.frontend.gtk.path import MAIN_PATH

from gi.repository import Gtk, Adw, Gio, GdkPixbuf, Gdk


@Gtk.Template(filename=os.path.join(MAIN_PATH, "page_welcome.ui"))
class WelcomePage(Adw.Bin):
    __gtype_name__ = "StWelcomePage"

    update_info = cast(Adw.Banner, Gtk.Template.Child())
    info_stack = cast(Gtk.Stack, Gtk.Template.Child())
    banner_info = cast(Gtk.Box, Gtk.Template.Child())
    link_button_wiki = cast(Gtk.LinkButton, Gtk.Template.Child())
    link_button_discord = cast(Gtk.LinkButton, Gtk.Template.Child())
    link_button_skytemple = cast(Gtk.LinkButton, Gtk.Template.Child())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._check_for_updates()
        self._check_for_banner()
        self.link_button_wiki.set_cursor_from_name("default")
        self.link_button_discord.set_cursor_from_name("default")
        self.link_button_skytemple.set_cursor_from_name("default")

    @Gtk.Template.Callback()
    def on_update_info_button_clicked(self, *args):
        webbrowser.open_new_tab("https://download.skytemple.org/randomizer/latest")

    @Gtk.Template.Callback()
    def on_any_link_button_activate_link(self, w: Gtk.LinkButton, *args):
        webbrowser.open_new_tab(w.get_uri())
        return True

    @Gtk.Template.Callback()
    def on_about_button_clicked(self, *args):
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
                "Edael (Duskako Sprites) https://twitter.com/Exodus_Drake"
            ],
            comments="Application to randomize the ROM of Pokémon Mystery Dungeon Explorers of Sky (EU/US).",
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

    def _check_for_updates(self):
        try:
            ver = version()
            if ver == "dev":
                return
            new_version = check_newest_release(ReleaseType.SKYTEMPLE_RANDOMIZER)
            if packaging.version.parse(ver) < packaging.version.parse(new_version):
                self.update_info.set_title(self.update_info.get_title().replace("{version}", new_version))
                return
        except Exception:
            pass
        # else/except:
        self.update_info.set_revealed(False)

    def _check_for_banner(self):
        try:
            # uncomment the following line to test banner.
            #import skytemple_files.common.version_util; skytemple_files.common.version_util.RELEASE_WEB = "https://raw.githubusercontent.com/SkyTemple/release-info/17d9087293f9c11a2353dd60e878bd78874496fc/"
            img_banner, url = get_event_banner()
            if img_banner is not None:
                input_stream = Gio.MemoryInputStream.new_from_data(img_banner, None)
                pixbuf = GdkPixbuf.Pixbuf.new_from_stream(input_stream, None)
                assert pixbuf is not None
                image = Gtk.Picture.new_for_pixbuf(pixbuf)
                image.set_can_shrink(True)
                image.set_hexpand(True)
                image.show()

                def open_web(*args):
                    if url is not None:
                        webbrowser.open_new_tab(url)

                def cursor_change_enter(*args):
                    self.banner_info.set_cursor_from_name("pointer")

                def cursor_change_leave(*args):
                    self.banner_info.set_cursor_from_name("default")
                click_gesture = Gtk.GestureClick()
                click_gesture.set_button(Gdk.BUTTON_PRIMARY)
                click_gesture.connect('pressed', open_web)
                self.banner_info.add_controller(click_gesture)
                motion_controller = Gtk.EventControllerMotion()
                motion_controller.connect('enter', cursor_change_enter)
                motion_controller.connect('leave', cursor_change_leave)
                self.banner_info.add_controller(motion_controller)
                self.banner_info.append(image)
                self.info_stack.set_visible_child_name("info_stack_banner")
                return
        except Exception:
            pass
        # else/except:
        self.info_stack.set_visible_child_name("info_stack_text")
