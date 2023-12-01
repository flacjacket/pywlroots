# Copyright (c) Sean Vig 2019
from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from pywayland.server import Signal

from wlroots import PtrHasData, ffi, lib

from .compositor import Surface
from .input_device import InputDevice, InputDeviceType
from .output import Output
from .output_layout import OutputLayout
from .pointer import (
    PointerAxisEvent,
    PointerButtonEvent,
    PointerHoldBeginEvent,
    PointerHoldEndEvent,
    PointerMotionAbsoluteEvent,
    PointerMotionEvent,
    PointerPinchBeginEvent,
    PointerPinchEndEvent,
    PointerPinchUpdateEvent,
    PointerSwipeBeginEvent,
    PointerSwipeEndEvent,
    PointerSwipeUpdateEvent,
)
from .touch import (
    TouchEventCancel,
    TouchEventDown,
    TouchEventMotion,
    TouchEventUp,
)

if TYPE_CHECKING:
    from .xcursor_manager import XCursorManager


class WarpMode(enum.Enum):
    Layout = enum.auto()
    LayoutClosest = enum.auto()
    AbsoluteClosest = enum.auto()


class Cursor(PtrHasData):
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

        self.motion_event = Signal(
            ptr=ffi.addressof(self._ptr.events.motion), data_wrapper=PointerMotionEvent
        )
        self.motion_absolute_event = Signal(
            ptr=ffi.addressof(self._ptr.events.motion_absolute),
            data_wrapper=PointerMotionAbsoluteEvent,
        )
        self.button_event = Signal(
            ptr=ffi.addressof(self._ptr.events.button), data_wrapper=PointerButtonEvent
        )
        self.axis_event = Signal(
            ptr=ffi.addressof(self._ptr.events.axis), data_wrapper=PointerAxisEvent
        )
        self.frame_event = Signal(ptr=ffi.addressof(self._ptr.events.frame))
        self.swipe_begin = Signal(
            ptr=ffi.addressof(self._ptr.events.swipe_begin),
            data_wrapper=PointerSwipeBeginEvent,
        )
        self.swipe_update = Signal(
            ptr=ffi.addressof(self._ptr.events.swipe_update),
            data_wrapper=PointerSwipeUpdateEvent,
        )
        self.swipe_end = Signal(
            ptr=ffi.addressof(self._ptr.events.swipe_end),
            data_wrapper=PointerSwipeEndEvent,
        )
        self.pinch_begin = Signal(
            ptr=ffi.addressof(self._ptr.events.pinch_begin),
            data_wrapper=PointerPinchBeginEvent,
        )
        self.pinch_update = Signal(
            ptr=ffi.addressof(self._ptr.events.pinch_update),
            data_wrapper=PointerPinchUpdateEvent,
        )
        self.pinch_end = Signal(
            ptr=ffi.addressof(self._ptr.events.pinch_end),
            data_wrapper=PointerPinchEndEvent,
        )
        self.hold_begin = Signal(
            ptr=ffi.addressof(self._ptr.events.hold_begin),
            data_wrapper=PointerHoldBeginEvent,
        )
        self.hold_end = Signal(
            ptr=ffi.addressof(self._ptr.events.hold_end),
            data_wrapper=PointerHoldEndEvent,
        )
        self.touch_up_event = Signal(
            ptr=ffi.addressof(self._ptr.events.touch_up),
            data_wrapper=TouchEventUp,
        )
        self.touch_down_event = Signal(
            ptr=ffi.addressof(self._ptr.events.touch_down),
            data_wrapper=TouchEventDown,
        )
        self.touch_motion_event = Signal(
            ptr=ffi.addressof(self._ptr.events.touch_motion),
            data_wrapper=TouchEventMotion,
        )
        self.touch_cancel_event = Signal(
            ptr=ffi.addressof(self._ptr.events.touch_cancel),
            data_wrapper=TouchEventCancel,
        )

    @property
    def x(self) -> float:
        """The x position of the cursor"""
        return self._ptr.x

    @property
    def y(self) -> float:
        """The y position of the cursor"""
        return self._ptr.y

    def destroy(self) -> None:
        """Clean up the cursor"""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    def attach_input_device(self, input_device: InputDevice) -> None:
        """Attaches this input device to this cursor

        The input device type must be one of:
            - InputDeviceType.POINTER
            - InputDeviceType.TOUCH
            - InputDeviceType.TABLET_TOOL

        :param input_device:
            The input device to attach to the cursor
        """
        allowed_device_types = (
            InputDeviceType.POINTER,
            InputDeviceType.TOUCH,
            InputDeviceType.TABLET_TOOL,
        )
        if input_device.type not in allowed_device_types:
            raise ValueError(
                f"Input device must be one of pointer, touch, or tablet tool, got: {input_device.type}"
            )

        lib.wlr_cursor_attach_input_device(self._ptr, input_device._ptr)

    def move(
        self,
        delta_x: float,
        delta_y: float,
        *,
        input_device: InputDevice | None = None,
    ) -> None:
        """Move the cursor in the direction of the given x and y layout coordinates

        If one coordinate is NAN, it will be ignored.

        The `input_device` may be passed to respect device mapping constraints.
        If `input_device` is None, device mapping constraints will be ignored.
        """
        if input_device is None:
            input_device_ptr = ffi.NULL
        else:
            input_device_ptr = input_device._ptr

        lib.wlr_cursor_move(self._ptr, input_device_ptr, delta_x, delta_y)

    def warp(
        self,
        warp_mode: WarpMode,
        x: float | None,
        y: float | None,
        *,
        input_device: InputDevice | None = None,
    ) -> bool:
        """Warp the cursor to the given x and y in location

        In Layout and LayoutClosest modes, warp the cursor to the given x and y
        in layout coordinates.  In AbsoluteClosest mode, warp the cursor to the
        given x and y in absolute 0..1 coordinates.

        For Layout mode, if x and y are out of the layout boundaries or
        constraints, no warp will happen.  For LayoutClosest and
        AbsoluteClosest modes, if the given point is out of the layout
        boundaries or constraints, the closest point will be used.

        If one coordinate is None, it will be ignored.

        The `input_device` may be passed to respect device mapping constraints.
        If `input_device` is None, device mapping constraints will be ignored.
        """
        if x is None:
            x = float("NaN")
        if y is None:
            y = float("NaN")

        if input_device is None:
            input_device_ptr = ffi.NULL
        else:
            input_device_ptr = input_device._ptr

        if warp_mode == WarpMode.Layout:
            return lib.wlr_cursor_warp(self._ptr, input_device_ptr, x, y)
        elif warp_mode == WarpMode.LayoutClosest:
            lib.wlr_cursor_warp_closest(self._ptr, input_device_ptr, x, y)
            return True
        elif warp_mode == WarpMode.AbsoluteClosest:
            lib.wlr_cursor_warp_absolute(self._ptr, input_device_ptr, x, y)
            return True
        else:
            raise ValueError("Invalid warp mode")

    def absolute_to_layout_coords(
        self, input_device: InputDevice | None, x: float, y: float
    ) -> tuple[float, float]:
        """Convert absolute 0..1 coordinates to layout coordinates

        The `input_device` may be passed to respect device mapping constraints.
        If `input_device` is `None`, device mapping constraints will be
        ignored.
        """
        if input_device is None:
            input_device_ptr = ffi.NULL
        else:
            input_device_ptr = input_device._ptr

        xy_ptr = ffi.new("double[2]")
        lib.wlr_cursor_absolute_to_layout_coords(
            self._ptr, input_device_ptr, x, y, xy_ptr, xy_ptr + 1
        )

        return xy_ptr[0], xy_ptr[1]

    def set_surface(self, surface: Surface | None, hotspot: tuple[int, int]) -> None:
        """Set the cursor surface

        The surface can be committed to update the cursor image. The surface
        position is subtracted from the hotspot. A None surface commit hides
        the cursor.
        """
        if surface is None:
            surface_ptr = ffi.NULL
        else:
            surface_ptr = surface._ptr

        lib.wlr_cursor_set_surface(self._ptr, surface_ptr, hotspot[0], hotspot[1])

    def __enter__(self) -> Cursor:
        """Context manager to clean up the cursor"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Clean up the cursor when exiting the context"""
        self.destroy()

    def map_to_output(self, output: Output | None) -> None:
        """
        Attaches this cursor to the given output, which must be among the outputs in the
        current output_layout for this cursor. This call is invalid for a cursor without
        an associated output layout.
        """
        if output is None:
            output_ptr = ffi.NULL
        else:
            output_ptr = output._ptr

        lib.wlr_cursor_map_to_output(self._ptr, output_ptr)

    def map_input_to_output(
        self, input_device: InputDevice, output: Output | None
    ) -> None:
        """
        Maps all input from a specific input device to a given output. The input device
        must be attached to this cursor and the output must be among the outputs in the
        attached output layout.
        """
        if output is None:
            output_ptr = ffi.NULL
        else:
            output_ptr = output._ptr

        lib.wlr_cursor_map_input_to_output(self._ptr, input_device._ptr, output_ptr)

    def set_xcursor(self, manager: XCursorManager, name: str) -> None:
        """
        Set the cursor image from an XCursor theme.

        The image will be loaded from the struct wlr_xcursor_manager.
        """
        lib.wlr_cursor_set_xcursor(self._ptr, manager._ptr, name.encode())
