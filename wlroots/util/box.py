# Copyright Sean Vig (c) 2020
# Copyright Matt Colligan (c) 2021

from __future__ import annotations

from pywayland.protocol.wayland import WlOutput

from wlroots import ffi, lib


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
        x: int | None = None,
        y: int | None = None,
        width: int | None = None,
        height: int | None = None,
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

    def __repr__(self) -> str:
        return f"Box({self.x}, {self.y}, {self.width}, {self.height})"

    def copy(self) -> Box:
        return Box(self.x, self.y, self.width, self.height)

    def copy_from(self, other: Box) -> None:
        self.x = other.x
        self.y = other.y
        self.width = other.width
        self.height = other.height

    def closest_point(self, x: float, y: float) -> tuple[float, float]:
        xy_ptr = ffi.new("double[2]")
        lib.wlr_box_closest_point(self._ptr, x, y, xy_ptr, xy_ptr + 1)
        return xy_ptr[0], xy_ptr[1]

    def contains_point(self, x: float, y: float) -> bool:
        return lib.wlr_box_contains_point(self._ptr, x, y)

    def transform(self, box: Box, transform: WlOutput.transform, width: int, height: int):
        lib.wlr_box_transform(self._ptr, box._ptr, transform, width, height)

    def intersection(self, box_a: Box, box_b: Box) -> bool:
        return lib.wlr_box_intersection(self._ptr, box_a._ptr, box_b._ptr)
