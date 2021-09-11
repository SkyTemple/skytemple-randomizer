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
from pythonforandroid.recipe import PythonRecipe


class ExplorerScriptRecipe(PythonRecipe):
    url = 'https://github.com/SkyTemple/explorerscript/archive/refs/tags/{version}.tar.gz'
    master_url = 'https://github.com/SkyTemple/explorerscript/archive/refs/heads/master.tar.gz'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False

    @property
    def versioned_url(self):
        if self.version == "master":
            return self.master_url
        return super().versioned_url


recipe = ExplorerScriptRecipe()
