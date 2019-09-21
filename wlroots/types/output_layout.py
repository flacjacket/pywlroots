# Copyright (c) Sean Vig 2019

from wlroots import ffi, lib


class OutputLayout:
    def __init__(self) -> None:
        """Creates an output layout to work with a layout of screens

        Creates a output layout, which can be used to describing outputs in
        physical space relative to one another, and perform various useful
        operations on that state.
        """
        ptr = lib.wlr_output_layout_create()
        self._ptr = ffi.gc(ptr, lib.wlr_output_layout_destroy)

    def destroy(self):
        """Destroy the current output layout"""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    def __enter__(self) -> "OutputLayout":
        """Use the output layout in a context manager"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Clean up the output layout when exiting the context"""
        self.destroy()
