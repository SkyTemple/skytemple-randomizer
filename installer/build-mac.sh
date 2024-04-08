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

# Build the app
pyinstaller --log-level=DEBUG skytemple-randomizer-mac.spec --noconfirm

# Harfbuzz conflict between PIL and GLib. Manually resolve with GLibs file:
cp /usr/local/lib/libharfbuzz.0.dylib dist/SkyTempleRandomizer.app/Contents/Resources/libharfbuzz.0.dylib

rm skytemple_randomizer.icns

# Since the library search path for the app is wrong, execute a shell script that sets is correctly
# and launches the app instead of launching run_skytemple directly
appdir=dist/SkyTempleRandomizer.app/Contents/MacOS
resdir=dist/SkyTempleRandomizer.app/Contents/Resources

# Change "run_skytemple" to "pre_run_skytemple" in the launcher info to launch the shell script instead of the app
sed -i '' 's/run_skytemple/pre_run_skytemple/' dist/SkyTempleRandomizer.app/Contents/Info.plist

# Create a shell script that sets LD_LIBRARY_PATH and launches SkyTemple
printf '#!/bin/sh\nLD_LIBRARY_PATH="$(dirname $0)" PATH="$PATH:$(dirname $0)/skytemple_files/_resources" "$(dirname $0)/run_skytemple"\n' > $appdir/pre_run_skytemple
chmod +x $appdir/pre_run_skytemple

echo $1 > $resdir/VERSION
echo $1 > $resdir/data/VERSION
