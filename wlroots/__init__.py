# Copyright (c) Sean Vig 2018

from __future__ import annotations

from typing import Any

from ._ffi import ffi, lib  # noqa: F401
from .version import version as _version

__wlroots_version__ = "{}.{}.{}".format(
    lib.WLR_VERSION_MAJOR,
    lib.WLR_VERSION_MINOR,
    lib.WLR_VERSION_MICRO,
)

__version__ = _version


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


class PtrHasData(Ptr):
    """
    Add methods to get and set the void *data member on the wrapped struct. The value
    stored can be of any Python type.
    """

    @property
    def data(self) -> Any | None:
        """Return any data that has been stored on the object"""
        if self._ptr.data == ffi.NULL:
            return None
        return ffi.from_handle(self._ptr.data)

    @data.setter
    def data(self, data: Any) -> None:
        """Store the given data on the current object"""
        self._data_handle = ffi.new_handle(data)
        self._ptr.data = self._data_handle


def str_or_none(member: ffi.CData) -> str | None:
    """
    Helper function to check struct members for ffi.NULL, returning None, or a char
    array, returning a string.
    """
    if member:
        return ffi.string(member).decode(errors="backslashreplace")
    return None
