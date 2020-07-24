#  Copyright 2020 Parakoopa
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
import logging
import os
import sys
import traceback
import webbrowser

import gi

from skytemple_files.dungeon_randomizer import run_main as run_dungeon_randomizer
from skytemple_files.ground_actor_randomizer import run_main as run_ground_actor_randomizer
from skytemple_files.starter_randomizer import run_main as run_starter_randomizer

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk, GLib
from gi.repository.Gtk import Window


class MainController:
    def __init__(self, builder: Gtk.Builder, window: Window):
        self.builder = builder
        self.window = window

        filter_nds = Gtk.FileFilter()
        filter_nds.set_name("Nintendo DS ROMs (*.nds)")
        filter_nds.add_mime_type("application/x-nintendo-ds-rom")
        filter_nds.add_pattern("*.nds")
        self.builder.get_object('input_file').add_filter(filter_nds)
        self.file_chooser: Gtk.FileChooserButton = self.builder.get_object('input_file')

        self.builder.connect_signals(self)

    def on_destroy(self, *args):
        Gtk.main_quit()

    def on_main_window_delete_event(self, *args):
        Gtk.main_quit()
        return False

    def gtk_widget_hide_on_delete(self, w: Gtk.Widget, *args):
        w.hide_on_delete()
        return True

    def on_about_clicked(self, *args):
        self.builder.get_object("about_dialog").run()

    def on_randomize_clicked(self, *args):
        in_fn = self.file_chooser.get_filename()
        if in_fn is None:
            self.display_error("Please choose an input file.")
            return
        rand_dungeons = self.builder.get_object('rand_dungeons').get_active()
        rand_npcs = self.builder.get_object('rand_npcs').get_active()
        rand_starters = self.builder.get_object('rand_starters').get_active()
        if not rand_dungeons and not rand_npcs and not rand_starters:
            self.display_error("You need to choose something to randomize.")
            return

        dialog = Gtk.FileChooserDialog(
            "Output ROM filename...",
            self.window,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        )

        filter_nds = Gtk.FileFilter()
        filter_nds.set_name("Nintendo DS ROMs (*.nds)")
        filter_nds.add_mime_type("application/x-nintendo-ds-rom")
        filter_nds.add_pattern("*.nds")
        dialog.add_filter(filter_nds)

        response = dialog.run()
        out_fn = dialog.get_filename()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            try:
                if rand_npcs:
                    run_ground_actor_randomizer(in_fn, out_fn)
                    in_fn = out_fn
                if rand_dungeons:
                    run_dungeon_randomizer(in_fn, out_fn)
                    in_fn = out_fn
                if rand_starters:
                    run_starter_randomizer(in_fn, out_fn)
                md = Gtk.MessageDialog(self.window,
                                       Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.OK,
                                       "Successfully randomized!",
                                       title="SkyTemple Randomizer")
                md.run()
                md.destroy()
            except BaseException as ex:
                tb = traceback.format_exc()
                print(tb)
                self.display_error(f"Error: {ex}\n{tb}")
                return

    def on_explanation_activate_link(self, *args):
        webbrowser.open_new_tab("https://discord.gg/4e3X36f")

    def on_explanation1_activate_link(self, *args):
        webbrowser.open_new_tab("https://projectpokemon.org/home/forums/topic/57303-pmd2-skytemple-rom-editor-maps-scripts-debugger/")

    def display_error(self, error_message, error_title='SkyTemple Randomizer - Error'):
        md = Gtk.MessageDialog(self.window,
                               Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR,
                               Gtk.ButtonsType.OK,
                               error_message,
                               title=error_title)
        md.run()
        md.destroy()


def main():
    path = os.path.abspath(os.path.dirname(__file__))

    if sys.platform.startswith('win'):
        # Load theming under Windows
        _windows_load_theme()
        # Solve issue #12
        try:
            from skytemple_files.common.platform_utils.win import win_set_error_mode
            win_set_error_mode()
        except BaseException:
            # This really shouldn't fail, but it's not important enough to crash over
            pass

    if sys.platform.startswith('darwin'):
        # Load theming under macOS
        _macos_load_theme()

    itheme: Gtk.IconTheme = Gtk.IconTheme.get_default()
    itheme.append_search_path(os.path.abspath(os.path.join(data_dir(), "icons")))
    itheme.rescan_if_needed()

    # Load Builder and Window
    builder = Gtk.Builder()
    builder.add_from_file(os.path.join(path, "skytemple_randomizer.glade"))
    main_window: Window = builder.get_object("main_window")
    main_window.set_role("SkyTemple Randomizer")
    GLib.set_application_name("SkyTemple Randomizer")
    GLib.set_prgname("skytemple_randomizer")
    # TODO: Deprecated but the only way to set the app title on GNOME...?
    main_window.set_wmclass("SkyTemple Randomizer", "SkyTemple Randomizer")

    # Load main window + controller
    MainController(builder, main_window)

    main_window.present()
    main_window.set_icon_name('skytemple')
    Gtk.main()


def data_dir():
    return os.path.join(os.path.dirname(__file__), 'data')


def _windows_load_theme():
    from skytemple_files.common.platform_utils.win import win_use_light_theme
    settings = Gtk.Settings.get_default()
    theme_name = 'Arc'
    if not win_use_light_theme():
        settings.set_property("gtk-application-prefer-dark-theme", True)
        theme_name = 'Arc-Dark'
    settings.set_property("gtk-theme-name", theme_name)


def _macos_load_theme():
    from skytemple_files.common.platform_utils.macos import macos_use_light_theme
    settings = Gtk.Settings.get_default()
    theme_name = 'Mojave-light'
    if not macos_use_light_theme():
        settings.set_property("gtk-application-prefer-dark-theme", True)
        theme_name = 'Mojave-dark'
    settings.set_property("gtk-theme-name", theme_name)


if __name__ == '__main__':
    # TODO: At the moment doesn't support any cli arguments.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    main()
