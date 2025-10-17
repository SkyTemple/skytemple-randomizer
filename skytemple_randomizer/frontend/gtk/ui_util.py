#  Copyright 2020-2025 SkyTemple Contributors
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
from typing import TypeVar, Iterable, Callable, Any

from gi.repository import GObject, Gtk, Adw, Gio, GLib
from gi.repository.Gio import AppInfo
from skytemple_files.common.i18n_util import _

from skytemple_randomizer.config import version
from skytemple_randomizer.frontend.gtk.frontend import GtkFrontend

T = TypeVar("T", bound=GObject.Object)
X = TypeVar("X")


def show_about_dialog(parent: Gtk.Widget):
    CREDITS = """Contributors:
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


def csv_filter() -> Gtk.FileFilter:
    csv_filter = Gtk.FileFilter()
    csv_filter.add_suffix("csv")
    csv_filter.add_mime_type("text/csv")
    csv_filter.set_name(_("CSV File (*.csv)"))
    return csv_filter


def xml_filter() -> Gtk.FileFilter:
    xml_filter = Gtk.FileFilter()
    xml_filter.add_suffix("xml")
    xml_filter.add_mime_type("text/xml")
    xml_filter.set_name(_("XML Document (*.xml)"))
    return xml_filter


def nds_filter() -> Gtk.FileFilter:
    nds_filter = Gtk.FileFilter()
    nds_filter.add_suffix("nds")
    nds_filter.add_mime_type("application/x-nintendo-ds-rom")
    nds_filter.set_name(_("Nintendo DS ROM (*.nds)"))
    return nds_filter


def json_filter() -> Gtk.FileFilter:
    json_filter = Gtk.FileFilter()
    json_filter.add_suffix("json")
    json_filter.add_mime_type("application/json")
    json_filter.set_name(_("JSON Document (*.json)"))
    return json_filter


def run_file_dialog(
    frontend: GtkFrontend,
    picker_key: str,
    filters: Iterable[Gtk.FileFilter],
    *,
    callback_ok: Callable[[Gtk.FileDialog, Gio.File | None], None],
    callback_error: Callable[[Gtk.FileDialog, type[BaseException], BaseException, Any], None],
    with_any_filter: bool = True,
    initial_name: str | None = None,
    save: bool = False,
    additional_dialog_kwargs: dict | None = None,
):
    """
    Create and run an async file dialog either for opening or saving. Try to remember the path that was chosen by the
    user.
    Add given filters and (by default) a filter to select any file.
    """
    if additional_dialog_kwargs is None:
        additional_dialog_kwargs = {}

    filter_store = Gio.ListStore.new(Gtk.FileFilter)

    for filter in filters:
        filter_store.append(filter)

    if with_any_filter:
        any_filter = Gtk.FileFilter()
        any_filter.add_pattern("*")
        any_filter.set_name(_("Any File"))
        filter_store.append(any_filter)

    assert frontend.settings is not None
    initial_dir = frontend.settings.get_file_picker_preset_path(picker_key)

    if initial_dir is None:
        initial_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)

    kwargs: dict[str, Any] = {"filters": filter_store}

    if initial_dir is not None:
        kwargs["initial_folder"] = Gio.File.new_for_path(initial_dir)

    if initial_name is not None:
        kwargs["initial_name"] = initial_name

    kwargs.update(additional_dialog_kwargs)

    dialog_for_file = Gtk.FileDialog(**kwargs)

    def cb(_dialog, result):
        try:
            if save:
                actual_result = dialog_for_file.save_finish(result)
            else:
                actual_result = dialog_for_file.open_finish(result)
        except Exception:
            callback_error(dialog_for_file, *sys.exc_info())
        else:
            try:
                if "RUNNING_IN_FLATPAK" not in os.environ:
                    # Useless in sandboxed environments until we get a way to get the actual file path, see
                    # https://github.com/flatpak/xdg-desktop-portal/issues/475
                    if actual_result is not None:
                        file_path = actual_result.get_path()
                        if file_path is not None:
                            file_path_parent = os.path.dirname(file_path)
                            if file_path_parent is not None:
                                assert frontend.settings is not None
                                frontend.settings.set_file_picker_preset_path(picker_key, file_path_parent)
            except Exception:
                pass

            callback_ok(dialog_for_file, actual_result)

    if save:
        dialog_for_file.save(frontend.window, None, cb)
    else:
        dialog_for_file.open(frontend.window, None, cb)
