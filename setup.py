# Copyright (c) Sean Vig 2018

import subprocess
import sys

from setuptools import setup

sys.path.insert(0, "wlroots")

subprocess.run(["python", "wlroots/include/check_headers.py", "--generate"])
setup(
    cffi_modules=["wlroots/ffi_build.py:ffi_builder"],
)
