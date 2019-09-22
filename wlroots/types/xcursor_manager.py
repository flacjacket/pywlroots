# Copyright (c) Sean Vig 2019

from wlroots import ffi, lib


class XCursorManager:
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

    def __enter__(self):
        """Setup X cursor manager in a context manager"""

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Clean-up the X cursor manager on contex manager exit"""
        self.destroy()
