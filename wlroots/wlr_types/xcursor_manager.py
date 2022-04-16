# Copyright (c) Sean Vig 2019

from __future__ import annotations

from typing import TYPE_CHECKING

from wlroots import ffi, lib, Ptr

from .cursor import Cursor

if TYPE_CHECKING:
    from typing import Iterator


class XCursorManager(Ptr):
    def __init__(self, size, scale=1):
        """Creates a new XCursor manager

        Create cursor with base size and scale.
        """
        ptr = lib.wlr_xcursor_manager_create(ffi.NULL, size)
        self._ptr = ffi.gc(ptr, lib.wlr_xcursor_manager_destroy)

        lib.wlr_xcursor_manager_load(self._ptr, scale)

    def destroy(self):
        """Destroy the x cursor manager"""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    def set_cursor_image(self, name: str, cursor: Cursor):
        """Set the cursor image

        Set a Cursor image to the specified cursor name for all scale factors.
        The wlroots cursor will take over from this point and ensure the
        correct cursor is used on each output, assuming an output layout is
        attached to it.
        """
        name_cdata = ffi.new("char []", name.encode())
        lib.wlr_xcursor_manager_set_cursor_image(self._ptr, name_cdata, cursor._ptr)

    def get_xcursor(self, name: str, scale: float = 1) -> XCursor | None:
        """
        Retrieves a wlr_xcursor reference for the given cursor name at the given scale
        factor, or NULL if this wlr_xcursor_manager has not loaded a cursor theme at the
        requested scale.
        """
        ptr = lib.wlr_xcursor_manager_get_xcursor(self._ptr, name.encode(), scale)
        if ptr == ffi.NULL:
            return None
        return XCursor(ptr)

    def __enter__(self):
        """Setup X cursor manager in a context manager"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Clean-up the X cursor manager on contex manager exit"""
        self.destroy()


class XCursor(Ptr):
    """struct wlr_xcursor"""

    def __init__(self, ptr):
        self._ptr = ptr

    @property
    def images(self) -> Iterator[XCursorImage]:
        for i in range(self._ptr.image_count):
            yield XCursorImage(self._ptr.images[0][i])


class XCursorImage(Ptr):
    """struct wlr_xcursor_image"""

    def __init__(self, ptr):
        self._ptr = ptr
