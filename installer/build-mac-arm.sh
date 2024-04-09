#!/bin/bash

# Call with "PACKAGE_VERSION=[version number] ./build-mac.sh"
# The version from the current pip install of SkyTemple is used if no version number is set.
set -e

pip3 install -U certifi

# Create the icon
# https://www.codingforentrepreneurs.com/blog/create-icns-icons-for-macos-apps
mkdir skytemple_randomizer.iconset
icons_path=../skytemple_randomizer/data/icons/hicolor
cp $icons_path/16x16/apps/skytemple_randomizer.png skytemple_randomizer.iconset/icon_16x16.png
cp $icons_path/32x32/apps/skytemple_randomizer.png skytemple_randomizer.iconset/icon_16x16@2x.png
cp $icons_path/32x32/apps/skytemple_randomizer.png skytemple_randomizer.iconset/icon_32x32.png
cp $icons_path/64x64/apps/skytemple_randomizer.png skytemple_randomizer.iconset/icon_32x32@2x.png
cp $icons_path/128x128/apps/skytemple_randomizer.png skytemple_randomizer.iconset/icon_128x128.png
cp $icons_path/256x256/apps/skytemple_randomizer.png skytemple_randomizer.iconset/icon_128x128@2x.png
cp $icons_path/256x256/apps/skytemple_randomizer.png skytemple_randomizer.iconset/icon_256x256.png
cp $icons_path/512x512/apps/skytemple_randomizer.png skytemple_randomizer.iconset/icon_256x256@2x.png
cp $icons_path/512x512/apps/skytemple_randomizer.png skytemple_randomizer.iconset/icon_512x512.png

iconutil -c icns skytemple_randomizer.iconset
rm -rf skytemple_randomizer.iconset

# :(((((((((( PIL ships an old harfbuzz version and PyInstaller is being dumb dumb
cp -f /opt/homebrew/Cellar/harfbuzz/*/lib/libharfbuzz.0.dylib "$VIRTUAL_ENV/lib/python3.12/site-packages/PIL/.dylibs/libharfbuzz.0.dylib"

# Build the app
pyinstaller --log-level=DEBUG skytemple-randomizer-mac.spec --noconfirm

rm skytemple_randomizer.icns
