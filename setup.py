# Copyright (c) Sean Vig 2018

from setuptools import setup


setup(
    cffi_modules=["wlroots/ffi_build.py:ffi_builder"],
)
