# Copyright Sean Vig (c) 2020

import enum

from pywayland.server import Signal

from wlroots import ffi, lib


@enum.unique
class KeyState(enum.IntEnum):
    KEY_RELEASED = lib.WLR_KEY_RELEASED
    KEY_PRESSED = lib.WLR_KEY_PRESSED


class KeyboardKeyEvent:
    def __init__(self, ptr) -> None:
        """Event that a key has been pressed or release

        This event is emitted before the xkb state of the keyboard has been
        updated (including modifiers).
        """
        self._ptr = ffi.cast("struct wlr_event_keyboard_key *", ptr)

    @property
    def time_msec(self) -> int:
        """Time of the key event"""
        return self._ptr.time_msec

    @property
    def keycode(self) -> int:
        """Keycode triggering the event"""
        return self._ptr.keycode

    @property
    def update_state(self) -> bool:
        """If backend doesn't update modifiers on its own"""
        return self._ptr.update_state

    @property
    def state(self) -> KeyState:
        """The state of the keycode triggering the event"""
        return KeyState(self._ptr.state)


class Keyboard:
    def __init__(self, ptr):
        """The Keyboard wlroots object

        :param ptr:
            The wlr_keyboard cdata pointer for the given keyboard
        """
        self._ptr = ptr

        self.modifiers_event = Signal(ptr=ffi.addressof(self._ptr.events.modifiers))
        self.key_event = Signal(
            ptr=ffi.addressof(self._ptr.events.key), data_wrapper=KeyboardKeyEvent
        )

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

    @property
    def keycodes(self):
        """Keycodes associated with the keyboard"""
        return self._ptr.keycodes

    @property
    def num_keycodes(self) -> int:
        """The number of keycodes"""
        return self._ptr.num_keycodes

    @property
    def modifiers(self):
        """The modifiers associated with the keyboard"""
        return self._ptr.modifiers
