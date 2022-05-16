#  Copyright 2020-2021 Capypara and the SkyTemple Contributors
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

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')

import json
import logging
import os
import random
import sys
import traceback
import webbrowser
from functools import partial
from math import floor
from typing import Optional, Callable, Dict
import yaml
from gi.repository.GtkSource import StyleSchemeManager, LanguageManager
from jsonschema import ValidationError
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from skytemple_randomizer.frontend.abstract import AbstractFrontend

import packaging.version

from skytemple_files.common.version_util import check_newest_release, ReleaseType
from skytemple_randomizer.randomizer.util.util import clear_script_cache

from ndspy.rom import NintendoDSRom

from skytemple_files.common.ppmdu_config.xml_reader import Pmd2XmlReader
from skytemple_files.common.util import open_utf8
from skytemple_icons import icons
from skytemple_randomizer.config import ConfigFileLoader, EnumJsonEncoder, \
    get_effective_seed, version, data_dir, Global
from skytemple_randomizer.frontend.gtk.config import ConfigUIApplier, ConfigUIReader, ConfigDocApplier
from skytemple_randomizer.randomizer_thread import RandomizerThread
from skytemple_randomizer.status import Status

from gi.repository import Gtk, GLib, Gdk, GtkSource
from gi.repository.Gtk import Window


class GtkFrontend(AbstractFrontend):
    def idle_add(self, fn: Callable):
        GLib.idle_add(fn)


class MainController:
    def __init__(self, builder: Gtk.Builder, window: Window):
        self.builder = builder
        Global.main_builder = builder
        self.window: Window = window

        accel = Gtk.AccelGroup()
        accel.connect(Gdk.KEY_space, Gdk.ModifierType.CONTROL_MASK, 0, self.on_show_debug)
        self.window.add_accel_group(accel)
        self.builder.get_object('progress').add_accel_group(accel)

        self.static_config = Pmd2XmlReader.load_default('EoS_EU')  # version doesn't really matter for this

        self.chosen_file = None

        # Source view
        view: GtkSource.View = self.builder.get_object('text_quiz_content')
        buffer: GtkSource.Buffer = GtkSource.Buffer.new_with_language(LanguageManager.get_default().get_language('yaml'))
        view.set_show_line_numbers(True)
        view.set_show_line_marks(True)
        view.set_auto_indent(True)
        view.set_insert_spaces_instead_of_tabs(True)
        view.set_indent_width(4)
        view.set_show_right_margin(True)
        view.set_indent_on_tab(True)
        view.set_highlight_current_line(True)
        view.set_smart_backspace(True)
        view.set_smart_home_end(True)
        view.set_monospace(True)
        buffer.set_highlight_matching_brackets(True)
        buffer.set_highlight_syntax(True)
        style_scheme_manager = StyleSchemeManager()
        selected_style_scheme_id = None
        for style_id in style_scheme_manager.get_scheme_ids():
            if not selected_style_scheme_id or style_id == 'oblivion':
                selected_style_scheme_id = style_id
        buffer.set_style_scheme(style_scheme_manager.get_scheme(selected_style_scheme_id))
        view.set_buffer(buffer)

        # Load default configuration
        self.ui_applier = ConfigUIApplier(self.builder,
                                          self.static_config.dungeon_data.dungeons,
                                          self.static_config.dungeon_data.items)
        self.ui_reader = ConfigUIReader(self.builder)
        self.ui_applier.apply(ConfigFileLoader.load(os.path.join(data_dir(), 'default.json')))
        ConfigDocApplier(self.window, self.builder).apply()
        self._check_for_updates()

        self.builder.connect_signals(self)

    def on_destroy(self, *args):
        Gtk.main_quit()

    def on_main_window_delete_event(self, *args):
        Gtk.main_quit()
        return False

    def gtk_widget_hide_on_delete(self, w: Gtk.Widget, *args):
        w.hide_on_delete()
        return True

    def on_update_button_clicked(self, *args):
        webbrowser.open_new_tab("https://projectpokemon.org/home/files/file/4235-skytemple-randomizer/")

    def on_show_debug(self, *args):
        self.builder.get_object('portrait_debug').show()

    def on_cr_dungeons_settings_randomize_toggled(self, widget, path):
        store: Gtk.Store = self.builder.get_object('store_tree_dungeons_dungeons')
        store[path][2] = not widget.get_active()

    def on_cr_dungeons_settings_monster_houses_toggled(self, widget, path):
        store: Gtk.Store = self.builder.get_object('store_tree_dungeons_dungeons')
        store[path][3] = not widget.get_active()

    def on_cr_dungeons_settings_randomize_weather_toggled(self, widget, path):
        store: Gtk.Store = self.builder.get_object('store_tree_dungeons_dungeons')
        store[path][4] = not widget.get_active()

    def on_cr_dungeons_settings_unlock_toggled(self, widget, path):
        store: Gtk.Store = self.builder.get_object('store_tree_dungeons_dungeons')
        store[path][5] = not widget.get_active()

    def on_cr_pokemon_abilities_enabled_use_toggled(self, widget, path):
        store: Gtk.Store = self.builder.get_object('store_tree_monsters_abilities')
        store[path][2] = not widget.get_active()

    def on_cr_pokemon_monsters_enabled_use_toggled(self, widget, path):
        store: Gtk.Store = self.builder.get_object('store_tree_monsters_monsters')
        store[path][2] = not widget.get_active()

    def on_cr_pokemon_moves_enabled_use_toggled(self, widget, path):
        store: Gtk.Store = self.builder.get_object('store_tree_monsters_moves')
        store[path][2] = not widget.get_active()

    def on_cr_dungeons_items_enabled_use_toggled(self, widget, path):
        store: Gtk.Store = self.builder.get_object('store_tree_dungeons_items')
        store[path][2] = not widget.get_active()

    def on_cr_dungeons_settings_enemy_iq_toggled(self, widget, path):
        store: Gtk.Store = self.builder.get_object('store_tree_dungeons_dungeons')
        store[path][6] = not widget.get_active()

    def on_btn_rom_clicked(self, *args):
        dialog: Gtk.FileChooserNative = Gtk.FileChooserNative.new(
            "Open ROM...",
            self.window,
            Gtk.FileChooserAction.OPEN,
            None, None
        )

        filter_nds = Gtk.FileFilter()
        filter_nds.set_name("Nintendo DS ROMs (*.nds)")
        filter_nds.add_mime_type("application/x-nintendo-ds-rom")
        filter_nds.add_pattern("*.nds")
        dialog.add_filter(filter_nds)

        response = dialog.run()
        fn = dialog.get_filename()
        dialog.destroy()

        if response == Gtk.ResponseType.ACCEPT:
            self.chosen_file = fn
            self.builder.get_object('label_rom').set_text(os.path.basename(fn))

    def on_import_clicked(self, *args):
        dialog: Gtk.FileChooserNative = Gtk.FileChooserNative.new(
            "Import configuration...",
            self.window,
            Gtk.FileChooserAction.OPEN,
            None, None
        )

        filter = Gtk.FileFilter()
        filter.set_name("JSON configuration file (*.json)")
        filter.add_mime_type("	application/json")
        filter.add_pattern("*.json")
        dialog.add_filter(filter)

        response = dialog.run()
        fn = dialog.get_filename()
        dialog.destroy()

        if response == Gtk.ResponseType.ACCEPT:
            try:
                self.ui_applier.apply(ConfigFileLoader.load(fn))
            except BaseException as e:
                self.display_error(f"The config file you tried to import is invalid:\n{e.__class__.__name__}:\n{e}")

    def on_export_clicked(self, *args):
        save_diag = Gtk.FileChooserNative.new(
            "Export configuration...",
            self.window,
            Gtk.FileChooserAction.SAVE,
            None, None
        )

        filter = Gtk.FileFilter()
        filter.set_name("JSON configuration file (*.json)")
        filter.add_mime_type("application/json")
        filter.add_pattern("*.json")
        save_diag.add_filter(filter)
        response = save_diag.run()
        fn = save_diag.get_filename()
        save_diag.destroy()

        if response == Gtk.ResponseType.ACCEPT:
            if '.' not in fn:
                fn += '.json'
            with open_utf8(fn, 'w') as f:
                try:
                    json.dump(self.ui_reader.read(), f, indent=4, cls=EnumJsonEncoder, ensure_ascii=False)
                except Exception as err:
                    tb = ""
                    if not isinstance(err, ValidationError) and not isinstance(err, ScannerError) and not isinstance(err, ParserError):
                        tb = traceback.format_exc()
                        print(tb)
                    self.display_error(f"Error saving these settings:\n{err}\n{tb}")

    def on_about_clicked(self, *args):
        about: Gtk.AboutDialog = self.builder.get_object("about_dialog")
        about.connect("response", lambda d, r: d.hide())

        def activate_link(l, uri, *args):
            webbrowser.open_new_tab(uri)
            return True

        about.connect("activate-link", activate_link)
        header_bar: Optional[Gtk.HeaderBar] = about.get_header_bar()
        if header_bar is not None:
            # Cool bug??? And it only works on the left as well, wtf?
            header_bar.set_decoration_layout('close')
        about.set_version(version())
        about.run()

    def on_discord_clicked(self, *args):
        webbrowser.open_new_tab('https://discord.gg/skytemple')

    def on_skytemple_clicked(self, *args):
        webbrowser.open_new_tab('https://skytemple.org')

    def on_randomize_clicked(self, *args):
        if self.chosen_file is None:
            self.display_error("Please choose an input file.")
            return

        dialog = Gtk.FileChooserNative.new(
            "Output ROM filename...",
            self.window,
            Gtk.FileChooserAction.SAVE,
            None, None
        )

        filter_nds = Gtk.FileFilter()
        filter_nds.set_name("Nintendo DS ROMs (*.nds)")
        filter_nds.add_mime_type("application/x-nintendo-ds-rom")
        filter_nds.add_pattern("*.nds")
        dialog.add_filter(filter_nds)

        response = dialog.run()
        out_fn = dialog.get_filename()
        dialog.destroy()

        if response == Gtk.ResponseType.ACCEPT:
            clear_script_cache()
            if '.' not in out_fn:
                out_fn += '.nds'
            try:
                self.builder.get_object('progress_close').set_sensitive(False)
                progress_bar: Gtk.ProgressBar = self.builder.get_object('progress_bar')
                progress_label: Gtk.Label = self.builder.get_object('progress_label')
                progress_diag: Gtk.Dialog = self.builder.get_object('progress')
                progress_diag.set_title('Randomizing...')

                def update_fn(progress, desc):
                    progress_bar.set_fraction((progress - 1) / randomizer.total_steps)
                    if desc == Status.DONE_SPECIAL_STR:
                        progress_label.set_text("Randomizing complete!")
                    else:
                        progress_label.set_text(f"{floor((progress - 1) / randomizer.total_steps * 100)}%: {desc}")

                def check_done():
                    if not randomizer.is_done():
                        return True
                    self.builder.get_object('progress_close').set_sensitive(True)
                    if randomizer.error:
                        img: Gtk.Image = self.builder.get_object('img_portrait_duskako')
                        img.set_from_file(os.path.join(data_dir(), 'duskako_sad.png'))
                        traceback_str = ''.join(traceback.format_exception(*randomizer.error))
                        progress_label.set_text(f"Error: {traceback_str}")
                        progress_diag.set_title('Randomizing failed!')
                    else:
                        rom.saveToFile(out_fn)
                        img: Gtk.Image = self.builder.get_object('img_portrait_duskako')
                        img.set_from_file(os.path.join(data_dir(), 'duskako_happy.png'))
                        progress_label.set_text("Randomizing complete!")
                        progress_diag.set_title('Randomizing complete!')
                    return False

                rom = NintendoDSRom.fromFile(self.chosen_file)
                status = Status()
                status.subscribe(lambda a, b: GLib.idle_add(partial(update_fn, a, b)))
                try:
                    config = self.ui_reader.read()
                except Exception as err:
                    tb = ""
                    if not isinstance(err, ValidationError) and not isinstance(err, ScannerError) and not isinstance(err, ParserError):
                        tb = traceback.format_exc()
                        print(tb)
                    self.display_error(f"There is an error in your settings:\n{err}\n{tb}")
                    return
                # Set the seed
                seed = get_effective_seed(config['seed'])
                random.seed(seed)
                self.builder.get_object('seed_label').set_text('Your Seed: ' + str(seed))
                randomizer = RandomizerThread(status, rom, config, seed, GtkFrontend())
                randomizer.start()

                # SHOW DIALOG
                img: Gtk.Image = self.builder.get_object('img_portrait_duskako')
                img.set_from_file(os.path.join(data_dir(), 'duskako_neutral.png'))

                GLib.timeout_add(100, check_done)

                progress_diag.run()
            except BaseException as ex:
                tb = traceback.format_exc()
                print(tb)
                self.display_error(f"Error: {ex}\n{tb}")
                return

    def on_progress_close_clicked(self, *args):
        self.builder.get_object('progress').hide()

    def on_portrait_close_clicked(self, *args):
        self.builder.get_object('portrait_debug').hide()

    def display_error(self, error_message, error_title='SkyTemple Randomizer - Error'):
        md = Gtk.MessageDialog(self.window,
                               Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR,
                               Gtk.ButtonsType.OK,
                               error_message,
                               title=error_title)
        md.run()
        md.destroy()

    def _check_for_updates(self):
        try:
            new_version = check_newest_release(ReleaseType.SKYTEMPLE_RANDOMIZER)
            if packaging.version.parse(version()) < packaging.version.parse(new_version):
                self.builder.get_object('update_new_version').set_text(new_version)
                return
        except Exception:
            pass
        # else/except:
        self.builder.get_object('update_info').hide()


def main():
    path = os.path.abspath(os.path.dirname(__file__))

    if sys.platform.startswith('win'):
        # Load theming under Windows
        _load_theme()
        # Solve issue #12
        try:
            from skytemple_files.common.platform_utils.win import win_set_error_mode
            win_set_error_mode()
        except BaseException:
            # This really shouldn't fail, but it's not important enough to crash over
            pass

    if sys.platform.startswith('darwin'):
        # Load theming under macOS
        _load_theme()

        # The search path is wrong if SkyTemple is executed as an .app bundle
        if getattr(sys, 'frozen', False):
            path = os.path.dirname(sys.executable)

    itheme: Gtk.IconTheme = Gtk.IconTheme.get_default()
    itheme.append_search_path(os.path.abspath(icons()))
    itheme.append_search_path(os.path.abspath(os.path.join(data_dir(), "icons")))
    itheme.rescan_if_needed()

    # Load CSS
    style_provider = Gtk.CssProvider()
    with open(os.path.join(path, "skytemple_randomizer.css"), 'rb') as f:
        css = f.read()
    style_provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

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

    try:
        wa = Gdk.Display.get_default().get_primary_monitor().get_workarea()
        main_window.resize(
            min(1280, wa.width),
            min(768, wa.height)
        )
    except:
        main_window.resize(
            1280, 768
        )
    main_window.set_position(Gtk.WindowPosition.CENTER)
    main_window.present()
    main_window.set_icon_name('skytemple_randomizer')
    Gtk.main()


def _load_theme():
    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-theme-name", 'Arc-Dark')


if __name__ == '__main__':
    def str_presenter(dumper, data):
        if len(data.splitlines()) > 1:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)


    yaml.add_representer(str, str_presenter)
    yaml.representer.SafeRepresenter.add_representer(str, str_presenter)

    # TODO: At the moment doesn't support any cli arguments.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    main()
