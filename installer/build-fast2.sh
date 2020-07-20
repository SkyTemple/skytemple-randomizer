#!/bin/sh
# I don't get it. If I put this in the same script, it doesn't work.
pyinstaller skytemple_randomizer.spec
sleep 20

# Remove unnesecary things
rm dist/skytemple_randomizer/share/doc/* -rf
rm dist/skytemple_randomizer/share/gtk-doc/* -rf
rm dist/skytemple_randomizer/share/man/* -rf
rm dist/skytemple_randomizer/share/themes/* -rf

# Install additional themes
cp -a bundling/themes/* dist/skytemple_randomizer/share/themes/
