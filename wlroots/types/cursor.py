# Copyright (c) Sean Vig 2019

from wlroots import ffi, lib
from .output_layout import OutputLayout


class Cursor:
    def __init__(self, output_layout: OutputLayout) -> None:
        """Manage a cursor attached to the given output layout

        Uses the given layout to establish the boundaries and movement
        semantics of this cursor. Cursors without an output layout allow
        infinite movement in any direction and do not support absolute input
        events.

        :param output_layout:
            The output layout to attach the cursor to and bound the cursor by.
        """
        ptr = lib.wlr_cursor_create()
        self._ptr = ffi.gc(ptr, lib.wlr_cursor_destroy)
        lib.wlr_cursor_attach_output_layout(self._ptr, output_layout._ptr)

    def destroy(self) -> None:
        """Clean up the cursor"""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    def __enter__(self) -> "Cursor":
        """Context manager to clean up the cursor"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Clean up the cursor when exiting the context"""
        self.destroy()
