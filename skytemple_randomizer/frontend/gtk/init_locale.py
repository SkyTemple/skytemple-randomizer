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
import platform

from skytemple_randomizer.data_dir import data_dir

APP = "org.skytemple.Randomizer"


# Setup locale :(
# TODO: Maybe want to get rid of duplication between SkyTemple and the Randomizer. And clean this up in general...
def init_locale():
    system = platform.system()
    LOCALE_DIR = os.path.abspath(os.path.join(data_dir(), "locale"))
    if hasattr(locale, "bindtextdomain"):
        libintl = locale
        lang, enc = locale.getlocale()
    elif system == "Windows":
        import ctypes
        import ctypes.util

        failed_to_set_locale = False
        if os.getenv("LANG") is None:
            try:
                lang, enc = locale.getlocale()
                os.environ["LANG"] = f"{lang}.{enc}"
                ctypes.cdll.msvcrt._putenv(f"LANG={lang}.{enc}")
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
                    locale.setlocale(locale.LC_ALL, lang)

                    # trying to get locale may fail now, we catch this.
                    locale.getlocale()
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
            libintl = ctypes.cdll.LoadLibrary(libintl_loc)  # type: ignore
        libintl_loc = os.path.join(os.path.dirname(__file__), "intl.dll")
        if os.path.exists(libintl_loc):
            libintl = ctypes.cdll.LoadLibrary(libintl_loc)  # type: ignore
        else:
            try:
                libintl = ctypes.cdll.LoadLibrary(ctypes.util.find_library("libintl-8"))  # type: ignore
            except Exception:
                libintl = ctypes.cdll.LoadLibrary(ctypes.util.find_library("intl"))  # type: ignore
    elif system == "Darwin":
        import ctypes
        import subprocess

        # look away! Avert your eyes!
        proc = subprocess.Popen(
            ["defaults", "read", "NSGlobalDomain", "AppleLocale"],
            stdout=subprocess.PIPE,
        )
        lang = proc.stdout.read()  # type: ignore
        if isinstance(lang, bytes):
            lang = str(lang, "ascii")  # type: ignore
        lang = lang.strip("\n")  # type: ignore
        locale.setlocale(locale.LC_ALL, lang)
        print(f"LANG={lang}")
        os.environ["LANG"] = lang
        libintl = ctypes.cdll.LoadLibrary("libintl.8.dylib")  # type: ignore
    if not os.getenv("LC_ALL"):
        try:
            os.environ["LC_ALL"] = lang  # type: ignore
            locale.setlocale(locale.LC_ALL, lang)
        except locale.Error:
            print("Failed setting locale")
    libintl.bindtextdomain(APP, LOCALE_DIR)  # type: ignore
    try:
        libintl.bind_textdomain_codeset(APP, "UTF-8")  # type: ignore
        libintl.libintl_setlocale(0, lang)  # type: ignore
    except Exception:
        pass
    libintl.textdomain(APP)
    gettext.bindtextdomain(APP, LOCALE_DIR)
    gettext.textdomain(APP)
    try:
        if os.environ["LC_ALL"] != "C":
            loc = os.environ["LC_ALL"]
            if loc == "":
                loc = locale.getlocale()[0]  # type: ignore
            from skytemple_files.common.i18n_util import reload_locale

            base_loc = loc.split("_")[0]
            fallback_loc = base_loc
            for subdir in next(os.walk(LOCALE_DIR))[1]:
                if subdir.startswith(base_loc):
                    fallback_loc = subdir
                    break
            reload_locale(
                APP,
                localedir=LOCALE_DIR,
                main_languages=list({loc, base_loc, fallback_loc}),
            )
    except Exception as ex:
        print("Failed setting up Python locale.")
        print(ex)
