# Copyright (c) Sean Vig 2019

import enum

from wlroots import ffi, lib, Ptr
from .input_device import ButtonState, InputDevice


@enum.unique
class AxisSource(enum.IntEnum):
    WHEEL = lib.WLR_AXIS_SOURCE_WHEEL
    FINGER = lib.WLR_AXIS_SOURCE_FINGER
    CONTINUOUS = lib.WLR_AXIS_SOURCE_CONTINUOUS
    WHEEL_TILT = lib.WLR_AXIS_SOURCE_WHEEL_TILT


@enum.unique
class AxisOrientation(enum.IntEnum):
    VERTICAL = lib.WLR_AXIS_ORIENTATION_VERTICAL
    HORIZONTAL = lib.WLR_AXIS_ORIENTATION_HORIZONTAL


class PointerEventMotion(Ptr):
    def __init__(self, ptr) -> None:
        """A relative motion pointer event

        Emitted by the cursor motion event.
        """
        ptr = ffi.cast("struct wlr_event_pointer_motion *", ptr)
        self._ptr = ptr

    @property
    def device(self) -> InputDevice:
        """Input device associated with the event"""
        return InputDevice(self._ptr.device)

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec

    @property
    def delta_x(self) -> float:
        return self._ptr.delta_x

    @property
    def delta_y(self) -> float:
        return self._ptr.delta_y

    @property
    def unaccel_delta_x(self) -> float:
        return self._ptr.unaccel_dx

    @property
    def unaccel_delta_y(self) -> float:
        return self._ptr.unaccel_dy


class PointerEventMotionAbsolute(Ptr):
    def __init__(self, ptr) -> None:
        """A absolute motion pointer event

        Emitted by the cursor absolute motion event.
        """
        ptr = ffi.cast("struct wlr_event_pointer_motion_absolute *", ptr)
        self._ptr = ptr

    @property
    def device(self) -> InputDevice:
        """Input device associated with the event"""
        return InputDevice(self._ptr.device)

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec

    @property
    def x(self) -> float:
        """The x position of the motion"""
        return self._ptr.x

    @property
    def y(self) -> float:
        """The y position of the motion"""
        return self._ptr.y


class PointerEventButton(Ptr):
    def __init__(self, ptr) -> None:
        """A pointer button event

        Emitted by the cursor button event.
        """
        ptr = ffi.cast("struct wlr_event_pointer_button *", ptr)
        self._ptr = ptr

    @property
    def device(self) -> InputDevice:
        """Input device associated with the event"""
        return InputDevice(self._ptr.device)

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec

    @property
    def button(self) -> int:
        return self._ptr.button

    @property
    def button_state(self) -> ButtonState:
        return ButtonState(self._ptr.state)


class PointerEventAxis(Ptr):
    def __init__(self, ptr) -> None:
        """A pointer axis event

        Emitted by the cursor axis event.
        """
        ptr = ffi.cast("struct wlr_event_pointer_axis *", ptr)
        self._ptr = ptr

    @property
    def device(self) -> InputDevice:
        """Input device associated with the event"""
        return InputDevice(self._ptr.device)

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec

    @property
    def source(self) -> AxisSource:
        return AxisSource(self._ptr.source)

    @property
    def orientation(self) -> AxisOrientation:
        return AxisOrientation(self._ptr.orientation)

    @property
    def delta(self) -> float:
        return self._ptr.delta

    @property
    def delta_discrete(self) -> int:
        return self._ptr.delta_discrete


class PointerEventSwipeBegin(Ptr):
    def __init__(self, ptr) -> None:
        ptr = ffi.cast("struct wlr_event_pointer_swipe_begin *", ptr)
        self._ptr = ptr


class PointerEventSwipeUpdate(Ptr):
    def __init__(self, ptr) -> None:
        ptr = ffi.cast("struct wlr_event_pointer_swipe_update *", ptr)
        self._ptr = ptr


class PointerEventSwipeEnd(Ptr):
    def __init__(self, ptr) -> None:
        ptr = ffi.cast("struct wlr_event_pointer_swipe_end *", ptr)
        self._ptr = ptr


class PointerEventPinchBegin(Ptr):
    def __init__(self, ptr) -> None:
        ptr = ffi.cast("struct wlr_event_pointer_pinch_begin *", ptr)
        self._ptr = ptr


class PointerEventPinchUpdate(Ptr):
    def __init__(self, ptr) -> None:
        ptr = ffi.cast("struct wlr_event_pointer_pinch_update *", ptr)
        self._ptr = ptr


class PointerEventPinchEnd(Ptr):
    def __init__(self, ptr) -> None:
        ptr = ffi.cast("struct wlr_event_pointer_pinch_end *", ptr)
        self._ptr = ptr
