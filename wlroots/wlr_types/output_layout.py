# Copyright (c) Sean Vig 2019

from typing import Tuple

from wlroots import ffi, lib
from .output import Output


class OutputLayout:
    def __init__(self) -> None:
        """Creates an output layout to work with a layout of screens

        Creates a output layout, which can be used to describing outputs in
        physical space relative to one another, and perform various useful
        operations on that state.
        """
        ptr = lib.wlr_output_layout_create()
        self._ptr = ffi.gc(ptr, lib.wlr_output_layout_destroy)

    def destroy(self) -> None:
        """Destroy the current output layout"""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    def add_auto(self, output: Output) -> None:
        """Add an auto configured output to the layout

        This will place the output in a sensible location in the layout. The
        coordinates of the output in the layout may adjust dynamically when the
        layout changes. If the output is already in the layout, it will become
        auto configured. If the position of the output is set such as with
        `wlr_output_layout_move()`, the output will become manually configured.

        :param output:
            The output to configure the layout against.
        """
        lib.wlr_output_layout_add_auto(self._ptr, output._ptr)

    def output_coords(self, output) -> Tuple[float, float]:
        """Determine coordinates of the output in the layout

        Given x and y in layout coordinates, adjusts them to local output
        coordinates relative to the given reference output.
        """
        ox = ffi.new("double *")
        oy = ffi.new("double *")
        lib.wlr_output_layout_output_coords(self._ptr, output._ptr, ox, oy)

        return ox[0], oy[0]

    def __enter__(self) -> "OutputLayout":
        """Use the output layout in a context manager"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Clean up the output layout when exiting the context"""
        self.destroy()
