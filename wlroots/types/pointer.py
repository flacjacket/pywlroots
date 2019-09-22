# Copyright (c) Sean Vig 2019

from wlroots import ffi
from .input_device import InputDevice


class PointerEventAxis:
    def __init__(self, ptr):
        """A pointer axis event

        Emitted by the cursor axis event.
        """
        ptr = ffi.cast("struct wlr_event_pointer_axis *", ptr)
        self._ptr = ptr

    @property
    def device(self):
        """Input device associated with the event"""
        return InputDevice(self._ptr.device)


class PointerEventButton:
    def __init__(self, ptr):
        """A pointer button event

        Emitted by the cursor button event.
        """
        ptr = ffi.cast("struct wlr_event_pointer_button *", ptr)
        self._ptr = ptr

    @property
    def device(self):
        """Input device associated with the event"""
        return InputDevice(self._ptr.device)


class PointerEventMotion:
    def __init__(self, ptr):
        """A relative motion pointer event

        Emitted by the cursor motion event.
        """
        ptr = ffi.cast("struct wlr_event_pointer_motion *", ptr)
        self._ptr = ptr

    @property
    def device(self):
        """Input device associated with the event"""
        return InputDevice(self._ptr.device)


class PointerEventMotionAbsolute:
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
    def x(self) -> float:
        """The x position of the motion"""
        return self._ptr.x

    @property
    def y(self) -> float:
        """The y position of the motion"""
        return self._ptr.y
