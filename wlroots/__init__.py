# Copyright (c) Sean Vig 2018

from ._ffi import ffi, lib  # noqa: F401

__wlroots_version__ = "{}.{}.{}".format(
    lib.WLR_VERSION_MAJOR,
    lib.WLR_VERSION_MICRO,
    lib.WLR_VERSION_MINOR,
)

__version__ = "0.2.4"


class Ptr:
    """Add equality checks for objects holding the same cdata

    Objects that reference the same cdata objects will be treated as equal.
    Note that these objects will still have a different hash such that they
    should not collide in a set or dictionary.
    """

    _ptr: ffi.CData

    def __eq__(self, other) -> bool:
        """Return true if the other object holds the same cdata"""
        return hasattr(other, "_ptr") and self._ptr == other._ptr

    def __hash__(self) -> int:
        """Use the hash from `object`, which is unique per object"""
        return super().__hash__()
