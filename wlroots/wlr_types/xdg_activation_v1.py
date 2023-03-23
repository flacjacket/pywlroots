# Copyright (c) Matt Colligan 2023

from __future__ import annotations

from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

from pywayland.server import Signal

from wlroots import ffi, Ptr, lib
from .surface import Surface

if TYPE_CHECKING:
    from pywayland.server import Display

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class XdgActivationV1(Ptr):
    def __init__(self, ptr) -> None:
        """An XDG activation manager: struct wlr_xdg_activation_v1."""
        self._ptr = ffi.cast("struct wlr_xdg_activation_v1 *", ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
        self.request_activate_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_activate),
            data_wrapper=XdgActivationV1RequestActivateEvent,
        )

    @classmethod
    def create(cls, display: Display) -> XdgActivationV1:
        """Create a `struct wlr_xdg_activation_v1` for the given display."""
        ptr = lib.wlr_xdg_activation_v1_create(display._ptr)
        return cls(ptr)


class XdgActivationV1RequestActivateEvent(Ptr):
    def __init__(self, ptr) -> None:
        """struct wlr_xdg_activation_v1_request_activate_event"""
        self._ptr = ffi.cast(
            "struct wlr_xdg_activation_v1_request_activate_event *", ptr
        )

    @property
    def surface(self) -> Surface:
        surface_ptr = self._ptr.surface
        _weakkeydict[surface_ptr] = self._ptr
        return Surface(surface_ptr)
