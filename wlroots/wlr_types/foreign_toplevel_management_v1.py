# Copyright (c) Matt Colligan 2021

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

from pywayland.server import Signal

from wlroots import ffi, Ptr, PtrHasData, lib
from .output import Output
from .surface import Surface

if TYPE_CHECKING:
    from pywayland.server import Display

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class ForeignToplevelHandleV1State(enum.IntEnum):
    MAXIMIZED = 1 << 0
    MINIMIZED = 1 << 1
    ACTIVATED = 1 << 2
    FULLSCREEN = 1 << 3


class ForeignToplevelManagerV1(PtrHasData):
    def __init__(self, ptr) -> None:
        """An foreign toplevel manager: wlr_foreign_toplevel_manager_v1."""
        self._ptr = ffi.cast("struct wlr_foreign_toplevel_manager_v1 *", ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    @classmethod
    def create(cls, display: Display) -> ForeignToplevelManagerV1:
        """Create a wlr_foreign_toplevel_manager_v1 for the given display."""
        ptr = lib.wlr_foreign_toplevel_manager_v1_create(display._ptr)
        return cls(ptr)

    def create_handle(self) -> ForeignToplevelHandleV1:
        """Create a new wlr_foreign_toplevel_handle_v1."""
        ptr = lib.wlr_foreign_toplevel_handle_v1_create(self._ptr)
        return ForeignToplevelHandleV1(ptr)


class ForeignToplevelHandleV1(PtrHasData):
    def __init__(self, ptr) -> None:
        """struct wlr_foreign_toplevel_handle_v1"""
        self._ptr = ffi.cast("struct wlr_foreign_toplevel_handle_v1 *", ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
        self.request_maximize_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_maximize),
            data_wrapper=ForeignToplevelHandleV1MaximizedEvent,
        )
        self.request_minimize_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_minimize),
            data_wrapper=ForeignToplevelHandleV1MinimizedEvent,
        )
        self.request_activate_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_activate),
            data_wrapper=ForeignToplevelHandleV1ActivatedEvent,
        )
        self.request_fullscreen_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_fullscreen),
            data_wrapper=ForeignToplevelHandleV1FullscreenEvent,
        )
        self.request_close_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_close)
        )
        self.set_rectangle_event = Signal(
            ptr=ffi.addressof(self._ptr.events.set_rectangle),
            data_wrapper=ForeignToplevelHandleV1SetRectangleEvent,
        )

    @property
    def manager(self) -> ForeignToplevelManagerV1:
        manager_ptr = self._ptr.manager
        _weakkeydict[manager_ptr] = self._ptr
        return ForeignToplevelManagerV1(manager_ptr)

    @property
    def title(self) -> str | None:
        if self._ptr.title == ffi.NULL:
            return None
        return ffi.string(self._ptr.title).decode()

    @property
    def app_id(self) -> str | None:
        if self._ptr.app_id == ffi.NULL:
            return None
        return ffi.string(self._ptr.app_id).decode()

    @property
    def parent(self) -> ForeignToplevelHandleV1 | None:
        if self._ptr.parent == ffi.NULL:
            return None
        return ForeignToplevelHandleV1(self._ptr.parent)

    def destroy(self) -> None:
        lib.wlr_foreign_toplevel_handle_v1_destroy(self._ptr)

    def set_title(self, title: str) -> None:
        lib.wlr_foreign_toplevel_handle_v1_set_title(self._ptr, title.encode())

    def set_app_id(self, app_id: str) -> None:
        lib.wlr_foreign_toplevel_handle_v1_set_app_id(self._ptr, app_id.encode())

    def output_enter(self, output: Output) -> None:
        lib.wlr_foreign_toplevel_handle_v1_output_enter(self._ptr, output._ptr)

    def output_leave(self, output: Output) -> None:
        lib.wlr_foreign_toplevel_handle_v1_output_leave(self._ptr, output._ptr)

    def set_maximized(self, maximized: bool) -> None:
        lib.wlr_foreign_toplevel_handle_v1_set_maximized(self._ptr, maximized)

    def set_minimized(self, minimized: bool) -> None:
        lib.wlr_foreign_toplevel_handle_v1_set_minimized(self._ptr, minimized)

    def set_activated(self, activated: bool) -> None:
        lib.wlr_foreign_toplevel_handle_v1_set_activated(self._ptr, activated)

    def set_fullscreen(self, fullscreen: bool) -> None:
        lib.wlr_foreign_toplevel_handle_v1_set_fullscreen(self._ptr, fullscreen)

    def set_parent(self, parent: ForeignToplevelHandleV1) -> None:
        lib.wlr_foreign_toplevel_handle_v1_set_parent(self._ptr, parent._ptr)


class _EventBase(Ptr):
    @property
    def toplevel(self) -> ForeignToplevelHandleV1:
        """The toplevel handle associated with this event."""
        return ForeignToplevelHandleV1(self._ptr.toplevel)


class ForeignToplevelHandleV1MaximizedEvent(_EventBase):
    def __init__(self, ptr) -> None:
        """Event emitted when a maximize state change is requested."""
        self._ptr = ffi.cast(
            "struct wlr_foreign_toplevel_handle_v1_maximized_event *", ptr
        )

    @property
    def maximized(self) -> bool:
        """The requested state."""
        return self._ptr.maximized


class ForeignToplevelHandleV1MinimizedEvent(_EventBase):
    def __init__(self, ptr) -> None:
        """Event emitted when a minimize state change is requested."""
        self._ptr = ffi.cast(
            "struct wlr_foreign_toplevel_handle_v1_minimized_event *", ptr
        )

    @property
    def minimized(self) -> bool:
        """The requested state."""
        return self._ptr.minimized


class ForeignToplevelHandleV1ActivatedEvent(_EventBase):
    def __init__(self, ptr) -> None:
        """Event emitted when activation of a toplevel is requested."""
        self._ptr = ffi.cast(
            "struct wlr_foreign_toplevel_handle_v1_activated_event *", ptr
        )


class ForeignToplevelHandleV1FullscreenEvent(_EventBase):
    def __init__(self, ptr) -> None:
        """Event emitted when a fullscreen state change is requested."""
        self._ptr = ffi.cast(
            "struct wlr_foreign_toplevel_handle_v1_fullscreen_event *", ptr
        )

    @property
    def fullscreen(self) -> bool:
        """The requested state."""
        return self._ptr.fullscreen

    @property
    def output(self) -> Output:
        """The output on which to fullscreen this toplevel."""
        return Output(self._ptr.output)


class ForeignToplevelHandleV1SetRectangleEvent(_EventBase):
    def __init__(self, ptr) -> None:
        """Event emitted when new geometry for a toplevel is requested."""
        self._ptr = ffi.cast(
            "struct wlr_foreign_toplevel_handle_v1_set_rectangle_event *", ptr
        )

    @property
    def surface(self) -> Surface:
        surface_ptr = self._ptr.surface
        _weakkeydict[surface_ptr] = self._ptr
        return Surface(surface_ptr)

    @property
    def x(self) -> int:
        return self._ptr.x

    @property
    def y(self) -> int:
        return self._ptr.y

    @property
    def width(self) -> int:
        return self._ptr.width

    @property
    def height(self) -> int:
        return self._ptr.height
