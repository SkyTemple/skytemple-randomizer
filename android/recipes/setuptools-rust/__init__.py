#  Copyright 2020-2023 Capypara and the SkyTemple Contributors
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


class SetuptoolsRustRecipe(PythonRecipe):
    version = 'v1.3.0'
    url = 'https://github.com/PyO3/setuptools-rust/archive/refs/tags/{version}.tar.gz'

    depends = ['setuptools', 'semantic-version', 'typing_extensions']
    conflicts = []
    call_hostpython_via_targetpython = False
    install_in_hostpython = True
    install_in_targetpython = False

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        env['SETUPTOOLS_SCM_PRETEND_VERSION'] = self.version
        return env

    def get_hostrecipe_env(self, arch=None):
        env = super().get_hostrecipe_env(arch)
        env['SETUPTOOLS_SCM_PRETEND_VERSION'] = self.version
        return env

recipe = SetuptoolsRustRecipe()
