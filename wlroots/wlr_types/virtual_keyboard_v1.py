# Copyright (c) 2021 Matt Colligan

from weakref import WeakKeyDictionary

from pywayland.server import Display, Signal

from wlroots import ffi, lib, Ptr
from wlroots.wlr_types.keyboard import Keyboard

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class VirtualKeyboardManagerV1(Ptr):
    def __init__(self, display: Display) -> None:
        """A wlr_virtual_keyboard_manager_v1 instance."""
        self._ptr = lib.wlr_virtual_keyboard_manager_v1_create(display._ptr)

        self.new_virtual_keyboard_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_virtual_keyboard),
            data_wrapper=VirtualKeyboardV1,
        )
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))


class VirtualKeyboardV1(Ptr):
    def __init__(self, ptr) -> None:
        """A wlr_virtual_keyboard_v1 instance."""
        self._ptr = ffi.cast("struct wlr_virtual_keyboard_v1 *", ptr)

    @property
    def keyboard(self) -> Keyboard:
        keyboard_ptr = ffi.addressof(self._ptr.keyboard)
        _weakkeydict[keyboard_ptr] = self._ptr
        return Keyboard(keyboard_ptr)

    @property
    def has_keymap(self) -> bool:
        return self._ptr.has_keymap
