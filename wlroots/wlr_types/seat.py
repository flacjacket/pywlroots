# Copyright (c) 2019 Sean Vig

from typing import Optional, Tuple
from weakref import WeakKeyDictionary

from pywayland.server import Display, Signal
from pywayland.protocol.wayland import WlSeat

from wlroots import ffi, PtrHasData, lib, Ptr
from .input_device import ButtonState, InputDevice
from .keyboard import Keyboard, KeyboardModifiers, KeyboardKeyEvent
from .pointer import AxisSource, AxisOrientation
from .surface import Surface

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class KeyboardGrab(Ptr):
    def __init__(self, seat: "Seat") -> None:
        """Setup the keyboard grab"""
        self._ptr = ffi.new("struct wlr_seat_keyboard_grab *")
        self._seat = seat

    def __enter__(self) -> "KeyboardGrab":
        """State the keyboard grab"""
        lib.wlr_seat_keyboard_start_grab(self._seat._ptr, self._ptr)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """End the grab of the keyboard of this seat"""
        lib.wlr_seat_keyboard_end_grab(self._seat)


class Seat(PtrHasData):
    def __init__(self, display: Display, name: str) -> None:
        """Allocates a new seat and adds a seat global to the display

        :param display:
            The Wayland server display to attach the seat to
        :param name:
            The name of the seat to create
        """
        ptr = lib.wlr_seat_create(display._ptr, name.encode())
        self._ptr = ffi.gc(ptr, lib.wlr_seat_destroy)

        self.pointer_grab_begin_event = Signal(
            ptr=ffi.addressof(self._ptr.events.pointer_grab_begin)
        )
        self.pointer_grab_end_event = Signal(
            ptr=ffi.addressof(self._ptr.events.pointer_grab_end)
        )

        self.keyboard_grab_begin_event = Signal(
            ptr=ffi.addressof(self._ptr.events.keyboard_grab_begin)
        )
        self.keyboard_grab_end_event = Signal(
            ptr=ffi.addressof(self._ptr.events.keyboard_grab_end)
        )

        self.request_set_cursor_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_set_cursor),
            data_wrapper=PointerRequestSetCursorEvent,
        )

        # Called when an application _wants_ to set the selection
        self.request_set_selection_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_set_selection),
            data_wrapper=RequestSetSelectionEvent,
        )
        # Called after the data source is set for the selection
        self.set_selection_event = Signal(
            ptr=ffi.addressof(self._ptr.events.set_selection),
            data_wrapper=RequestSetPrimarySelectionEvent,
        )

        # Called when an application _wants_ to set the primary selection (user selects some data)
        self.request_set_primary_selection_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_set_primary_selection)
        )
        # Called after the primary selection source object is set
        self.set_primary_selection_event = Signal(
            ptr=ffi.addressof(self._ptr.events.set_primary_selection)
        )

        self.request_start_drag_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_start_drag),
            data_wrapper=RequestStartDragEvent,
        )
        self.start_drag_event = Signal(ptr=ffi.addressof(self._ptr.events.start_drag))

    @property
    def pointer_state(self) -> "SeatPointerState":
        """The pointer state associated with the seat"""
        pointer_state_ptr = ffi.addressof(self._ptr.pointer_state)
        _weakkeydict[pointer_state_ptr] = self._ptr
        return SeatPointerState(pointer_state_ptr)

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

    @property
    def destroyed(self) -> bool:
        """Whether this seat has been destroyed."""
        return self._ptr is None

    def set_capabilities(self, capabilities: WlSeat.capability) -> None:
        """Updates the capabilities available on this seat

        Will automatically send them to all clients.

        :param capabilities:
            The Wayland seat capabilities to set on the seat.
        """
        lib.wlr_seat_set_capabilities(self._ptr, capabilities)

    def set_name(self, name: str) -> None:
        """Updates the name of this seat

        Will automatically send it to all clients.
        """
        lib.wlr_seat_set_name(self._ptr, name.encode())

    def pointer_surface_has_focus(self, surface: Surface) -> bool:
        """Whether or not the surface has pointer focus"""
        return lib.wlr_seat_pointer_surface_has_focus(self._ptr, surface._ptr)

    def pointer_clear_focus(self) -> None:
        """Clear the focused surface for the pointer and leave all entered surfaces"""
        return lib.wlr_seat_pointer_clear_focus(self._ptr)

    def pointer_notify_enter(
        self, surface: Surface, surface_x: float, surface_y: float
    ) -> None:
        """Notify the seat of a pointer enter event to the given surface

        Notify the seat of a pointer enter event to the given surface and
        request it to be the focused surface for the pointer. Pass
        surface-local coordinates where the enter occurred.
        """
        lib.wlr_seat_pointer_notify_enter(self._ptr, surface._ptr, surface_x, surface_y)

    def pointer_notify_motion(
        self, time_msec: int, surface_x: float, surface_y: float
    ) -> None:
        """Notify the seat of motion over the given surface

        Pass surface-local coordinates where the pointer motion occurred.
        """
        lib.wlr_seat_pointer_notify_motion(self._ptr, time_msec, surface_x, surface_y)

    def pointer_notify_button(
        self, time_msec: int, button: int, button_state: ButtonState
    ) -> int:
        """Notify the seat that a button has been pressed

        Returns the serial of the button press or zero if no button press was
        sent.
        """
        return lib.wlr_seat_pointer_notify_button(
            self._ptr, time_msec, button, button_state.value
        )

    def pointer_notify_axis(
        self,
        time_msec: int,
        orientation: AxisOrientation,
        value: float,
        value_discrete: int,
        source: AxisSource,
    ) -> None:
        """Notify the seat of an axis event"""
        lib.wlr_seat_pointer_notify_axis(
            self._ptr, time_msec, orientation.value, value, value_discrete, source.value
        )

    def pointer_notify_frame(self) -> None:
        """Notify the seat of a frame event

        Frame events are sent to end a group of events that logically belong
        together. Motion, button and axis events should all be followed by a
        frame event.
        """
        lib.wlr_seat_pointer_notify_frame(self._ptr)

    def pointer_has_grab(self):
        """Whether or not the pointer has a grab other than the default grab"""
        lib.wlr_seat_pointer_has_grab(self._ptr)

    def set_keyboard(self, input_device: InputDevice) -> None:
        """Set this keyboard as the active keyboard for the seat

        :param input_device:
            The input device associated to the keyboard to set
        """
        lib.wlr_seat_set_keyboard(self._ptr, input_device._ptr)

    def grab(self) -> KeyboardGrab:
        """Start a grab of the keyboard of this seat"""
        return KeyboardGrab(self)

    @property
    def has_grab(self) -> bool:
        """Whether or not the keyboard has a grab other than the default grab"""
        return lib.wlr_seat_keyboard_has_grab(self._ptr)

    def keyboard_notify_key(self, key_event: KeyboardKeyEvent) -> None:
        """Notify the seat that a key has been pressed on the keyboard

        Defers to any keyboard grabs.
        """
        lib.wlr_seat_keyboard_notify_key(
            self._ptr, key_event.time_msec, key_event.keycode, key_event.state
        )

    def keyboard_notify_modifiers(self, modifiers: KeyboardModifiers) -> None:
        """Notify the seat that the modifiers for the keyboard have changed

        Defers to any keyboard grabs.
        """
        lib.wlr_seat_keyboard_notify_modifiers(self._ptr, modifiers._ptr)

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
            keyboard.modifiers._ptr,
        )

    def keyboard_clear_focus(self) -> None:
        """Clear the focused surface for the keyboard and leave all entered surfaces"""
        lib.wlr_seat_keyboard_clear_focus(self._ptr)

    def keyboard_has_grab(self) -> bool:
        """Whether or not the keyboard has a grab other than the default grab"""
        return lib.wlr_seat_keyboard_has_grab(self._ptr)

    def set_selection(self, source, serial: int) -> None:
        """Sets the current selection for the seat

        None can be provided to clear it.  This removes the previous one if
        there was any. In case the selection doesn't come from a client,
        Display.next_serial() can be used to generate a serial.
        """
        if source is None:
            lib.wlr_seat_set_selection(self._ptr, ffi.NULL, serial)
        else:
            # TODO: wrap source in a data source
            lib.wlr_seat_set_selection(self._ptr, source, serial)

    def __enter__(self) -> "Seat":
        """Context manager to clean up the seat"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Clean up the seat when exiting the context"""
        self.destroy()


class PointerRequestSetCursorEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_seat_pointer_request_set_cursor_event *", ptr)

    # TODO: seat client

    @property
    def surface(self) -> Surface:
        # TODO: setup weakref
        return Surface(self._ptr.surface)

    @property
    def serial(self) -> int:
        return self._ptr.serial

    @property
    def hotspot(self) -> Tuple[int, int]:
        return self._ptr.hotspot_x, self._ptr.hotspot_y


class RequestSetSelectionEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_seat_request_set_selection_event *", ptr)

    # TODO: source

    @property
    def serial(self) -> int:
        return self._ptr.serial


class RequestSetPrimarySelectionEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_seat_request_set_selection_event *", ptr)

    # TODO: source

    @property
    def serial(self) -> int:
        return self._ptr.serial


class RequestStartDragEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_seat_request_start_drag_event *", ptr)

    # TODO


class PointerFocusChangeEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_seat_pointer_focus_change_event *", ptr)

    # TODO


class KeyboardFocusChangeEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_seat_keyboard_focus_change_event *", ptr)

    # TODO


class SeatPointerState(Ptr):
    def __init__(self, ptr) -> None:
        """The current state of the pointer on the seat"""
        self._ptr = ptr

        self.focus_change_event = Signal(
            ptr=ffi.addressof(self._ptr.events.focus_change),
            data_wrapper=PointerFocusChangeEvent,
        )

    @property
    def focused_surface(self) -> Optional[Surface]:
        """The surface that currently has keyboard focus"""
        focused_surface = self._ptr.focused_surface
        if focused_surface == ffi.NULL:
            return None
        return Surface(focused_surface)


class SeatKeyboardState(Ptr):
    def __init__(self, ptr) -> None:
        """The current state of the keyboard on the seat"""
        self._ptr = ptr

        self.focus_change_event = Signal(
            ptr=ffi.addressof(self._ptr.events.focus_change),
            data_wrapper=KeyboardFocusChangeEvent,
        )

    @property
    def focused_surface(self) -> Optional[Surface]:
        """The surface that is currently focused"""
        focused_surface = self._ptr.focused_surface
        if focused_surface == ffi.NULL:
            return None
        return Surface(focused_surface)
