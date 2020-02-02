# Copyright Sean Vig (c) 2020

from wlroots import ffi


class Box:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """A simple box structure, represented by a coordinate and dimensions"""
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._ptr = ffi.new("struct wlr_box *")
        self._ptr.x = x
        self._ptr.y = y
        self._ptr.width = width
        self._ptr.height = height

    @property
    def x(self) -> int:
        """x position of the box"""
        return self._x

    @property
    def y(self) -> int:
        """y position of the box"""
        return self._y

    @property
    def width(self) -> int:
        """width of the box"""
        return self._width

    @property
    def height(self) -> int:
        """height of the box"""
        return self._height
