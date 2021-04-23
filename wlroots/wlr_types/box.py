# Copyright Sean Vig (c) 2020

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
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """A simple box structure, represented by a coordinate and dimensions"""
        self._ptr = ffi.new("struct wlr_box *")
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    x = property(_int_getter("x"), _int_setter("x"))
    y = property(_int_getter("y"), _int_setter("y"))
    width = property(_int_getter("width"), _int_setter("width"))
    height = property(_int_getter("height"), _int_setter("height"))
