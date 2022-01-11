# Copyright (c) Sean Vig 2019
# Copyright (c) Matt Colligan 2021

from __future__ import annotations

from typing import TYPE_CHECKING

from pywayland.server import Signal
from pywayland.protocol.wayland import WlOutput

from wlroots import ffi, PtrHasData, lib, Ptr, str_or_none
from wlroots.util.region import PixmanRegion32
from .matrix import Matrix

if TYPE_CHECKING:
    from wlroots.allocator import Allocator
    from wlroots.renderer import Renderer


class Output(PtrHasData):
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
        self.damage_event = Signal(ptr=ffi.addressof(self._ptr.events.damage))
        self.needs_frame_event = Signal(ptr=ffi.addressof(self._ptr.events.needs_frame))
        self.precommit_event = Signal(ptr=ffi.addressof(self._ptr.events.precommit))
        self.commit_event = Signal(ptr=ffi.addressof(self._ptr.events.commit))
        self.present_event = Signal(ptr=ffi.addressof(self._ptr.events.present))
        self.bind_event = Signal(ptr=ffi.addressof(self._ptr.events.bind))
        self.enable_event = Signal(ptr=ffi.addressof(self._ptr.events.enable))
        self.mode_event = Signal(ptr=ffi.addressof(self._ptr.events.mode))
        self.description_event = Signal(ptr=ffi.addressof(self._ptr.events.description))
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    @property
    def name(self) -> str | None:
        """The name of the output"""
        return str_or_none(self._ptr.name)

    @property
    def description(self) -> str | None:
        """The description of the output"""
        return str_or_none(self._ptr.description)

    @property
    def make(self) -> str | None:
        return str_or_none(self._ptr.make)

    @property
    def model(self) -> str | None:
        return str_or_none(self._ptr.model)

    @property
    def serial(self) -> str | None:
        return str_or_none(self._ptr.serial)

    @property
    def physical_size_mm(self) -> tuple[int, int]:
        """Returns the width and height of the output, in millimeters"""
        return self._ptr.phys_width, self._ptr.phys_height

    @property
    def modes(self):
        if lib.wl_list_empty(ffi.addressof(self._ptr.modes)) == 1:
            return []

    @property
    def enabled(self) -> bool:
        return self._ptr.enabled

    @property
    def current_mode(self) -> OutputMode:
        return OutputMode(self._ptr.current_mode)

    @property
    def scale(self) -> float:
        return self._ptr.scale

    @property
    def transform(self) -> WlOutput.transform:
        return WlOutput.transform(self._ptr.transform)

    @property
    def transform_matrix(self) -> Matrix:
        """The transform matrix giving the projection of the output"""
        return Matrix(self._ptr.transform_matrix)

    def enable(self, *, enable: bool = True) -> None:
        """Enables or disables the output

        A disabled output is turned off and doesn't emit `frame` events.
        """
        lib.wlr_output_enable(self._ptr, enable)

    def preferred_mode(self) -> OutputMode | None:
        """Returns the preferred mode for this output

        If the output doesn't support modes, returns None.
        """
        output_mode_ptr = lib.wlr_output_preferred_mode(self._ptr)
        if output_mode_ptr == ffi.NULL:
            return None

        return OutputMode(output_mode_ptr)

    def set_mode(self, mode: OutputMode) -> None:
        """Sets the output mode

        The output needs to be enabled.
        """
        lib.wlr_output_set_mode(self._ptr, mode._ptr)

    def set_custom_mode(self, width: int, height: int, refresh: int) -> None:
        """
        Sets a custom mode on the output. If modes are available, they are preferred.
        Setting `refresh` to zero lets the backend pick a preferred value. The
        output needs to be enabled.
        """
        lib.wlr_output_set_custom_mode(self._ptr, width, height, refresh)

    def create_global(self) -> None:
        """Create the global corresponding to the output"""
        lib.wlr_output_create_global(self._ptr)

    def __enter__(self) -> Output:
        """Start rendering frame"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Stop rendering frame, commit when exiting normally, otherwise rollback"""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def init_render(self, allocator: Allocator, renderer: Renderer) -> None:
        """Initialize the output's rendering subsystem with the provided allocator and renderer.

        Can only be called once.

        Call this function prior to any call to `attach_render`, `commit`, or
        `cursor_create`. The buffer capabilities of the provided must match the
        capabilities of the output's backend.  Raises error otherwise.
        """
        if not lib.wlr_output_init_render(self._ptr, allocator._ptr, renderer._ptr):
            raise RuntimeError(
                "Output capabilities must match the capabilities of the output's backend."
            )

    def attach_render(self) -> None:
        """Attach the renderer's buffer to the output

        Compositors must call this function before rendering. After they are
        done rendering, they should call `.commit()` to submit the new frame.
        """
        if not lib.wlr_output_attach_render(self._ptr, ffi.NULL):
            raise RuntimeError("Unable to attach render")

    def commit(self) -> None:
        """Commit the pending output state

        If `.attach_render` has been called, the pending frame will be
        submitted for display.
        """
        if not lib.wlr_output_test(self._ptr):
            self.rollback()
            raise RuntimeError("Rendering on output failed")
        if not lib.wlr_output_commit(self._ptr):
            raise RuntimeError("Unable to commit output")

    def rollback(self) -> None:
        """Discard the pending output state"""
        lib.wlr_output_rollback(self._ptr)

    def effective_resolution(self) -> tuple[int, int]:
        """Computes the transformed and scaled output resolution"""
        width_ptr = ffi.new("int *")
        height_ptr = ffi.new("int *")
        lib.wlr_output_effective_resolution(self._ptr, width_ptr, height_ptr)
        width = width_ptr[0]
        height = height_ptr[0]
        return width, height

    def transformed_resolution(self) -> tuple[int, int]:
        """Computes the transformed output resolution"""
        width_ptr = ffi.new("int *")
        height_ptr = ffi.new("int *")
        lib.wlr_output_transformed_resolution(self._ptr, width_ptr, height_ptr)
        width = width_ptr[0]
        height = height_ptr[0]
        return width, height

    def render_software_cursors(self, damage: PixmanRegion32 | None = None) -> None:
        """Renders software cursors

        This is a utility function that can be called when compositors render.
        """
        if damage is None:
            lib.wlr_output_render_software_cursors(self._ptr, ffi.NULL)
        else:
            lib.wlr_output_render_software_cursors(self._ptr, damage._ptr)

    @staticmethod
    def transform_invert(transform: WlOutput.transform) -> WlOutput.transform:
        """Returns the transform that, when composed with transform gives transform.normal"""
        return WlOutput.transform(lib.wlr_output_transform_invert(transform))

    def set_damage(self, damage: PixmanRegion32) -> None:
        """
        Set the damage region for the frame to be submitted. This is the region of
        the screen that has changed since the last frame.

        Compositors implementing damage tracking should call this function with the
        damaged region in output-buffer-local coordinates.

        This region is not to be confused with the renderer's buffer damage, ie. the
        region compositors need to repaint. Compositors usually need to repaint more
        than what changed since last frame since multiple render buffers are used.
        """
        lib.wlr_output_set_damage(self._ptr, damage._ptr)

    def set_transform(self, transform: WlOutput.transform) -> None:
        """
        Sets a transform for the output.

        Transform is double-buffered state, see `wlr_output_commit`.
        """
        lib.wlr_output_set_transform(self._ptr, transform)

    def set_scale(self, scale: float) -> None:
        """
        Sets a scale for the output.

        Scale is double-buffered state, see `wlr_output_commit`.
        """
        lib.wlr_output_set_scale(self._ptr, scale)

    def test(self) -> bool:
        """
        Test whether the pending output state would be accepted by the backend. If
        this function returns true, `wlr_output_commit` can only fail due to a
        runtime error.

        This function doesn't mutate the pending state.
        """
        return lib.wlr_output_test(self._ptr)

    @property
    def is_headless(self) -> bool:
        return lib.wlr_output_is_headless(self._ptr)


class OutputMode(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ptr

    @property
    def width(self) -> int:
        return self._ptr.width

    @property
    def height(self) -> int:
        return self._ptr.height

    @property
    def refresh_mhz(self) -> int:
        return self._ptr.refresh

    @property
    def preferred(self) -> int:
        return self._ptr.preferred
