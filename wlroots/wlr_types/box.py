# Copyright Sean Vig (c) 2020
# Copyright Matt Colligan (c) 2021

from typing import Optional

from wlroots import ffi


def _int_getter(attr):
    def getter(self):
        return getattr(self._ptr, attr)

    return getter


def _int_setter(attr):
    def setter(self, value):
        setattr(self._ptr, attr, value)

    return setter


class Box:
    def __init__(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        ptr=None,
    ) -> None:
        """A simple box structure, represented by a coordinate and dimensions"""
        if ptr is None:
            self._ptr = ffi.new("struct wlr_box *")
        else:
            self._ptr = ptr

        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height

    x = property(_int_getter("x"), _int_setter("x"))
    y = property(_int_getter("y"), _int_setter("y"))
    width = property(_int_getter("width"), _int_setter("width"))
    height = property(_int_getter("height"), _int_setter("height"))
