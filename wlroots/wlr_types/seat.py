# Copyright (c) 2019 Sean Vig

from __future__ import annotations

from typing import Iterator
from weakref import WeakKeyDictionary

from pywayland.protocol.wayland import WlSeat
from pywayland.server import Display, Signal
from pywayland.utils import wl_list_for_each

from wlroots import Ptr, PtrHasData, ffi, instance_or_none, lib, ptr_or_null

from .compositor import Surface
from .data_device_manager import Drag
from .input_device import ButtonState
from .keyboard import Keyboard, KeyboardKeyEvent, KeyboardModifiers
from .pointer import AxisOrientation, AxisSource

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class KeyboardGrab(Ptr):
    def __init__(self, seat: Seat) -> None:
        """Setup the keyboard grab"""
        self._ptr = ffi.new("struct wlr_seat_keyboard_grab *")
        self._seat = seat

    def __enter__(self) -> KeyboardGrab:
        """State the keyboard grab"""
        lib.wlr_seat_keyboard_start_grab(self._seat._ptr, self._ptr)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """End the grab of the keyboard of this seat"""
        lib.wlr_seat_keyboard_end_grab(self._seat._ptr)


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

        self.touch_grab_begin_event = Signal(
            ptr=ffi.addressof(self._ptr.events.touch_grab_begin)
        )
        self.touch_grab_end_event = Signal(
            ptr=ffi.addressof(self._ptr.events.touch_grab_end)
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
            ptr=ffi.addressof(self._ptr.events.set_selection)
        )

        # Called when an application _wants_ to set the primary selection (user selects some data)
        self.request_set_primary_selection_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_set_primary_selection),
            data_wrapper=RequestSetPrimarySelectionEvent,
        )
        # Called after the primary selection source object is set
        self.set_primary_selection_event = Signal(
            ptr=ffi.addressof(self._ptr.events.set_primary_selection)
        )

        self.request_start_drag_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_start_drag),
            data_wrapper=RequestStartDragEvent,
        )
        self.start_drag_event = Signal(
            ptr=ffi.addressof(self._ptr.events.start_drag),
            data_wrapper=Drag,
        )

    @property
    def pointer_state(self) -> SeatPointerState:
        """The pointer state associated with the seat"""
        pointer_state_ptr = ffi.addressof(self._ptr.pointer_state)
        _weakkeydict[pointer_state_ptr] = self._ptr
        return SeatPointerState(pointer_state_ptr)

    @property
    def keyboard_state(self) -> SeatKeyboardState:
        """The keyboard state associated with the seat"""
        keyboard_state_ptr = ffi.addressof(self._ptr.keyboard_state)
        _weakkeydict[keyboard_state_ptr] = self._ptr
        return SeatKeyboardState(keyboard_state_ptr)

    def get_keyboard(self) -> Keyboard | None:
        """Get the active keyboard for the seat."""
        return instance_or_none(Keyboard, lib.wlr_seat_get_keyboard(self._ptr))

    def set_keyboard(self, keyboard: Keyboard | None) -> None:
        """Set this keyboard as the active keyboard for the seat"""
        lib.wlr_seat_set_keyboard(self._ptr, ptr_or_null(keyboard))

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
        """Clear the focused surface for the pointer and leave all entered surfaces.

        This function does not respect pointer grabs: you probably want
        `pointer_notify_clear_focus()` instead.
        """
        return lib.wlr_seat_pointer_clear_focus(self._ptr)

    def pointer_notify_clear_focus(self) -> None:
        """Notify the seat of a pointer leave event to the currently-focused surface.

        Defers to any grab of the pointer.
        """
        return lib.wlr_seat_pointer_notify_clear_focus(self._ptr)

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

    def pointer_has_grab(self) -> bool:
        """Whether or not the pointer has a grab other than the default grab"""
        return lib.wlr_seat_pointer_has_grab(self._ptr)

    def grab(self) -> KeyboardGrab:
        """Start a grab of the keyboard of this seat"""
        return KeyboardGrab(self)

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

    def touch_send_down(
        self,
        surface: Surface,
        time_msec: int,
        touch_id: int,
        surface_x: float,
        surface_y: float,
    ) -> int:
        """
        Send a touch down event to the client of the given surface. All future touch
        events for this point will go to this surface. If the touch down is valid,
        this will add a new touch point with the given `touch_id`. The touch down may
        not be valid if the surface seat client does not accept touch input.
        Coordinates are surface-local. This function does not respect touch grabs:
        you probably want `touch_notify_down()` instead.
        """
        return lib.wlr_seat_touch_send_down(
            self._ptr, surface._ptr, time_msec, touch_id, surface_x, surface_y
        )

    def touch_send_up(self, time_msec: int, touch_id: int) -> None:
        """
        Send a touch up event for the touch point given by the `touch_id`. The event
        will go to the client for the surface given in the corresponding touch down
        event. This will remove the touch point. This function does not respect touch
        grabs: you probably want `touch_notify_up()` instead.
        """
        lib.wlr_seat_touch_send_up(self._ptr, time_msec, touch_id)

    def touch_send_motion(
        self, time_msec: int, touch_id: int, surface_x: float, surface_y: float
    ) -> None:
        """
        Send a touch motion event for the touch point given by the `touch_id`. The
        event will go to the client for the surface given in the corresponding touch
        down event. This function does not respect touch grabs: you probably want
        `touch_notify_motion()` instead.
        """
        lib.wlr_seat_touch_send_motion(
            self._ptr, time_msec, touch_id, surface_x, surface_y
        )

    def touch_send_cancel(self, surface: Surface) -> None:
        """
        Notify the seat that this is a global gesture and the client should cancel
        processing it. The event will go to the client for the surface given.
        This function does not respect touch grabs: you probably want
        `touch_notify_cancel()` instead.
        """
        lib.wlr_seat_touch_send_cancel(self._ptr, surface._ptr)

    def touch_send_frame(self) -> None:
        lib.wlr_seat_touch_send_frame(self._ptr)

    def touch_notify_down(
        self,
        surface: Surface,
        time_msec: int,
        touch_id: int,
        surface_x: float,
        surface_y: float,
    ) -> int:
        """
        Notify the seat of a touch down on the given surface. Defers to any grab of the
        touch device.

        Returns the serial id.
        """
        return lib.wlr_seat_touch_notify_down(
            self._ptr, surface._ptr, time_msec, touch_id, surface_x, surface_y
        )

    def touch_notify_up(self, time_msec: int, touch_id: int) -> None:
        """
        Notify the seat that the touch point given by `touch_id` is up. Defers to any
        grab of the touch device.
        """
        lib.wlr_seat_touch_notify_up(self._ptr, time_msec, touch_id)

    def touch_notify_motion(
        self, time_msec: int, touch_id: int, surface_x: float, surface_y: float
    ) -> None:
        """
        Notify the seat that the touch point given by `touch_id` has moved. Defers to
        any grab of the touch device. The seat should be notified of touch motion even
        if the surface is not the owner of the touch point for processing by grabs.
        """
        lib.wlr_seat_touch_notify_motion(
            self._ptr, time_msec, touch_id, surface_x, surface_y
        )

    def touch_point_focus(
        self,
        surface: Surface,
        time_msec: int,
        touch_id: int,
        surface_x: float,
        surface_y: float,
    ) -> None:
        """
        Notify the seat that the touch point given by `touch_id` has entered a new
        surface. The surface is required. To clear focus, use touch_point_clear_focus().
        """
        lib.wlr_seat_touch_point_focus(
            self._ptr, surface._ptr, time_msec, touch_id, surface_x, surface_y
        )

    def touch_point_clear_focus(
        self,
        time_msec: int,
        touch_id: int,
    ) -> None:
        """Clear the focused surface for the touch point given by `touch_id`."""
        lib.wlr_seat_touch_point_clear_focus(self._ptr, time_msec, touch_id)

    def touch_notify_cancel(self, surface: Surface):
        """Notify the seat that this is a global gesture and the client should
        cancel processing it. Defers to any grab of the touch device."""
        lib.wlr_seat_touch_notify_cancel(self._ptr, surface._ptr)

    def touch_notify_frame(self) -> None:
        lib.wlr_seat_touch_notify_frame(self._ptr)

    def touch_num_points(self) -> int:
        """
        How many touch points are currently down for the seat.
        """
        return lib.wlr_seat_touch_num_points(self._ptr)

    def touch_has_grab(self) -> bool:
        """
        Whether or not the seat has a touch grab other than the default grab.
        """
        return lib.wlr_seat_touch_has_grab(self._ptr)

    def touch_get_point(self, touch_id: int) -> TouchPoint | None:
        """
        Get the active touch point with the given `touch_id`.

        If the touch point does not exist or is no longer active, returns None.
        """
        ptr = lib.wlr_seat_touch_get_point(self._ptr, touch_id)
        return instance_or_none(TouchPoint, ptr)

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

    def set_primary_selection(self, source, serial: int) -> None:
        """Sets the current primary selection for the seat.

        None can be provided to clear it. This removes the previous one if
        there was any. In case the selection doesn't come from a client,
        Display.next_serial() can be used to generate a serial.
        """
        if source is None:
            lib.wlr_seat_set_primary_selection(self._ptr, ffi.NULL, serial)
        else:
            # TODO: wrap source in a data source
            lib.wlr_seat_set_primary_selection(self._ptr, source, serial)

    def validate_pointer_grab_serial(self, origin: Surface, serial: int) -> bool:
        """Check whether this serial is valid to start a pointer grab action."""
        return lib.wlr_seat_validate_pointer_grab_serial(self._ptr, origin._ptr, serial)

    def start_pointer_drag(self, drag: Drag, serial: int) -> None:
        """
        Starts a pointer drag on the seat. This starts implicit keyboard and pointer
        grabs.
        """
        lib.wlr_seat_start_pointer_drag(self._ptr, drag._ptr, serial)

    def surface_accepts_touch(self, surface: Surface) -> bool:
        return lib.wlr_surface_accepts_touch(self._ptr, surface._ptr)

    def __enter__(self) -> Seat:
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
    def hotspot(self) -> tuple[int, int]:
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
        self._ptr = ffi.cast(
            "struct wlr_seat_request_set_primary_selection_event *", ptr
        )

    # TODO: source

    @property
    def serial(self) -> int:
        return self._ptr.serial


class RequestStartDragEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_seat_request_start_drag_event *", ptr)

    @property
    def drag(self) -> Drag:
        return Drag(self._ptr.drag)

    @property
    def origin(self) -> Surface:
        return Surface(self._ptr.origin)

    @property
    def serial(self) -> int:
        return self._ptr.serial


class _FocusChangeEvent(Ptr):
    """
    Base class for ...FocusChangeEvents which provides common properties.
    """

    # TODO: wlr_seat *seat

    @property
    def old_surface(self) -> Surface:
        # TODO: May old_surface be NULL?
        return Surface(self._ptr.old_surface)

    @property
    def new_surface(self) -> Surface:
        return Surface(self._ptr.new_surface)


class PointerFocusChangeEvent(_FocusChangeEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_seat_pointer_focus_change_event *", ptr)

    @property
    def surface_x(self) -> float:
        return self._ptr.sx

    @property
    def surface_y(self) -> float:
        return self._ptr.sy


class KeyboardFocusChangeEvent(_FocusChangeEvent):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_seat_keyboard_focus_change_event *", ptr)


class SeatPointerState(Ptr):
    def __init__(self, ptr) -> None:
        """The current state of the pointer on the seat"""
        self._ptr = ptr

        self.focus_change_event = Signal(
            ptr=ffi.addressof(self._ptr.events.focus_change),
            data_wrapper=PointerFocusChangeEvent,
        )

    @property
    def surface_x(self) -> float:
        return self._ptr.sx

    @property
    def surface_y(self) -> float:
        return self._ptr.sy

    @property
    def focused_surface(self) -> Surface | None:
        """The surface that currently has keyboard focus"""
        return instance_or_none(Surface, self._ptr.focused_surface)


class SeatKeyboardState(Ptr):
    def __init__(self, ptr) -> None:
        """The current state of the keyboard on the seat"""
        self._ptr = ptr

        self.focus_change_event = Signal(
            ptr=ffi.addressof(self._ptr.events.focus_change),
            data_wrapper=KeyboardFocusChangeEvent,
        )

    @property
    def focused_surface(self) -> Surface | None:
        """The surface that is currently focused"""
        return instance_or_none(Surface, self._ptr.focused_surface)


class SeatTouchState(Ptr):
    def __init__(self, ptr) -> None:
        """The current state of touch on the seat"""
        self._ptr = ptr

    @property
    def grab_serial(self) -> int:
        return self._ptr.grab_serial

    def grab_id(self) -> int:
        return self._ptr.grab_id

    @property
    def touch_points(self) -> Iterator[TouchPoint]:
        for ptr in wl_list_for_each(
            "struct wlr_touch_point *",
            self._ptr.touch_points,
            "link",
            ffi=ffi,
        ):
            yield TouchPoint(ptr)


class TouchPoint(Ptr):
    def __init__(self, ptr):
        self._ptr = ptr

    @property
    def touch_id(self) -> int:
        return self._ptr.touch_id

    @property
    def surface_x(self) -> float:
        return self._ptr.sx

    @property
    def surface_y(self) -> float:
        return self._ptr.sy

    @property
    def surface(self) -> Surface | None:
        return instance_or_none(Surface, self._ptr.surface)

    @property
    def focused_surface(self) -> Surface | None:
        """The surface that is currently focused

        Note: wlroot calls it "focus_surface" renamed it to "focused_surface"
        to keep the name aligned to "SeatKeyboardState" and "SeatPointerState".
        """
        return instance_or_none(Surface, self._ptr.focus_surface)
