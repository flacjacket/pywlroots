from __future__ import annotations

from typing import TYPE_CHECKING

from pywayland.server import Listener

if TYPE_CHECKING:
    from wlroots.wlr_types import InputDevice, Keyboard
    from wlroots.wlr_types.keyboard import KeyboardKeyEvent
    from .server import TinywlServer


class KeyboardHandler:
    def __init__(
        self,
        keyboard: Keyboard,
        input_device: InputDevice,
        tinywl_server: TinywlServer,
    ) -> None:
        self.keyboard = keyboard
        self.input_device = input_device
        self.tinywl_server = tinywl_server

        keyboard.modifiers_event.add(Listener(self.keyboard_handle_modifiers))
        keyboard.key_event.add(Listener(self.keyboard_handle_key))

    def keyboard_handle_modifiers(self, listener: Listener, data) -> None:
        """Activates the keyboard and sends the modifiers event to the active surface"""
        self.tinywl_server.send_modifiers(self.keyboard.modifiers, self.input_device)

    def keyboard_handle_key(
        self, listener: Listener, key_event: KeyboardKeyEvent
    ) -> None:
        """Activates the keyboard and sends the key event to the active surface

        Gives the display manager the first right of refusal
        """
        self.tinywl_server.send_key(key_event, self.input_device)
