# Copyright (c) Sean Vig 2019

import enum

from wlroots import ffi, lib


@enum.unique
class InputDeviceType(enum.IntEnum):
    KEYBOARD = lib.WLR_INPUT_DEVICE_KEYBOARD
    POINTER = lib.WLR_INPUT_DEVICE_POINTER
    TOUCH = lib.WLR_INPUT_DEVICE_TOUCH
    TABLET_TOOL = lib.WLR_INPUT_DEVICE_TABLET_TOOL
    TABLET_PAD = lib.WLR_INPUT_DEVICE_TABLET_PAD
    SWITCH = lib.WLR_INPUT_DEVICE_SWITCH


class InputDevice:
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
