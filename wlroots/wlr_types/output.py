# Copyright (c) Sean Vig 2019

from typing import Tuple

from pywayland.server import Signal
from pywayland.protocol.wayland import WlOutput

from wlroots import ffi, lib
from .matrix import Matrix


class Output:
    def __init__(self, ptr) -> None:
        """A compositor output region

        This typically corresponds to a monitor that displays part of the
        compositor space.

        The `frame` event will be emitted when it is a good time for the
        compositor to submit a new frame.

        To render a new frame, compositors should call
        `wlr_output_attach_render`, render and call `wlr_output_commit`. No
        rendering should happen outside a `frame` event handler or before
        `wlr_output_attach_render`.

        :param ptr:
            The wlr_output cdata pointer
        """
        self._ptr = ffi.cast("struct wlr_output *", ptr)

        self.frame_event = Signal(ptr=ffi.addressof(self._ptr.events.frame))
        self.needs_frame_event = Signal(ptr=ffi.addressof(self._ptr.events.needs_frame))
        self.precommit_event = Signal(ptr=ffi.addressof(self._ptr.events.precommit))
        self.commit_event = Signal(ptr=ffi.addressof(self._ptr.events.commit))
        self.present_event = Signal(ptr=ffi.addressof(self._ptr.events.present))
        self.enable_event = Signal(ptr=ffi.addressof(self._ptr.events.enable))
        self.mode_event = Signal(ptr=ffi.addressof(self._ptr.events.mode))
        self.scale_event = Signal(ptr=ffi.addressof(self._ptr.events.scale))
        self.transform_event = Signal(ptr=ffi.addressof(self._ptr.events.transform))
        self.description_event = Signal(ptr=ffi.addressof(self._ptr.events.description))
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    @property
    def name(self) -> str:
        """The name of the output"""
        return ffi.string(self._ptr.name).decode()

    @property
    def transform_matrix(self) -> Matrix:
        """The transform matrix giving the projection of the output"""
        return Matrix(self._ptr.transform_matrix)

    def create_global(self) -> None:
        """Create the global corresponding to the output"""
        lib.wlr_output_create_global(self._ptr)

    def attach_render(self) -> bool:
        """Attach the renderer's buffer to the output

        Compositors must call this function before rendering. After they are
        done rendering, they should call `.commit()` to submit the new frame.
        """
        return lib.wlr_output_attach_render(self._ptr, ffi.NULL)

    def commit(self) -> bool:
        """Commit the pending output state

        If `.attach_render` has been called, the pending frame will be
        submitted for display.
        """
        return lib.wlr_output_commit(self._ptr)

    def effective_resolution(self) -> Tuple[int, int]:
        """Computes the transformed and scaled output resolution"""
        width_ptr = ffi.new("int *")
        height_ptr = ffi.new("int *")
        lib.wlr_output_effective_resolution(self._ptr, width_ptr, height_ptr)
        width = width_ptr[0]
        height = height_ptr[0]
        return width, height

    def render_software_cursors(self) -> None:
        """Renders software cursors

        This is a utility function that can be called when compositors render.
        """
        lib.wlr_output_render_software_cursors(self._ptr, ffi.NULL)

    @property
    def modes(self):
        if lib.wl_list_empty(ffi.addressof(self._ptr.modes)) == 1:
            return []

    @staticmethod
    def transform_invert(transform: WlOutput.transform) -> WlOutput.transform:
        """Returns the transform that, when composed with transform gives transform.normal"""
        return WlOutput.transform(lib.wlr_output_transform_invert(transform))
