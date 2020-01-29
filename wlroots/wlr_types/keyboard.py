# Copyright Sean Vig (c) 2020

from pywayland.server import Signal

from wlroots import ffi, lib


class Keyboard:
    def __init__(self, ptr):
        """The Keyboard wlroots object

        :param ptr:
            The wlr_keyboard cdata pointer for the given keyboard
        """
        self._ptr = ptr

        self.modifiers_event = Signal(ptr=ffi.addressof(self._ptr.events.modifiers))
        self.key_event = Signal(ptr=ffi.addressof(self._ptr.events.key))

    def set_keymap(self, keymap):
        """Set the keymap associated with the keyboard"""
        lib.wlr_keyboard_set_keymap(self._ptr, keymap._keymap)

    def set_repeat_info(self, rate, delay):
        """Sets the keyboard repeat info

        :param rate:
            The keyrepeats made per second
        :param delay:
            The delay in milliseconds before repeating
        """
        lib.wlr_keyboard_set_repeat_info(self._ptr, rate, delay)
