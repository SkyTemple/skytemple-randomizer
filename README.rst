|logo|

SkyTemple Randomizer
====================

|build| |crowdin| |pypi-version| |pypi-downloads| |pypi-license| |pypi-pyversions| |discord|

.. |logo| image:: https://raw.githubusercontent.com/SkyTemple/skytemple/master/skytemple/data/icons/hicolor/256x256/apps/skytemple.png

.. |crowdin| image:: https://badges.crowdin.net/skytemple/localized.svg
    :target: https://crowdin.com/project/skytemple
    :alt: Localization Progress

.. |build| image:: https://img.shields.io/github/actions/workflow/status/SkyTemple/skytemple-randomizer/build-test-publish.yml
    :target: https://pypi.org/project/skytemple-randomizer/
    :alt: Build Status

.. |pypi-version| image:: https://img.shields.io/pypi/v/skytemple-randomizer
    :target: https://pypi.org/project/skytemple-randomizer/
    :alt: Version

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/skytemple-randomizer
    :target: https://pypi.org/project/skytemple-randomizer/
    :alt: Downloads

.. |pypi-license| image:: https://img.shields.io/pypi/l/skytemple-randomizer
    :alt: License (GPLv3)

.. |pypi-pyversions| image:: https://img.shields.io/pypi/pyversions/skytemple-randomizer
    :alt: Supported Python versions

.. |discord| image:: https://img.shields.io/discord/710190644152369162?label=Discord
    :target: https://discord.gg/skytemple
    :alt: Discord

.. |kofi| image:: https://www.ko-fi.com/img/githubbutton_sm.svg
    :target: https://ko-fi.com/I2I81E5KH
    :alt: Ko-Fi

Randomizer for Pokémon Mystery Dungeon Explorers of Sky.

It is available for Linux, macOS and Windows.

GTK frontend
------------
When installing from source, you probably want to install the "gtk" extra,
in order to have the actual GUI functional.

The GTK frontend requires GTK 4.14+, all related libraries and libadwaita 1.5+ to be
installed.

Build
~~~~~
In addition to normally installing the Python package in dev mode, you also need to make sure you
have all submodules checked out. After this you need to compile all MO files (localizations) and Blueprint
Files to XML UI files. To do that:

- Linux, possibly MacOS: ``make``
- Linux/MacOS without make: ``./build-blp-to-ui.sh && installer/generate-mo.sh``
- Windows: ``.\build-blp-to-ui.ps1`` with PowerShell and ``installer\generate-mo.sh`` with an MSys2 environment bash shell. Gettext must be available.

If you are working with the UI files you may want to use the Blueprint Compiler Language Server or setup file watchers
to compile BLP files to UI files. More info about Blueprint Compiler can be found on its website:
https://jwestman.pages.gitlab.gnome.org/blueprint-compiler/

Downloads
---------
- Windows: https://projectpokemon.org/home/files/file/4235-skytemple-randomizer/
- MacOS: https://projectpokemon.org/home/files/file/4235-skytemple-randomizer/
- Linux: https://flathub.org/apps/details/org.skytemple.Randomizer

For build instructions in general see the SkyTemple_ repository.

You probably want to install the optional `gtk` extra if you want a frontend. Without it (as of now)
"only" the API is available and you can use Randomizer as a library. See the `skytemple_randomizer.randomizer_thread`
for the entrypoint (specifically the class `RandomizerThread`). You will need to implement your own `AbstractFrontend`.
The passed in `Status` object can be used to monitor the status of the randomization for progress display. See the
GTK implementation for reference on how to use all of this.

Without the `gtk` extra, importing anything from `skytemple_randomizer.frontend.gtk` may fail. Running the script
`skytemple_randomizer` may also fail. You will need to use the API instead.

|flathub_badge|

.. _Flathub: https://flathub.org/apps/details/org.skytemple.SkyTemple

.. |flathub_badge| image:: https://flathub.org/assets/badges/flathub-badge-en.png
    :target: https://flathub.org/apps/details/org.skytemple.SkyTemple
    :alt: Install on Flathub
    :width: 240px

.. _SkyTemple: https://github.com/SkyTemple/SkyTemple

Source repository for the Flatpak: https://github.com/flathub/org.skytemple.Randomizer

|kofi|
