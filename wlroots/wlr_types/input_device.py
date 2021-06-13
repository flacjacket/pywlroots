# Copyright (c) Sean Vig 2019

import enum
import weakref
from typing import Optional

from .keyboard import Keyboard
from wlroots import ffi, PtrHasData, lib

_weakkeydict: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()


@enum.unique
class ButtonState(enum.IntEnum):
    RELEASED = lib.WLR_BUTTON_RELEASED
    PRESSED = lib.WLR_BUTTON_PRESSED


@enum.unique
class InputDeviceType(enum.IntEnum):
    KEYBOARD = lib.WLR_INPUT_DEVICE_KEYBOARD
    POINTER = lib.WLR_INPUT_DEVICE_POINTER
    TOUCH = lib.WLR_INPUT_DEVICE_TOUCH
    TABLET_TOOL = lib.WLR_INPUT_DEVICE_TABLET_TOOL
    TABLET_PAD = lib.WLR_INPUT_DEVICE_TABLET_PAD
    SWITCH = lib.WLR_INPUT_DEVICE_SWITCH


class InputDevice(PtrHasData):
    def __init__(self, ptr) -> None:
        """Create the input device from the given cdata

        :param ptr:
            The wlr_input_device for the given input device
        """
        self._ptr = ffi.cast("struct wlr_input_device *", ptr)

    @property
    def device_type(self) -> InputDeviceType:
        """The device type associated with the current device"""
        return InputDeviceType(self._ptr.type)

    @property
    def vendor(self) -> int:
        return self._ptr.vendor

    @property
    def product(self) -> int:
        return self._ptr.product

    @property
    def name(self) -> str:
        return ffi.string(self._ptr.name).decode()

    @property
    def keyboard(self) -> Keyboard:
        """Return the keyboard type associated with the input device

        The device must be a keyboard, otherwise this throws a ValueError.
        """
        if self.device_type != InputDeviceType.KEYBOARD:
            raise ValueError(
                f"Expected keyborad input device type, got: {self.device_type}"
            )

        keyboard = Keyboard(self._ptr.keyboard)

        _weakkeydict[keyboard] = self._ptr

        return keyboard

    def libinput_get_device_handle(self) -> Optional[ffi.CData]:
        """
        Returns the underlying libinput device if there is one.

        Returns a pointer to a `struct libinput_device` for use by libinput-interfacing
        code.
        """
        if lib.wlr_input_device_is_libinput(self._ptr):
            return lib.wlr_libinput_get_device_handle(self._ptr)
        return None
