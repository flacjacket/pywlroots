# Copyright (c) Sean Vig 2018

try:
    from ._ffi import ffi, lib  # noqa: F401
except ImportError:
    __wlroots_version__ = None
else:
    __wlroots_version__ = "{}.{}.{}".format(
        lib.WLR_VERSION_MAJOR, lib.WLR_VERSION_MICRO, lib.WLR_VERSION_MINOR,
    )

__version__ = "0.1.0"
