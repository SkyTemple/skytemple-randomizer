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


class TilequantRecipe(PythonRecipe):
    version = '0.4.0.post0'
    url = 'https://github.com/SkyTemple/tilequant/archive/refs/tags/{version}.tar.gz'

    call_hostpython_via_targetpython = False
    depends = ['gitpython']
    conflicts = []

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        #env['CC'] = self.ctx.ndk_dir + '/toolchains/llvm/prebuilt/linux-x86_64/bin/clang --target=armv7a-linux-androideabi'
        return env


recipe = TilequantRecipe()
