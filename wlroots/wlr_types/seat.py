# Copyright (c) 2019 Sean Vig

from typing import Optional
from weakref import WeakKeyDictionary

from pywayland.server import Display, Signal
from pywayland.protocol.wayland import WlSeat

from wlroots import ffi, lib
from .input_device import InputDevice
from .keyboard import Keyboard, KeyboardKeyEvent
from .surface import Surface

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class Seat:
    def __init__(self, display: Display, name: str) -> None:
        """Allocates a new seat and adds a seat global to the display

        :param display:
            The Wayland server display to attach the seat to
        :param name:
            The name of the seat to create
        """
        ptr = lib.wlr_seat_create(display._ptr, name.encode())
        self._ptr = ffi.gc(ptr, lib.wlr_seat_destroy)

        self.request_set_cursor_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_set_cursor)
        )

    @property
    def keyboard_state(self) -> "SeatKeyboardState":
        """The keyboard state associated with the seat"""
        keyboard_state_ptr = ffi.addressof(self._ptr.keyboard_state)
        _weakkeydict[keyboard_state_ptr] = self._ptr
        return SeatKeyboardState(keyboard_state_ptr)

    @property
    def keyboard(self) -> Keyboard:
        """Get the keyboard associated with this seat"""
        keyboard_ptr = lib.wlr_seat_get_keyboard(self._ptr)
        return Keyboard(keyboard_ptr)

    def destroy(self) -> None:
        """Clean up the seat"""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    def set_capabilities(self, capabilities: WlSeat.capability) -> None:
        """Updates the capabilities available on this seat

        Will automatically send them to all clients.

        :param capabilities:
            The Wayland seat capabilities to set on the seat.
        """
        lib.wlr_seat_set_capabilities(self._ptr, capabilities)

    def set_keyboard(self, input_device: InputDevice) -> None:
        """Set this keyboard as the active keyboard for the seat

        :param input_device:
            The input device associated to the keyboard to set
        """
        lib.wlr_seat_set_keyboard(self._ptr, input_device._ptr)

    def pointer_notify_frame(self) -> None:
        """Notify the seat of a frame event

        Frame events are sent to end a group of events that logically belong
        together. Motion, button and axis events should all be followed by a
        frame event.
        """
        lib.wlr_seat_pointer_notify_frame(self._ptr)

    def keyboard_notify_key(self, key_event: KeyboardKeyEvent) -> None:
        """Notify the seat that a key has been pressed on the keyboard

        Defers to any keyboard grabs.
        """
        lib.wlr_seat_keyboard_notify_key(
            self._ptr, key_event.time_msec, key_event.keycode, key_event.state
        )

    def keyboard_notify_enter(self, surface: Surface, keyboard: Keyboard) -> None:
        """Notify the seat that the keyboard focus has changed

        Notify the seat that the keyboard focus has changed and request it to
        be the focused surface for this keyboard. Defers to any current grab of
        the seat's keyboard.
        """
        lib.wlr_seat_keyboard_notify_enter(
            self._ptr,
            surface._ptr,
            keyboard.keycodes,
            keyboard.num_keycodes,
            ffi.addressof(keyboard.modifiers),
        )

    def __enter__(self) -> "Seat":
        """Context manager to clean up the seat"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Clean up the seat when exiting the context"""
        self.destroy()


class SeatKeyboardState:
    def __init__(self, ptr) -> None:
        """The current state of the keyboard on the seat"""
        self._ptr = ptr

    @property
    def focused_surface(self) -> Optional[Surface]:
        """The surface that is currently focused"""
        focused_surface = self._ptr.focused_surface
        if focused_surface == ffi.NULL:
            return None
        return Surface(focused_surface)
