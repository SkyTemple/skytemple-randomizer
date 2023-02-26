# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import PurePosixPath, Path

pkg_path = os.path.abspath(os.path.join('..', 'skytemple_randomizer'))
site_packages = next(p for p in sys.path if 'site-packages' in p)

mingw = os.getenv("MINGW_VERSION", "mingw64")

additional_files = []
additional_datas = [
    (os.path.join(pkg_path, 'data'), 'data'),
    (os.path.join(pkg_path, 'frontend', 'gtk', '*.glade'), '.'),
    (os.path.join(pkg_path, 'frontend', 'gtk', '*.css'), '.'),
    (os.path.join(site_packages, 'skytemple_icons', 'hicolor'), 'skytemple_icons/hicolor'),
    (os.path.join(site_packages, 'skytemple_files', '_resources'), 'skytemple_files/_resources'),
    (os.path.join(site_packages, 'certifi', 'cacert.pem'), 'certifi'),
    (os.path.join('.', 'armips.exe'), 'skytemple_files/_resources'),

    # These aren't auto dectected for some reason :(
    (os.path.join("D:/", "a", "_temp", "msys64", mingw, 'share', 'fontconfig'), 'share/fontconfig'),
    (os.path.join("D:/", "a", "_temp", "msys64", mingw, 'share', 'glib-2.0'), 'share/glib-2.0'),
    (os.path.join("D:/", "a", "_temp", "msys64", mingw, 'share', 'gtksourceview-4'), 'share/gtksourceview-4'),
    (os.path.join("D:/", "a", "_temp", "msys64", mingw, 'share', 'icons'), 'share/icons'),
    (os.path.join("D:/", "a", "_temp", "msys64", mingw, 'share', 'locale'), 'share/locale'),
    (os.path.join("D:/", "a", "_temp", "msys64", mingw, 'share', 'themes'), 'share/themes'),

    # Themes
    ('Arc', 'share/themes/Arc'),
    ('Arc-Dark', 'share/themes/Arc-Dark')
]

additional_binaries = [
    (os.path.join("D:/", "a", "_temp", "msys64", mingw, "bin", "libcrypto*.dll"), '.'),
    (os.path.join("D:/", "a", "_temp", "msys64", mingw, "bin", "libssl-1_1*.dll"), '.'),
    (os.path.join("D:/", "a", "_temp", "msys64", mingw, "bin", "libgmp-10.dll"), '.'),
    (os.path.join(site_packages, 'skytemple_rust*.pyd'), '.'),
]

block_cipher = None


a = Analysis(['../skytemple_randomizer/frontend/gtk/main.py'],
             pathex=[os.path.abspath(os.path.join('..', 'skytemple_randomizer'))],
             binaries=additional_binaries,
             datas=additional_datas,
             hiddenimports=['pkg_resources.py2_warn', 'packaging.version', 'packaging.specifiers',
                            'packaging.requirements', 'packaging.markers', '_sysconfigdata__win32_', 'win32api',
                            'certifi'],
             hookspath=[os.path.abspath(os.path.join('.', 'hooks'))],
             hooksconfig={
                 "gi": {
                     "module-versions": {
                         "Gtk": "3.0",
                         "GtkSource": "4",
                     },
                 },
             },
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='skytemple_randomizer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon=os.path.abspath(os.path.join('.', 'skytemple_randomizer.ico')))

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               additional_files,
               strip=False,
               upx=True,
               upx_exclude=[],
               version=os.getenv('PACKAGE_VERSION', '0.0.0'),
               name='skytemple_randomizer')
