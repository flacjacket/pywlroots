# Copyright (c) Sean Vig 2019

from typing import Optional, Tuple

from pywayland.server import Signal

from wlroots import ffi, lib, Ptr
from .box import Box
from .output import Output


class OutputLayout(Ptr):
    def __init__(self) -> None:
        """Creates an output layout to work with a layout of screens

        Creates a output layout, which can be used to describing outputs in
        physical space relative to one another, and perform various useful
        operations on that state.
        """
        ptr = lib.wlr_output_layout_create()
        self._ptr = ffi.gc(ptr, lib.wlr_output_layout_destroy)

        self.add_event = Signal(ptr=ffi.addressof(ptr.events.add))
        self.change_event = Signal(ptr=ffi.addressof(ptr.events.change))
        self.destroy_event = Signal(ptr=ffi.addressof(ptr.events.destroy))

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

    def output_coords(self, output: Output) -> Tuple[float, float]:
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

    def output_at(self, x: float, y: float) -> Optional[Output]:
        """
        Get the output at the specified layout coordinates. Returns None if no output
        matches the coordinates.
        """
        output_ptr = lib.wlr_output_layout_output_at(self._ptr, x, y)
        if output_ptr == ffi.NULL:
            return None
        return Output(output_ptr)

    def add(self, output: Output, lx: int, ly: int) -> None:
        """
        Add the output to the layout at the specified coordinates. If the output is
        already part of the output layout, this moves the output.
        """
        lib.wlr_output_layout_add(self._ptr, output._ptr, lx, ly)

    def move(self, output: Output, lx: int, ly: int) -> None:
        """Move an output to specified coordinates."""
        lib.wlr_output_layout_move(self._ptr, output._ptr, lx, ly)

    def remove(self, output: Output) -> None:
        """Remove an output from the layout."""
        lib.wlr_output_layout_remove(self._ptr, output._ptr)

    def get_box(self, reference: Output) -> Box:
        """
        Get the box of the layout for the given reference output in layout
        coordinates. If `reference` is NULL, the box will be for the extents of the
        entire layout.
        """
        box_ptr = lib.wlr_output_layout_get_box(self._ptr, reference._ptr)
        return Box(ptr=box_ptr)

    def closest_point(
        self, lx: float, ly: float, reference: Optional[Output] = None
    ) -> Tuple[float, float]:
        """
        Get the closest point on this layout from the given point from the reference
        output. If reference is NULL, gets the closest point from the entire layout.
        """
        if reference:
            reference_ptr = reference._ptr
        else:
            reference_ptr = ffi.NULL

        dest_lx = ffi.new("double *")
        dest_ly = ffi.new("double *")
        lib.wlr_output_layout_closest_point(
            self._ptr, reference_ptr, lx, ly, dest_lx, dest_ly
        )
        return dest_lx[0], dest_ly[0]
