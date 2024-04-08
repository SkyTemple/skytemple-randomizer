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
import gettext
import locale
import os
import sys

from skytemple_randomizer.data_dir import data_dir


# Setup locale :(
# TODO: Maybe want to get rid of duplication between SkyTemple and the Randomizer. And clean this up in general...
def init_locale():
    LOCALE_DIR = os.path.abspath(os.path.join(data_dir(), "locale"))
    if sys.platform.startswith("win"):
        import ctypes
        import ctypes.util

        failed_to_set_locale = False
        if os.getenv("LANG") is None:
            lang, enc = locale.getlocale()
            os.environ["LANG"] = f"{lang}.{enc}"
            ctypes.cdll.msvcrt._putenv(f"LANG={lang}.{enc}")
            try:
                locale.setlocale(locale.LC_ALL, f"{lang}.{enc}")
            except Exception:
                failed_to_set_locale = True

        try:
            locale.getlocale()
        except Exception:
            failed_to_set_locale = True

        if failed_to_set_locale:
            failed_to_set_locale = False

            try:
                lang, enc = locale.getlocale()
                print(
                    f"WARNING: Failed processing current locale {lang}.{enc}. Falling back to {lang}"
                )
                # If this returns None for lang, then we bail!
                if lang is not None:
                    os.environ["LANG"] = lang
                    ctypes.cdll.msvcrt._putenv(f"LANG={lang}")
                    try:
                        locale.setlocale(locale.LC_ALL, lang)
                    except Exception:
                        failed_to_set_locale = True

                    try:
                        locale.getlocale()
                    except Exception:
                        failed_to_set_locale = True
                else:
                    failed_to_set_locale = True

                if failed_to_set_locale:
                    print(f"WARNING: Failed to set locale to {lang} falling back to C.")
                    os.environ["LANG"] = "C"
                    ctypes.cdll.msvcrt._putenv("LANG=C")
                    locale.setlocale(locale.LC_ALL, "C")
            except Exception:
                failed_to_set_locale = True

        libintl_loc = os.path.join(os.path.dirname(__file__), "libintl-8.dll")
        if os.path.exists(libintl_loc):
            libintl = ctypes.cdll.LoadLibrary(libintl_loc)
        libintl_loc = os.path.join(os.path.dirname(__file__), "intl.dll")
        if os.path.exists(libintl_loc):
            libintl = ctypes.cdll.LoadLibrary(libintl_loc)
        else:
            try:
                libintl = ctypes.cdll.LoadLibrary(ctypes.util.find_library("libintl-8"))
            except Exception:
                libintl = ctypes.cdll.LoadLibrary(ctypes.util.find_library("intl"))
    elif hasattr(locale, "bindtextdomain"):
        libintl = locale
    elif sys.platform == "darwin":
        import ctypes

        libintl = ctypes.cdll.LoadLibrary("libintl.dylib")
    libintl.bindtextdomain("org.skytemple.Randomizer", LOCALE_DIR)  # type: ignore
    try:
        libintl.bind_textdomain_codeset("org.skytemple.Randomizer", "UTF-8")  # type: ignore
    except Exception:
        pass
    locale.textdomain("org.skytemple.Randomizer")
    libintl.textdomain("org.skytemple.Randomizer")
    gettext.bindtextdomain("org.skytemple.Randomizer", LOCALE_DIR)
    gettext.textdomain("org.skytemple.Randomizer")
    try:
        if "LC_ALL" not in os.environ or os.environ["LC_ALL"] != "C":
            if "LC_ALL" not in os.environ:
                loc = locale.getlocale()[0]  # type: ignore
            else:
                loc = os.environ["LC_ALL"]
            from skytemple_files.common.i18n_util import reload_locale

            if loc is None:
                return

            base_loc = loc.split("_")[0]
            fallback_loc = base_loc
            for subdir in next(os.walk(LOCALE_DIR))[1]:
                if subdir.startswith(base_loc):
                    fallback_loc = subdir
                    break
            reload_locale(
                "org.skytemple.Randomizer",
                localedir=LOCALE_DIR,
                main_languages=list({loc, base_loc, fallback_loc}),
            )
    except Exception as ex:
        print("Failed setting up Python locale.")
        print(ex)
