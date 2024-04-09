# -*- mode: python ; coding: utf-8 -*-
import os
import sys

pkg_path = os.path.abspath(os.path.join("..", "skytemple_randomizer"))
site_packages = next(p for p in sys.path if "site-packages" in p)

additional_datas = [
    (os.path.join(pkg_path, "data"), "data"),
    (os.path.join(pkg_path, "frontend", "gtk", "widgets", "*.ui"), "."),
    (os.path.join(pkg_path, "frontend", "gtk", "*.css"), "."),
    (
        os.path.join(site_packages, "skytemple_icons", "hicolor"),
        "skytemple_icons/hicolor",
    ),
    (
        os.path.join(site_packages, "skytemple_files", "_resources"),
        "skytemple_files/_resources",
    ),
    (os.path.join(site_packages, "certifi", "cacert.pem"), "certifi"),
    (os.path.join(".", "armips"), "skytemple_files/_resources"),
]

additional_binaries = [
    (os.path.join(site_packages, "skytemple_rust*.so"), "."),
]

block_cipher = None


a = Analysis(
    ["../skytemple_randomizer/frontend/gtk/main.py"],
    pathex=[os.path.abspath(os.path.join("..", "skytemple_randomizer"))],
    binaries=additional_binaries,
    datas=additional_datas,
    hiddenimports=[
        "packaging.version",
        "packaging.specifiers",
        "packaging.requirements",
        "packaging.markers",
        "certifi",
    ],
    hookspath=None,
    hooksconfig={
        "gi": {
            "module-versions": {
                "Gtk": "4.0",
                "Adw": "1",
            },
        },
    },
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="run_skytemple",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="skytemple_randomizer",
)

app = BUNDLE(
    coll,
    name="SkyTemple Randomizer.app",
    icon="skytemple_randomizer.icns",
    version=os.getenv("PACKAGE_VERSION", "0.0.0"),
    bundle_identifier="de.parakoopa.skytemple_randomizer",
    info_plist={"LSEnvironment": {"LC_CTYPE": "en_US.UTF-8"}},
)
