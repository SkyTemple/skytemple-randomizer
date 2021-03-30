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
from os import listdir
from os.path import exists, isfile, isdir, join
from re import match

import sh
from pythonforandroid.logger import info_main, info, shprint
from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe
import os

from pythonforandroid.util import current_directory, ensure_dir


class PythonIgraphVersionRecipe(CppCompiledComponentsPythonRecipe):
    version = 'master'
    url = 'git+https://github.com/igraph/python-igraph.git' #  'https://github.com/igraph/python-igraph/releases/download/{version}/python-igraph-{version}.tar.gz'

    call_hostpython_via_targetpython = False
    depends = ['setuptools']
    conflicts = []

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        toolchain = self.ctx.ndk_dir + '/toolchains/llvm/prebuilt/linux-x86_64'
        target = 'armv7a-linux-androideabi'
        api = '21'
        env['AR'] = f'{toolchain}/bin/llvm-ar'
        env['AS'] = f'{toolchain}/bin/{target}{api}-clang'
        env['RANLIB'] = f'{toolchain}/bin/arm-linux-androideabi-ranlib'
        env['STRIP'] = f'{toolchain}/bin/llvm-strip'
        env['IGRAPH_CMAKE_EXTRA_ARGS'] = f'-DCMAKE_SYSTEM_NAME={target} ' \
                                         f'-DF2C_EXTERNAL_ARITH_HEADER={os.path.join(os.path.dirname(__file__), "arith.h")} ' \
                                         f'-DIGRAPH_GRAPHML_SUPPORT=0'
        env['LDFLAGS'] += env.get('LDFLAGS', '') + " -l{}".format(
                self.stl_lib_name
            )
        env['MAKE'] = 'make -j2'
        os.system('ls -la /usr/local/lib/android/sdk/ndk/19.2.5345600/sources/cxx-stl/llvm-libc++/include')
        exit(1)
        # Fix PATH:
        env['PATH'] = env['PATH'].replace('\n', '')
        return env

    def unpack(self, arch):
        """Only overwritten to keep the .git directory..."""
        info_main('Unpacking {} for {}'.format(self.name, arch))

        build_dir = self.get_build_container_dir(arch)

        user_dir = os.environ.get('P4A_{}_DIR'.format(self.name.lower()))
        if user_dir is not None:
            info('P4A_{}_DIR exists, symlinking instead'.format(
                self.name.lower()))
            if exists(self.get_build_dir(arch)):
                return
            shprint(sh.rm, '-rf', build_dir)
            shprint(sh.mkdir, '-p', build_dir)
            shprint(sh.rmdir, build_dir)
            ensure_dir(build_dir)
            shprint(sh.cp, '-a', user_dir, self.get_build_dir(arch))
            return

        if self.url is None:
            info('Skipping {} unpack as no URL is set'.format(self.name))
            return

        filename = shprint(
            sh.basename, self.versioned_url).stdout[:-1].decode('utf-8')
        ma = match(u'^(.+)#[a-z0-9_]{3,}=([0-9a-f]{32,})$', filename)
        if ma:                  # fragmented URL?
            filename = ma.group(1)

        with current_directory(build_dir):
            directory_name = self.get_build_dir(arch)

            if not exists(directory_name) or not isdir(directory_name):
                extraction_filename = join(
                    self.ctx.packages_path, self.name, filename)
                if isfile(extraction_filename):
                    raise NotImplementedError("Not implemented, remove custom unpack.")
                elif isdir(extraction_filename):
                    os.mkdir(directory_name)
                    for entry in listdir(extraction_filename):
                        shprint(sh.cp, '-Rv',
                                join(extraction_filename, entry),
                                directory_name)
                else:
                    raise Exception(
                        'Given path is neither a file nor a directory: {}'
                        .format(extraction_filename))

            else:
                info('{} is already unpacked, skipping'.format(self.name))

recipe = PythonIgraphVersionRecipe()
