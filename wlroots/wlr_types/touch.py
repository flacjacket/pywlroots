# Copyright (c) Matt Colligan 2021
from __future__ import annotations

from weakref import WeakKeyDictionary

from wlroots import Ptr, PtrHasData, ffi, lib, str_or_none

from .input_device import InputDevice

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class Touch(PtrHasData):
    def __init__(self, ptr) -> None:
        self._ptr = ptr

    @staticmethod
    def from_input_device(input_device: InputDevice) -> Touch:
        return Touch(lib.wlr_touch_from_input_device(input_device._ptr))

    @property
    def base(self) -> InputDevice:
        device_ptr = ffi.addressof(self._ptr.base)
        _weakkeydict[device_ptr] = self._ptr
        return InputDevice(device_ptr)

    @property
    def output_name(self) -> str | None:
        """The name of any associated output"""
        return str_or_none(self._ptr.output_name)

    @property
    def width_mm(self) -> float:
        return self._ptr.width_mm

    @property
    def height_mm(self) -> float:
        return self._ptr.height_mm


class _TouchEvent(Ptr):
    @property
    def touch(self) -> Touch:
        """The touch device associated with the event"""
        return Touch(self._ptr.touch)

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec

    @property
    def touch_id(self) -> int:
        return self._ptr.touch_id


class TouchDownEvent(_TouchEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_touch_down_event *", ptr)

    @property
    def x(self) -> float:
        return self._ptr.x

    @property
    def y(self) -> float:
        return self._ptr.y


class TouchUpEvent(_TouchEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_touch_up_event *", ptr)


class TouchMotionEvent(_TouchEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_touch_motion_event *", ptr)

    @property
    def x(self) -> float:
        return self._ptr.x

    @property
    def y(self) -> float:
        return self._ptr.y


class TouchCancelEvent(_TouchEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_touch_cancel_event *", ptr)
