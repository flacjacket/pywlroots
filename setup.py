# Copyright (c) Sean Vig 2018

import glob
import os
import subprocess
import sys

from setuptools import setup
from setuptools.command.sdist import sdist


class SdistClean(sdist):
    def run(self):
        # These files are not tracked by git and as a result check-manifest complains
        # when present, '_build.py' needs to be removed manually since it keeps being
        # created by other setup commands and '.h' files are needen only during build
        files = glob.glob("wlroots/include/*.h")
        files.append("wlroots/_build.py")
        for file in files:
            try:
                os.remove(file)
            except Exception:
                pass
        sdist.run(self)


sys.path.insert(0, "wlroots")

subprocess.run(["python", "wlroots/include/check_headers.py", "--generate"])
setup(
    cmdclass={"sdist": SdistClean},
    cffi_modules=["wlroots/ffi_build.py:ffi_builder"],
)
