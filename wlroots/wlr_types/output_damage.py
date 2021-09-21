# Copyright (c) Matt Colligan 2021

from pywayland.server import Signal

from wlroots import ffi, lib, Ptr
from wlroots.util.box import Box
from wlroots.util.region import PixmanRegion32
from .output import Output


class OutputDamage(Ptr):
    def __init__(self, output: Output) -> None:
        """
        Tracks damage for an output.

        The `frame` event will be emitted when it is a good time for the compositor
        to submit a new frame.

        To render a new frame, compositors should call
        `wlr_output_damage_attach_render`, render and call `wlr_output_commit`. No
        rendering should happen outside a `frame` event handler or before
        `wlr_output_damage_attach_render`.
        """
        self._ptr = lib.wlr_output_damage_create(output._ptr)

        self.frame_event = Signal(ptr=ffi.addressof(self._ptr.events.frame))
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    @property
    def output(self) -> Output:
        """The name of the output"""
        return Output(self._ptr.output)

    @property
    def current(self) -> PixmanRegion32:
        return PixmanRegion32(ffi.addressof(self._ptr.current))

    def destroy(self) -> None:
        """The name of the output"""
        lib.wlr_output_damage_destroy(self._ptr)
        self._ptr = None

    def attach_render(self, damage: PixmanRegion32) -> bool:
        """
        Attach the renderer's buffer to the output. Compositors must call this
        function before rendering. After they are done rendering, they should call
        `wlr_output_set_damage` and `wlr_output_commit` to submit the new frame.

        `needs_frame` will be set to true if a frame should be submitted. `damage`
        will be set to the region of the output that needs to be repainted, in
        output-buffer-local coordinates.

        The buffer damage region accumulates all damage since the buffer has last
        been swapped. This is not to be confused with the output surface damage,
        which only contains the changes between two frames.

        Returns a bool specifying whether the output needs a new frame rendered.
        """
        needs_frame_ptr = ffi.new("bool *")
        if not lib.wlr_output_damage_attach_render(
            self._ptr, needs_frame_ptr, damage._ptr
        ):
            raise RuntimeError("Rendering on output failed")

        return needs_frame_ptr[0]

    def add(self, damage: PixmanRegion32) -> None:
        """Accumulates damage and schedules a `frame` event."""
        lib.wlr_output_damage_add(self._ptr, damage._ptr)

    def add_whole(self) -> None:
        """Damages the whole output and schedules a `frame` event."""
        lib.wlr_output_damage_add_whole(self._ptr)

    def add_box(self, box: Box) -> None:
        """Accumulates damage from a box and schedules a `frame` event."""
        lib.wlr_output_damage_add_box(self._ptr, box._ptr)
