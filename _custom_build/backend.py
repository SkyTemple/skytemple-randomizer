# mypy: ignore-errors
import platform
import subprocess

from setuptools import build_meta as _orig
from setuptools.build_meta import *  # noqa: F403


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """
    Build the wheel, but before: Build all UI files and MO files
    """
    print("Building Blueprint files and locale message files...")
    if platform.system() == "Windows":
        subprocess.run(["powershell.exe", r".\_custom_build\_build.ps1"], check=True)
    else:
        subprocess.run(["make"], check=True)
    return _orig.build_wheel(wheel_directory, config_settings, metadata_directory)
