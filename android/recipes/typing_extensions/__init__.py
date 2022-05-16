#  Copyright 2020-2021 Capypara and the SkyTemple Contributors
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
import os

from pythonforandroid.recipe import PythonRecipe


class TypingExtensionsRecipe(PythonRecipe):
    version = '3.7.4.3'
    url = 'https://skytemple.org/build_deps/typing_extensions.tar.xz'

    depends = ['setuptools']
    conflicts = []
    call_hostpython_via_targetpython = False
    install_in_hostpython = True
    install_in_targetpython = False

recipe = TypingExtensionsRecipe()
