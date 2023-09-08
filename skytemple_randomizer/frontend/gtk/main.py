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

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from strictyaml import YAMLError

from skytemple_randomizer.frontend.gtk.settings import SkyTempleRandomizerSettingsStoreGtk
from skytemple_randomizer.frontend.gtk.ui_util import builder_get_assert, iter_maybe, iter_tree_model

import json
import logging
import os
import random
import sys
import traceback
import webbrowser
from functools import partial
from math import floor
from typing import Optional, Callable
from gi.repository.GtkSource import StyleSchemeManager, LanguageManager, SmartHomeEndType
from jsonschema import ValidationError

from skytemple_randomizer.frontend.abstract import AbstractFrontend

import packaging.version

from skytemple_files.common.version_util import check_newest_release, ReleaseType, get_event_banner
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
from skytemple_randomizer.lists import DEFAULTMONSTERPOOL

from gi.repository import Gtk, GLib, Gdk, GtkSource, Gio, GdkPixbuf


if getattr(sys, 'frozen', False):
    # Running via PyInstaller. Fix SSL configuration
    os.environ["SSL_CERT_FILE"] = os.path.join(
        os.path.dirname(sys.executable), "certifi", "cacert.pem"
    )


class GtkFrontend(AbstractFrontend):
    def idle_add(self, fn: Callable):
        GLib.idle_add(fn)


class MainController(Gtk.Application):
    def __init__(self):
        # Load Builder and Window
        path = os.path.abspath(os.path.dirname(__file__))
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(path, "skytemple_randomizer.glade"))
        self.window = builder_get_assert(builder, Gtk.ApplicationWindow, "main_window")
        super().__init__(application_id="org.skytemple.Randomizer")
        GLib.set_application_name("SkyTemple Randomizer")

        self.builder = builder
        Global.main_builder = builder

        accel = Gtk.AccelGroup()
        accel.connect(Gdk.KEY_space, Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags(0), self.on_show_debug)
        self.window.add_accel_group(accel)
        builder_get_assert(builder, Gtk.Dialog, 'progress').add_accel_group(accel)

        self.static_config = Pmd2XmlReader.load_default('EoS_EU')  # version doesn't really matter for this
        self.settings = SkyTempleRandomizerSettingsStoreGtk()

        self.chosen_file: Optional[str] = None

        # Source view
        view = builder_get_assert(builder, GtkSource.View, 'text_quiz_content')
        lang = LanguageManager.get_default().get_language('yaml')
        buffer: GtkSource.Buffer
        if lang is not None:
            buffer = GtkSource.Buffer.new_with_language(lang)
        else:
            buffer = GtkSource.Buffer.new()
        view.set_show_line_numbers(True)
        view.set_show_line_marks(True)
        view.set_auto_indent(True)
        view.set_insert_spaces_instead_of_tabs(True)
        view.set_indent_width(4)
        view.set_show_right_margin(True)
        view.set_indent_on_tab(True)
        view.set_highlight_current_line(True)
        view.set_smart_backspace(True)
        view.set_smart_home_end(SmartHomeEndType.BEFORE)
        view.set_monospace(True)
        buffer.set_highlight_matching_brackets(True)
        buffer.set_highlight_syntax(True)
        style_scheme_manager = StyleSchemeManager()
        selected_style_scheme_id = None
        for style_id in iter_maybe(style_scheme_manager.get_scheme_ids()):
            if not selected_style_scheme_id or style_id == 'oblivion':
                selected_style_scheme_id = style_id
        if selected_style_scheme_id is not None:
            buffer.set_style_scheme(style_scheme_manager.get_scheme(selected_style_scheme_id))
        view.set_buffer(buffer)

        # Load default configuration
        self.ui_applier = ConfigUIApplier(self.builder,
                                          self.static_config.dungeon_data.dungeons,
                                          self.static_config.dungeon_data.items,
                                          self.static_config.dungeon_data.item_categories)
        self.ui_reader = ConfigUIReader(self.builder)
        self.ui_applier.apply(ConfigFileLoader.load(os.path.join(data_dir(), 'default.json')))
        ConfigDocApplier(self.window, self.builder).apply()
        self._check_for_updates()

        self.banner_hash: Optional[str] = None
        self._check_for_banner()

        self.builder.connect_signals(self)

        try:
            default_display = Gdk.Display.get_default()
            assert default_display is not None
            primary_monitor = default_display.get_primary_monitor()
            assert primary_monitor is not None
            wa = primary_monitor.get_workarea()
            self.window.resize(
                min(1280, wa.width),
                min(768, wa.height)
            )
        except:
            self.window.resize(
                1280, 768
            )
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_icon_name('skytemple_randomizer')

    def do_activate(self) -> None:
        self.window.set_application(self)
        self.window.present()

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
        builder_get_assert(self.builder, Gtk.Dialog, 'portrait_debug').show()

    def on_cr_dungeons_settings_randomize_toggled(self, widget, path):
        store = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_dungeons_dungeons')
        store[path][2] = not widget.get_active()

    def on_cr_dungeons_settings_monster_houses_toggled(self, widget, path):
        store = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_dungeons_dungeons')
        store[path][3] = not widget.get_active()

    def on_cr_dungeons_settings_randomize_weather_toggled(self, widget, path):
        store = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_dungeons_dungeons')
        store[path][4] = not widget.get_active()

    def on_cr_dungeons_settings_unlock_toggled(self, widget, path):
        store = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_dungeons_dungeons')
        store[path][5] = not widget.get_active()

    def on_cr_pokemon_abilities_enabled_use_toggled(self, widget, path):
        store = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_monsters_abilities')
        store[path][2] = not widget.get_active()

    def on_cr_pokemon_monsters_enabled_use_toggled(self, widget, path):
        store = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_monsters_monsters')
        store[path][2] = not widget.get_active()

    def on_cr_pokemon_starters_enabled_use_toggled(self, widget, path):
        store = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_monsters_starters')
        store[path][2] = not widget.get_active()

    def on_cr_pokemon_moves_enabled_use_toggled(self, widget, path):
        store = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_monsters_moves')
        store[path][2] = not widget.get_active()

    def on_cr_dungeons_items_enabled_use_toggled(self, widget, path):
        store = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_dungeons_items')
        store[path][2] = not widget.get_active()

    def on_cr_dungeons_settings_enemy_iq_toggled(self, widget, path):
        store = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_dungeons_dungeons')
        store[path][6] = not widget.get_active()

    def on_cr_item_weights_multiplier_edited(self, _widget, path, text):
        try:
            float(text)
        except ValueError:
            return
        store = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_item_weights')
        store[path][2] = text

    def on_btn_pokemon_copy_for_starters(self, source):
        destination = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_monsters_starters')
        values = [x[2] for x in source]
        for idx, x in enumerate(iter_tree_model(destination)):
            x[2] = values[idx]

    def on_btn_pokemon_copy_for_monsters(self, source):
        destination = builder_get_assert(self.builder, Gtk.ListStore, 'store_tree_monsters_monsters')
        values = [x[2] for x in source]
        for idx, x in enumerate(iter_tree_model(destination)):
            x[2] = values[idx]

    def on_btn_pokemon_reset(self, pool):
        for x in pool:
            x[2] = x[0] in DEFAULTMONSTERPOOL

    def on_btn_pokemon_select_none(self, pool):
        for x in pool:
            x[2] = False

    def on_btn_rom_clicked(self, *args):
        self.show_info("The input file must be an EU or US .nds ROM of Explorers of Sky, which is not included in the "
                       "randomizer, you must acquire it yourself. Wii U Virtual Console ROMs are not supported.\n"
                       "Re-randomizing a ROM that has already been randomized is not supported and might not work "
                       "properly.")

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
            assert fn is not None
            self.chosen_file = fn
            builder_get_assert(self.builder, Gtk.Label, 'label_rom').set_text(os.path.basename(fn))

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
            assert fn is not None
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
            assert fn is not None
            if '.' not in fn:
                fn += '.json'
            with open_utf8(fn, 'w') as f:
                try:
                    json.dump(self.ui_reader.read(), f, indent=4, cls=EnumJsonEncoder, ensure_ascii=False)
                except Exception as err:
                    tb = ""
                    if not isinstance(err, ValidationError) and not isinstance(err, YAMLError):
                        tb = traceback.format_exc()
                        print(tb)
                    self.display_error(f"Error saving these settings:\n{err}\n{tb}")

    def on_about_clicked(self, *args):
        about = builder_get_assert(self.builder, Gtk.AboutDialog, "about_dialog")
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

        self.show_info("Choose the folder where you want to save the randomized ROM. You also need to give it a name. "
                       "For Windows users, do not try to save it inside Program Files as it might not work.")

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
            assert out_fn is not None
            clear_script_cache()
            if '.' not in out_fn:
                out_fn += '.nds'
            try:
                builder_get_assert(self.builder, Gtk.Button, 'progress_close').set_sensitive(False)
                progress_bar = builder_get_assert(self.builder, Gtk.ProgressBar, 'progress_bar')
                progress_label = builder_get_assert(self.builder, Gtk.Label, 'progress_label')
                progress_diag = builder_get_assert(self.builder, Gtk.Dialog, 'progress')
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
                    builder_get_assert(self.builder, Gtk.Button, 'progress_close').set_sensitive(True)
                    if randomizer.error:
                        img = builder_get_assert(self.builder, Gtk.Image, 'img_portrait_duskako')
                        img.set_from_file(os.path.join(data_dir(), 'duskako_sad.png'))
                        traceback_str = ''.join(traceback.format_exception(*randomizer.error))
                        progress_label.set_text(f"Error: {traceback_str}")
                        progress_diag.set_title('Randomizing failed!')
                    else:
                        assert out_fn is not None
                        rom.saveToFile(out_fn, updateDeviceCapacity=True)
                        img = builder_get_assert(self.builder, Gtk.Image, 'img_portrait_duskako')
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
                    if not isinstance(err, ValidationError) and not isinstance(err, YAMLError):
                        tb = traceback.format_exc()
                        print(tb)
                    self.display_error(f"There is an error in your settings:\n{err}\n{tb}")
                    return
                # Set the seed
                seed = get_effective_seed(config['seed'])
                random.seed(seed)
                builder_get_assert(self.builder, Gtk.Label, 'seed_label').set_text('Your Seed: ' + str(seed))
                randomizer = RandomizerThread(status, rom, config, seed, GtkFrontend())
                randomizer.start()

                # SHOW DIALOG
                img = builder_get_assert(self.builder, Gtk.Image, 'img_portrait_duskako')
                img.set_from_file(os.path.join(data_dir(), 'duskako_neutral.png'))

                GLib.timeout_add(100, check_done)

                progress_diag.run()
            except BaseException as ex:
                tb = traceback.format_exc()
                print(tb)
                self.display_error(f"Error: {ex}\n{tb}")
                return

    def on_progress_close_clicked(self, *args):
        builder_get_assert(self.builder, Gtk.Dialog, 'progress').hide()

    def on_portrait_close_clicked(self, *args):
        builder_get_assert(self.builder, Gtk.Dialog, 'portrait_debug').hide()

    def on_dismiss_banner_clicked(self, *args):
        if self.banner_hash is not None:
            self.settings.set_hash_last_dismissed_banner(self.banner_hash)
        builder_get_assert(self.builder, Gtk.Box, 'banner_info_wrapper').hide()

    def display_error(self, error_message, error_title='SkyTemple Randomizer - Error'):
        md = Gtk.MessageDialog(parent=self.window,
                               destroy_with_parent=True,
                               message_type=Gtk.MessageType.ERROR,
                               buttons=Gtk.ButtonsType.OK,
                               text=error_message,
                               title=error_title)
        md.run()
        md.destroy()

    def show_info(self, info, *args):
        md = Gtk.MessageDialog(parent=self.window,
                               destroy_with_parent=True,
                               message_type=Gtk.MessageType.INFO,
                               buttons=Gtk.ButtonsType.OK,
                               text=info)
        md.run()
        md.destroy()

    def _check_for_updates(self):
        try:
            new_version = check_newest_release(ReleaseType.SKYTEMPLE_RANDOMIZER)
            if packaging.version.parse(version()) < packaging.version.parse(new_version):
                builder_get_assert(self.builder, Gtk.Label, 'update_new_version').set_text(new_version)
                return
        except Exception:
            pass
        # else/except:
        builder_get_assert(self.builder, Gtk.Box, 'update_info').hide()

    def _check_for_banner(self):
        try:
            img_banner, url = get_event_banner()
            if img_banner is not None:
                self.banner_hash = hashlib.sha1(img_banner).hexdigest()
                if self.banner_hash != self.settings.get_hash_last_dismissed_banner():
                    input_stream = Gio.MemoryInputStream.new_from_data(img_banner, None)
                    pixbuf = GdkPixbuf.Pixbuf.new_from_stream(input_stream, None)
                    image = Gtk.Image()
                    image.show()
                    image.set_from_pixbuf(pixbuf)

                    def open_web(*args):
                        if url is not None:
                            webbrowser.open_new_tab(url)

                    def cursor_change(w: Gtk.Widget, evt: Gdk.EventCrossing):
                        cursor = None
                        if evt.get_event_type() == Gdk.EventType.ENTER_NOTIFY:
                            cursor = Gdk.Cursor.new_from_name(w.get_display(), "pointer")
                        elif evt.get_event_type() == Gdk.EventType.LEAVE_NOTIFY:
                            cursor = Gdk.Cursor.new_from_name(w.get_display(), "default")
                        if cursor is not None:
                            window = w.get_window()
                            if window is not None:
                                window.set_cursor(cursor)
                    b_info = builder_get_assert(self.builder, Gtk.EventBox, 'banner_info')
                    b_info.connect('button-release-event', open_web)
                    b_info.connect('enter-notify-event', cursor_change)
                    b_info.connect('leave-notify-event', cursor_change)
                    b_info.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
                    b_info.add(image)
                    return
        except Exception:
            pass
        # else/except:
        builder_get_assert(self.builder, Gtk.Box, 'banner_info_wrapper').hide()


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
    default_screen = Gdk.Screen.get_default()
    if default_screen is not None:
        Gtk.StyleContext.add_provider_for_screen(
            default_screen, style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    # Load main window + controller
    app = MainController()
    sys.exit(app.run(sys.argv))


def _load_theme():
    settings = Gtk.Settings.get_default()
    if settings is not None:
        settings.set_property("gtk-theme-name", 'Arc-Dark')


if __name__ == '__main__':
    # TODO: At the moment doesn't support any cli arguments.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
