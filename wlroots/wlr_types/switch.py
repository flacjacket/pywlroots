from __future__ import annotations

import enum
from weakref import WeakKeyDictionary

from pywayland.server import Signal

from wlroots import Ptr, PtrHasData, ffi, lib

from .input_device import InputDevice

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


@enum.unique
class SwitchType(enum.IntEnum):
    LID = lib.WLR_SWITCH_TYPE_LID
    TABLET_MODE = lib.WLR_SWITCH_TYPE_TABLET_MODE


@enum.unique
class SwitchState(enum.IntEnum):
    STATE_OFF = lib.WLR_SWITCH_STATE_OFF
    STATE_ON = lib.WLR_SWITCH_STATE_ON


class Switch(PtrHasData):
    """
    A switch input device.

    Typically a switch input device can indicate whether a laptop lid is opened
    or closed, or whether tablet mode is enabled.

    See https://wayland.freedesktop.org/libinput/doc/latest/switches.html
    """

    def __init__(self, ptr) -> None:
        self._ptr = ptr
        self.toggle_event = Signal(
            ptr=ffi.addressof(self._ptr.events.toggle), data_wrapper=SwitchToggleEvent
        )

    @staticmethod
    def from_input_device(input_device: InputDevice) -> Switch:
        """
        Get a Switch from an InputDevice.

        Asserts that the input device is a switch.
        """
        return Switch(lib.wlr_switch_from_input_device(input_device._ptr))

    @property
    def base(self) -> InputDevice:
        device_ptr = ffi.addressof(self._ptr.base)
        _weakkeydict[device_ptr] = self._ptr
        return InputDevice(device_ptr)


class SwitchToggleEvent(Ptr):

    def __init__(self, ptr):
        self._ptr = ptr

    @property
    def time_msec(self) -> int:
        return self._ptr.time_msec

    @property
    def switch_type(self) -> SwitchType:
        return SwitchType(self._ptr.switch_type)

    @property
    def switch_state(self) -> SwitchState:
        return SwitchState(self._ptr.switch_state)
