# Copyright (c) Sean Vig 2018

from __future__ import absolute_import

from ._ffi import ffi, lib

__wlroots_version__ = "{}.{}.{}".format(
    lib.WLR_VERSION_MAJOR,
    lib.WLR_VERSION_MICRO,
    lib.WLR_VERSION_MINOR,
)
