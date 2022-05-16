#!/usr/bin/env python
import os
import shutil
import sys
import traceback

IGNORE_REQS = ['PyGObject', 'pycairo']
ADDITIONAL_REQS = ['pillow == 7.0.0']

from pythonforandroid.util import BuildInterruptingException, handle_build_exception

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(__file__), '..'
)))
from setup import __version__, install_requires

from pkg_resources import WorkingSet, Requirement

USE_MASTER_LIST = [
    "python-igraph"  # fix for igraph
]

if os.getenv('SKYTEMPLE_USE_MASTER', False):
    USE_MASTER_LIST += [
        "skytemple-files", "explorerscript"
    ]

gen = (f'"{x}"'.replace(" ", "") for x in install_requires + ADDITIONAL_REQS)
os.system(f'pip3 install {(" ".join(gen))}')
recursive_reqs = WorkingSet().resolve([Requirement(x) for x in install_requires + ADDITIONAL_REQS], replace_conflicting=True)
absp = os.getcwd()
os.chdir(os.path.join('..', 'skytemple_randomizer', 'frontend', 'common_web'))
os.system(f'npm install')
os.system(f'npm run-script build')
os.chdir(absp)
install_requires = [f'{x.project_name}=={x.version if x.project_name not in USE_MASTER_LIST else "master"}'
                    for x in recursive_reqs if x.project_name not in IGNORE_REQS]
install_requires += ['armips']  # we also need armips

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
    'ndk-api': int(os.getenv('NDKAPI', '23')),
    'port': 44235,
    'private': '_prebuild',
    'local-recipes': './recipes'
}

error = False
os.makedirs('_prebuild')
try:
    shutil.copy('main.py', '_prebuild/main.py')
    shutil.copytree('../skytemple_randomizer', '_prebuild/skytemple_randomizer')
    with open('_prebuild/skytemple_randomizer/data/VERSION', 'w') as f:
        f.write(__version__)
    shutil.rmtree('_prebuild/skytemple_randomizer/frontend/common_web/node_modules')
    os.chdir(os.path.join('_prebuild', 'skytemple_randomizer', 'frontend', 'common_web'))
    os.system(f'npm install --only=prod')
    os.chdir(absp)

    sys.argv = ['p4a', 'apk', '--arch', 'armeabi-v7a']
    for k, v in options.items():
        sys.argv += [f'--{k}', str(v)]
    sys.argv += ['--no-optimize-python']
    if os.getenv('SKYTEMPLE_BUILD_PRODUCTION', False):
        sys.argv += ['--release', '--sign']

    try:
        from pythonforandroid.toolchain import ToolchainCL
        ToolchainCL()
    except BuildInterruptingException as exc:
        handle_build_exception(exc)
        error = True
except Exception as ex:
    traceback.print_exc()
    error = True
finally:
    shutil.rmtree(os.path.join(absp, '_prebuild'))

if error:
    print("Build error.")
    exit(1)
