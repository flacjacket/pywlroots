# Copyright (c) Sean Vig 2019
# Copyright (c) Matt Colligan 2022

from __future__ import annotations

import enum
from weakref import WeakKeyDictionary

from wlroots import Ptr, ffi, lib, str_or_none

from .input_device import ButtonState, InputDevice

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


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


class Pointer(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ptr

    @classmethod
    def from_input_device(cls, input_device: InputDevice) -> Pointer:
        return Pointer(lib.wlr_pointer_from_input_device(input_device._ptr))

    @property
    def base(self) -> InputDevice:
        device_ptr = ffi.addressof(self._ptr.base)
        _weakkeydict[device_ptr] = self._ptr
        return InputDevice(device_ptr)

    @property
    def output_name(self) -> str | None:
        """The name of any associated output"""
        return str_or_none(self._ptr.output_name)


class _PointerEvent(Ptr):
    @property
    def pointer(self) -> Pointer:
        """The pointer associated with the event"""
        return Pointer(self._ptr.pointer)

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec


class PointerMotionEvent(_PointerEvent):
    def __init__(self, ptr) -> None:
        """A relative motion pointer event"""
        self._ptr = ffi.cast("struct wlr_pointer_motion_event *", ptr)

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


class PointerMotionAbsoluteEvent(_PointerEvent):
    def __init__(self, ptr) -> None:
        """A absolute motion pointer event"""
        self._ptr = ffi.cast("struct wlr_pointer_motion_absolute_event *", ptr)

    @property
    def x(self) -> float:
        return self._ptr.x

    @property
    def y(self) -> float:
        return self._ptr.y


class PointerButtonEvent(_PointerEvent):
    def __init__(self, ptr) -> None:
        """A pointer button event"""
        self._ptr = ffi.cast("struct wlr_pointer_button_event *", ptr)

    @property
    def button(self) -> int:
        return self._ptr.button

    @property
    def button_state(self) -> ButtonState:
        return ButtonState(self._ptr.state)


class PointerAxisEvent(_PointerEvent):
    def __init__(self, ptr) -> None:
        """A pointer axis event"""
        self._ptr = ffi.cast("struct wlr_pointer_axis_event *", ptr)

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


class PointerSwipeBeginEvent(_PointerEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_pointer_swipe_begin_event *", ptr)

    @property
    def fingers(self) -> int:
        return self._ptr.fingers


class PointerSwipeUpdateEvent(_PointerEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_pointer_swipe_update_event *", ptr)

    @property
    def fingers(self) -> int:
        return self._ptr.fingers

    @property
    def dx(self) -> float:
        return self._ptr.dx

    @property
    def dy(self) -> float:
        return self._ptr.dy


class PointerSwipeEndEvent(_PointerEvent):
    def __init__(self, ptr) -> None:
        ptr = ffi.cast("struct wlr_pointer_swipe_end_event *", ptr)
        self._ptr = ptr

    @property
    def cancelled(self) -> bool:
        return self._ptr.cancelled


class PointerPinchBeginEvent(_PointerEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_pointer_pinch_begin_event *", ptr)

    @property
    def fingers(self) -> int:
        return self._ptr.fingers

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec

    @property
    def dx(self) -> float:
        return self._ptr.dx

    @property
    def dy(self) -> float:
        return self._ptr.dy


class PointerPinchUpdateEvent(_PointerEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_pointer_pinch_update_event *", ptr)

    @property
    def fingers(self) -> int:
        return self._ptr.fingers

    @property
    def dx(self) -> float:
        return self._ptr.dx

    @property
    def dy(self) -> float:
        return self._ptr.dy

    @property
    def scale(self) -> float:
        return self._ptr.scale

    @property
    def rotation(self) -> float:
        return self._ptr.rotation

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec

    @property
    def cancelled(self) -> bool:
        return self._ptr.cancelled


class PointerPinchEndEvent(_PointerEvent):
    def __init__(self, ptr) -> None:
        ptr = ffi.cast("struct wlr_pointer_pinch_end_event *", ptr)
        self._ptr = ptr

    @property
    def cancelled(self) -> bool:
        return self._ptr.cancelled


class PointerHoldBeginEvent(_PointerEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_pointer_hold_begin_event *", ptr)

    @property
    def fingers(self) -> int:
        return self._ptr.fingers


class PointerHoldEndEvent(_PointerEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_pointer_hold_end_event *", ptr)

    @property
    def cancelled(self) -> bool:
        return self._ptr.cancelled
