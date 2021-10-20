# Copyright (c) Matt Colligan 2021

from wlroots import ffi, Ptr
from .input_device import InputDevice


class TouchEventUp(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_event_touch_up *", ptr)

    @property
    def device(self) -> InputDevice:
        return InputDevice(self._ptr.device)

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec

    @property
    def touch_id(self) -> int:
        return self._ptr.touch_id


class TouchEventDown(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_event_touch_down *", ptr)

    @property
    def device(self) -> InputDevice:
        return InputDevice(self._ptr.device)

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec

    @property
    def touch_id(self) -> int:
        return self._ptr.touch_id

    @property
    def x(self) -> float:
        return self._ptr.x

    @property
    def y(self) -> float:
        return self._ptr.y


class TouchEventMotion(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_event_touch_motion *", ptr)

    @property
    def device(self) -> InputDevice:
        return InputDevice(self._ptr.device)

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec

    @property
    def touch_id(self) -> int:
        return self._ptr.touch_id

    @property
    def x(self) -> float:
        return self._ptr.x

    @property
    def y(self) -> float:
        return self._ptr.y


class TouchEventCancel(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_event_touch_cancel *", ptr)

    @property
    def device(self) -> InputDevice:
        return InputDevice(self._ptr.device)

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec

    @property
    def touch_id(self) -> int:
        return self._ptr.touch_id
