# Copyright (c) Sean Vig 2018

import sys

from setuptools import setup


pywlroots_version = "0.0.1"

description = "Python binding to the wlroots library using cffi"

if "_cffi_backend" in sys.builtin_module_names:
    import _cffi_backend
    if _cffi_backend.__version__ < "1.0.0":
        raise RuntimeError("PyPy version is too old, must support cffi 1.0.0")
    requires_cffi = "cffi=={}".format(_cffi_backend.__version__)
else:
    requires_cffi = "cffi>=1.0.0"

dependencies = ["pywayland", requires_cffi]

classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "Operating System :: POSIX",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Desktop Environment :: Window Managers",
    "Topic :: Software Development :: Libraries",
]

modules = [
    "wlroots",
]

setup(
    name="pywlroots",
    version=pywlroots_version,
    author="Sean Vig",
    author_email="sean.v.775@gmail.com",
    url="https://github.com/flacjacket/pywlroots",
    cffi_modules=["wlroots/ffi_build.py:ffi_builder"],
    classifiers=classifiers,
    description=description,
    install_requires=dependencies,
    packages=modules,
    setup_requires=dependencies,
)
