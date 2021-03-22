#!/usr/bin/env python
import os
import shutil
import sys

IGNORE_REQS = ['PyGObject', 'pycairo']
ADDITIONAL_REQS = ['pillow == 7.0.0']

from pythonforandroid.util import BuildInterruptingException, handle_build_exception

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(__file__), '..'
)))
from setup import __version__, install_requires

from pkg_resources import WorkingSet, Requirement

gen = (f'"{x}"'.replace(" ", "") for x in install_requires + ADDITIONAL_REQS)
os.system(f'pip3 install {(" ".join(gen))}')
recursive_reqs = WorkingSet().resolve([Requirement(x) for x in install_requires + ADDITIONAL_REQS], replace_conflicting=True)
absp = os.getcwd()
os.chdir(os.path.join('..', 'skytemple_randomizer', 'frontend', 'common_web'))
os.system(f'npm install')
os.system(f'npm run-script build')
os.chdir(absp)
# fix for igraph
install_requires = [f'{x.project_name}=={x.version if x.project_name != "python-igraph" else "master"}' for x in recursive_reqs if x.project_name not in IGNORE_REQS]

options = {
    'dist-name': 'skytemple_randomizer',
    'package': 'org.skytemple.randomizer',
    'name': 'SkyTemple Randomizer',
    'version': __version__,
    'bootstrap': 'webview',
    'requirements': 'tornado>=6.1,' + ','.join(install_requires).replace(' ', ''),
    'sdk-dir': os.getenv('ANDROIDSDK', '/opt/android-sdk'),
    'ndk-dir': os.getenv('ANDROIDNDK', '/opt/android-sdk/ndk/19.2.5345600'),
    'android-api': int(os.getenv('ANDROIDAPI', '27')),
    'ndk-api': int(os.getenv('NDKAPI', '21')),
    'port': 44235,
    'private': '_prebuild',
    'local-recipes': './recipes'
}

os.makedirs('_prebuild')
try:
    # sudo cp /opt/android-sdk/ndk/19.2.5345600/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/arm-linux-androideabi/libunwind.a /opt/android-sdk/ndk/19.2.5345600/platforms/android-21/arch-arm/usr/lib/libunwind.a
    shutil.copy('main.py', '_prebuild/main.py')
    shutil.copytree('../skytemple_randomizer', '_prebuild/skytemple_randomizer')
    shutil.rmtree('_prebuild/skytemple_randomizer/frontend/common_web/node_modules')
    os.chdir(os.path.join('_prebuild', 'skytemple_randomizer', 'frontend', 'common_web'))
    os.system(f'npm install --only=prod')
    os.chdir(absp)

    sys.argv = ['p4a', 'apk']
    for k, v in options.items():
        sys.argv += [f'--{k}', str(v)]

    try:
        from pythonforandroid.toolchain import ToolchainCL
        ToolchainCL()
    except BuildInterruptingException as exc:
        handle_build_exception(exc)
finally:
    shutil.rmtree(os.path.join(absp, '_prebuild'))
