import os
import platform
import sys


def data_dir():
    if getattr(sys, "frozen", False):
        if platform.system() == "Windows":
            return os.path.join(os.path.dirname(sys.executable), "_internal", "data")
        else:
            return os.path.join(os.path.dirname(sys.executable), "data")
    return os.path.join(os.path.dirname(__file__), "data")
