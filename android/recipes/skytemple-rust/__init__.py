#  Copyright 2020-2021 Parakoopa and the SkyTemple Contributors
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
import glob
import os

import sh
from pythonforandroid.logger import info, shprint
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.util import current_directory


class SkyTempleRustRecipe(CompiledComponentsPythonRecipe):
    version = '0.0.1.post0'
    url = 'https://github.com/SkyTemple/skytemple-rust/archive/refs/tags/{version}.tar.gz'

    call_hostpython_via_targetpython = False
    depends = ['toml', 'setuptools-rust', 'setuptools']
    conflicts = []

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        env['RUST_LOG'] = 'debug'
        env['CARGO_TERM_VERBOSE'] = 'verbose'
        env['PKG_CONFIG_ALLOW_CROSS'] = '1'
        env['CARGO_BUILD_TARGET'] = 'armv7-linux-androideabi'
        link_root = self.ctx.python_recipe.link_root(arch)
        env['PYO3_CROSS_LIB_DIR'] = link_root
        env['PYO3_CROSS_INCLUDE_DIR'] = self.ctx.python_recipe.include_root(arch)
        env["LD_LIBRARY_PATH"] = link_root
        env['TARGET'] = 'armv7a-linux-androideabi'
        env['CARGO_TARGET_ARMV7_LINUX_ANDROIDEABI_LINKER'] = self.ctx.ndk_dir + '/toolchains/llvm/prebuilt/linux-x86_64/bin/armv7a-linux-androideabi21-clang'
        env['CARGO_TARGET_ARMV7_LINUX_ANDROIDEABI_AR'] = self.ctx.ndk_dir + '/toolchains/llvm/prebuilt/linux-x86_64/bin/arm-linux-androideabi-ar'
        env['RUSTFLAGS'] = f'-C link-args=-L{link_root} -lpython3.8'
        assert os.path.exists(env['PYO3_CROSS_LIB_DIR']), env['PYO3_CROSS_LIB_DIR']
        assert os.path.exists(env['PYO3_CROSS_INCLUDE_DIR']), env['PYO3_CROSS_INCLUDE_DIR']
        return env

    def build_compiled_components(self, arch):
        info('Building compiled components in {}'.format(self.name))

        env = self.get_recipe_env(arch)
        hostpython = sh.Command(self.hostpython_location)
        with current_directory(self.get_build_dir(arch.arch)):
            if self.install_in_hostpython:
                shprint(hostpython, 'setup.py', 'clean', '--all', _env=env)
            shprint(hostpython, 'setup.py', self.build_cmd, '-v',
                    _env=env, *self.setup_extra_args)
            build_dir = glob.glob('build/lib/*')[0]
            shprint(sh.find, build_dir, '-name', '"*.o"', '-exec',
                    env['STRIP'], '{}', ';', _env=env)


recipe = SkyTempleRustRecipe()
