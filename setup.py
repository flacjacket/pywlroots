# Copyright (c) Sean Vig 2018

import sys

from distutils.command.build import build
from setuptools import setup
from setuptools.command.install import install


NO_SETUP_REQUIRES_ARGUMENTS = ["--help", "-h", "sdist"]


class DummyBuild(build):
    def run(self):
        raise RuntimeError("Requested running build")


class DummyInstall(install):
    def run(self):
        raise RuntimeError("Requested running install")


def keywords_with_side_effects(argv):
    if any(arg in NO_SETUP_REQUIRES_ARGUMENTS for arg in argv):
        return {"cmdclass": {"build": DummyBuild, "install": DummyInstall}}
    else:
        return {
            "setup_requires": ["cffi>=1.12.0", "pywayland>=0.1.1", "xkbcommon>=0.2"],
            "cffi_modules": ["wlroots/ffi_build.py:ffi_builder"],
        }


sys.path.insert(0, "wlroots")

setup(**keywords_with_side_effects(sys.argv))
