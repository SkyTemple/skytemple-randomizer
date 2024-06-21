import os
import platform
import sys


def data_dir():
    if getattr(sys, "frozen", False):
        system = platform.system()
        if system == "Windows":
            return os.path.join(os.path.dirname(sys.executable), "_internal", "data")
        elif system == "Darwin":
            return os.path.join(os.path.dirname(sys.executable), "..", "Resources", "data")
        else:
            return os.path.join(os.path.dirname(sys.executable), "data")
    return os.path.join(os.path.dirname(__file__), "data")
