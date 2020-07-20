Windows Installer
-----------------

This is just a direct fork of the SkyTemple installer directory!

To be used with: https://github.com/exaile/python-gtk3-gst-sdk/tree/master/win_installer.

You need to place the following wheels in this directory (glob patterns, must only match one):

- ``python_igraph-*-cp38-cp38-mingw.whl``
- ``skytemple_rust-*-cp38-cp38-mingw.whl``

Additionally you need to put a stable version of armips_ into this directory
and call it:

- armips.exe
