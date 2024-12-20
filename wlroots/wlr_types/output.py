# Copyright (c) Sean Vig 2019
# Copyright (c) Matt Colligan 2021

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, NamedTuple

from pywayland.protocol.wayland import WlOutput
from pywayland.server import Signal
from pywayland.utils import wl_list_for_each

from wlroots import (
    Ptr,
    PtrHasData,
    ffi,
    instance_or_none,
    lib,
    ptr_or_null,
    str_or_none,
)
from wlroots.wlr_types.buffer import Buffer
from wlroots.util.clock import Timespec
from wlroots.util.region import PixmanRegion32

from .matrix import Matrix

if TYPE_CHECKING:
    from typing import Iterator

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
        self.precommit_event = Signal(
            ptr=ffi.addressof(self._ptr.events.precommit),
            data_wrapper=OutputPrecommitEvent,
        )
        self.commit_event = Signal(
            ptr=ffi.addressof(self._ptr.events.commit), data_wrapper=OutputCommitEvent
        )
        self.present_event = Signal(ptr=ffi.addressof(self._ptr.events.present))
        self.bind_event = Signal(
            ptr=ffi.addressof(self._ptr.events.bind), data_wrapper=OutputBindEvent
        )
        self.description_event = Signal(ptr=ffi.addressof(self._ptr.events.description))
        self.request_state_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_state),
            data_wrapper=OutputRequestStateEvent,
        )
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
    def modes(self) -> Iterator[OutputMode]:
        for ptr in wl_list_for_each(
            "struct wlr_output_mode *",
            self._ptr.modes,
            "link",
            ffi=ffi,
        ):
            yield OutputMode(ptr)

    @property
    def enabled(self) -> bool:
        return self._ptr.enabled

    @property
    def current_mode(self) -> OutputMode | None:
        if self._ptr.current_mode == ffi.NULL:
            return None
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

    @property
    def commit_seq(self) -> int:
        """
        Commit sequence number. Incremented on each commit, may overflow.
        """
        return self._ptr.commit_seq

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

    def set_mode(self, mode: OutputMode | None) -> None:
        """Sets the output mode

        The output needs to be enabled.
        """
        lib.wlr_output_set_mode(self._ptr, ptr_or_null(mode))

    def set_custom_mode(self, custom_mode: CustomMode) -> None:
        """
        Sets a custom mode on the output. If modes are available, they are preferred.
        Setting `refresh` to zero lets the backend pick a preferred value. The
        output needs to be enabled.
        """
        lib.wlr_output_set_custom_mode(
            self._ptr, custom_mode.width, custom_mode.height, custom_mode.refresh
        )

    def create_global(self) -> None:
        """Create the global corresponding to the output"""
        lib.wlr_output_create_global(self._ptr)

    def __enter__(self) -> Output:
        """Start rendering frame"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Stop rendering frame, commit when exiting normally, otherwise rollback"""
        if exc_type is None:
            if not self.commit():
                raise RuntimeError("Unable to commit output")
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

    def commit(self, output_state: OutputState | None = None) -> bool:
        """Commit the pending output state

        If `.attach_render` has been called, the pending frame will be
        submitted for display.
        """
        if output_state is None:
            return lib.wlr_output_commit(self._ptr)
        else:
            return lib.wlr_output_commit_state(self._ptr, output_state._ptr)

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
        lib.wlr_output_render_software_cursors(self._ptr, ptr_or_null(damage))

    @staticmethod
    def transform_invert(transform: WlOutput.transform) -> WlOutput.transform:
        """Returns the transform that, when composed with transform gives transform.normal"""
        return WlOutput.transform(lib.wlr_output_transform_invert(transform))

    @staticmethod
    def transform_compose(
        tr_a: WlOutput.transform, tr_b: WlOutput.transform
    ) -> WlOutput.transform:
        """
        Returns a transform that, when applied, has the same effect as applying
        sequentially `tr_a` and `tr_b`.
        """
        return WlOutput.transform(lib.wlr_output_transform_compose(tr_a, tr_b))

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

    def test(self, output_state: OutputState | None = None) -> bool:
        """
        Test whether the pending output state would be accepted by the backend. If
        this function returns true, `wlr_output_commit` can only fail due to a
        runtime error.

        This function doesn't mutate the pending state.
        """
        if output_state is None:
            return lib.wlr_output_test(self._ptr)
        else:
            return lib.wlr_output_test_state(self._ptr, output_state._ptr)

    def enable_adaptive_sync(self, *, enable: bool = True) -> None:
        """
        Enables or disables adaptive sync (ie. variable refresh rate) on this
        output. On some backends, this is just a hint and may be ignored.
        Compositors can inspect `wlr_output.adaptive_sync_status` to query the
        effective status. Backends that don't support adaptive sync will reject
        the output commit.

        When enabled, compositors can submit frames a little bit later than the
        deadline without dropping a frame.

        Adaptive sync is double-buffered state, see commit().
        """
        lib.wlr_output_enable_adaptive_sync(self._ptr, enable)

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


class CustomMode(NamedTuple):
    """
    Custom mode which specifies the width and height, and the refresh rate
    of an Output.

    If refresh is zero (default), the backend uses a reasonable default value.
    """

    width: int
    height: int
    refresh: int = 0


class OutputState(Ptr):
    """
    Holds the double-buffered output state.
    """

    def __init__(self, ptr: ffi.CData | None = None) -> None:
        if ptr is None:
            ptr = ffi.new("struct wlr_output_state *")
            lib.wlr_output_state_init(ptr)
        self._ptr = ptr

    @property
    def enabled(self) -> bool:
        return self._ptr.enabled

    def set_enabled(self, enabled: bool) -> None:
        lib.wlr_output_state_set_enabled(self._ptr, enabled)

    @property
    def damage(self) -> PixmanRegion32 | None:
        return instance_or_none(PixmanRegion32, self._ptr.damage)

    def set_damage(self, damage: PixmanRegion32) -> None:
        """
        Sets the damage region for an output.

        This is used as a hint to the backend and can be used to reduce power consumption or increase performance on some devices.

        This should be called in along with ``OutputState.set_buffer()``.
        This state will be applied once ``Output.commit(output_state)`` is called.
        """
        lib.wlr_output_state_set_damage(self._ptr, damage._ptr)

    @property
    def buffer(self) -> Buffer | None:
        return instance_or_none(Buffer, self._ptr.buffer)

    def set_buffer(self, buffer: Buffer) -> None:
        """
        Sets the buffer for an output.

        The buffer contains the contents of the screen.

        If the compositor wishes to present a new frame, they must commit with a buffer.
        This state will be applied once ``Output.commit(output_state)`` is called.
        """
        lib.wlr_output_state_set_buffer(self._ptr, buffer._ptr)

    @property
    def scale(self) -> float:
        return self._ptr.scale

    def set_scale(self, scale: float) -> None:
        lib.wlr_output_state_set_scale(self._ptr, scale)

    @property
    def transform(self) -> WlOutput.transform:
        return WlOutput.transform(self._ptr.transform)

    def set_transform(self, transform: WlOutput.transform) -> None:
        lib.wlr_output_state_set_transform(self._ptr, transform)

    @property
    def adaptive_sync_enabled(self) -> bool:
        return self._ptr.adaptive_sync_enabled

    def set_adaptive_sync_enabled(self, enabled: bool) -> None:
        lib.wlr_output_state_set_adaptive_sync_enabled(self._ptr, enabled)

    @property
    def render_format(self) -> int:
        return self._ptr.render_format

    def set_render_format(self, format: int) -> None:
        lib.wlr_output_state_set_render_format(self._ptr, format)

    @property
    def subpixel(self) -> WlOutput.subpixel:
        return WlOutput.subpixel(self._ptr.subpixel)

    def set_subpixel(self, subpixel: WlOutput.subpixel) -> None:
        lib.wlr_output_state_set_subpixel(self._ptr, subpixel)

    @property
    def mode(self) -> OutputMode | None:
        mode_ptr = self._ptr.mode
        return OutputMode(mode_ptr) if mode_ptr != ffi.NULL else None

    def set_mode(self, mode: OutputMode | None) -> None:
        lib.wlr_output_state_set_mode(self._ptr, ptr_or_null(mode))

    @property
    def custom_mode(self) -> CustomMode:
        mode = self._ptr.custom_mode
        return CustomMode(width=mode.width, height=mode.height, refresh=mode.refresh)

    def set_custom_mode(self, mode: CustomMode) -> None:
        lib.wlr_output_state_set_custom_mode(
            self._ptr, mode.width, mode.height, mode.refresh
        )

    def finish(self) -> None:
        lib.wlr_output_state_finish(self._ptr)


class OutputPresentFlag(enum.IntFlag):
    WLR_OUTPUT_PRESENT_VSYNC = lib.WLR_OUTPUT_PRESENT_VSYNC
    """
    The presentation was synchronized to the "vertical retrace" by the
    display hardware such that tearing does not happen.
    """

    WLR_OUTPUT_PRESENT_HW_CLOCK = lib.WLR_OUTPUT_PRESENT_HW_CLOCK
    """
    The display hardware provided measurements that the hardware driver
    converted into a presentation timestamp.
    """

    WLR_OUTPUT_PRESENT_HW_COMPLETION = lib.WLR_OUTPUT_PRESENT_HW_COMPLETION
    """
    The display hardware signalled that it started using the new image
    content.
    """

    WLR_OUTPUT_PRESENT_ZERO_COPY = lib.WLR_OUTPUT_PRESENT_ZERO_COPY
    """
    The presentation of this update was done zero-copy.
    """


class _OutputStateAwareEvent(Ptr):
    """\
    Common event superclass which provides access to the output and output state.
    """

    @property
    def output(self) -> Output:
        return Output(self._ptr.output)

    @property
    def state(self) -> OutputState:
        return OutputState(self._ptr.state)


class OutputRequestStateEvent(_OutputStateAwareEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_output_event_request_state *", ptr)


OutputEventRequestState = OutputRequestStateEvent


class OutputPrecommitEvent(_OutputStateAwareEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_output_event_precommit *", ptr)


class OutputCommitEvent(_OutputStateAwareEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_output_event_commit *", ptr)

    @property
    def when(self) -> Timespec:
        return Timespec(self._ptr.when)


class OutputDamageEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_output_event_damage *", ptr)

    @property
    def output(self) -> Output:
        return Output(self._ptr.output)

    @property
    def damage(self) -> PixmanRegion32:
        """
        Output-buffer-local coordinates.
        """
        return PixmanRegion32(self._ptr.damage)


class OutputBindEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_output_event_bind *", ptr)

    @property
    def output(self) -> Output:
        return Output(self._ptr.output)

    @property
    def resource(self) -> ffi.CData:  # This should be WlResource
        return self._ptr.resource


class OutputPresentEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_output_event_present *", ptr)

    @property
    def output(self) -> Output:
        return Output(self._ptr.output)

    @property
    def commit_seq(self) -> int:
        """
        Frame submission for which this presentation event is for
        (see Output.commit_seq).
        """
        return self._ptr.commit_seq

    @property
    def presented(self) -> bool:
        """
        Whether the frame was presented at all.
        """
        return self._ptr.presented

    @property
    def when(self) -> Timespec:
        """
        Time when the content update turned into light the first time.
        """
        return Timespec(self._ptr.when)

    @property
    def seq(self) -> int:
        """
        Vertical retrace counter. Zero if unavailable.
        """
        return self._ptr.seq

    @property
    def refresh_nsec(self) -> int:
        """
        Prediction of how many nanoseconds after `when` the very next output
        refresh may occur. Zero if unknown.
        """
        return self._ptr.refresh

    @property
    def flags(self) -> OutputPresentFlag:
        return OutputPresentFlag(self._ptr.flags)
