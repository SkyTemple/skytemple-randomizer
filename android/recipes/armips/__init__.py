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
from os.path import join, exists
from shutil import copy, move

import sh
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory


class ArmipsRecipe(Recipe):
    version = 'master'
    url = 'git+https://github.com/Kingcom/armips.git'
    built_libraries = {'libarmips.so': '.'}

    def should_build(self, arch):
        armips = join(self.get_build_dir(arch.arch), 'libarmips.so')

        if not exists(armips):
            return True

        return False

    def build_arch(self, arch, *extra_args):
        super().build_arch(arch)

        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(
                sh.cmake,
                f'-DCMAKE_TOOLCHAIN_FILE={self.ctx.ndk_dir}/build/cmake/android.toolchain.cmake',
                f'-DANDROID_ABI={arch}',
                f'-DANDROID_NATIVE_API_LEVEL={self.ctx.ndk_api}',
                f'-DCMAKE_BUILD_TYPE=Release CMakeLists.txt',
                *extra_args, _env=env
            )
            shprint(
                sh.cmake, '--build', '.',
                _env=env
            )
            # a bit of a dirty workaround
            move(join(self.get_build_dir(arch.arch), "armips"), join(self.get_build_dir(arch.arch), "libarmips.so"))


recipe = ArmipsRecipe()
