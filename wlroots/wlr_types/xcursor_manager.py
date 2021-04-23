# Copyright (c) Sean Vig 2019

from wlroots import ffi, lib, Ptr

from .cursor import Cursor


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

    def __enter__(self):
        """Setup X cursor manager in a context manager"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Clean-up the X cursor manager on contex manager exit"""
        self.destroy()
