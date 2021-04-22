# Copyright (c) Sean Vig 2018

from ._ffi import ffi, lib  # noqa: F401

__wlroots_version__ = "{}.{}.{}".format(
    lib.WLR_VERSION_MAJOR,
    lib.WLR_VERSION_MICRO,
    lib.WLR_VERSION_MINOR,
)

__version__ = "0.2.2"
