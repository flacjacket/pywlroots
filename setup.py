# Copyright (c) Sean Vig 2018

import sys
from setuptools import setup


sys.path.insert(0, "wlroots")

setup(
    cffi_modules=["wlroots/ffi_build.py:ffi_builder"],
)
