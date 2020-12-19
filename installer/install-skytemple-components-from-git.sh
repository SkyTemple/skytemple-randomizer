#!/bin/sh
set -e

pip3 uninstall -y explorerscript && pip3 install git+https://github.com/SkyTemple/explorerscript.git
pip3 uninstall -y skytemple-files && pip3 install git+https://github.com/SkyTemple/skytemple-files.git
pip3 uninstall -y skytemple-icons && pip3 install git+https://github.com/SkyTemple/skytemple-icons.git
