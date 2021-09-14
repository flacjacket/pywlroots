# Copyright (c) Matt Colligan 2021

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

from pywayland.server import Signal

from wlroots import ffi, PtrHasData, lib
from .surface import Surface

if TYPE_CHECKING:
    from pywayland.server import Display

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class XdgToplevelDecorationV1Mode(enum.IntEnum):
    NONE = lib.WLR_XDG_TOPLEVEL_DECORATION_V1_MODE_NONE
    CLIENT_SIDE = lib.WLR_XDG_TOPLEVEL_DECORATION_V1_MODE_CLIENT_SIDE
    SERVER_SIDE = lib.WLR_XDG_TOPLEVEL_DECORATION_V1_MODE_SERVER_SIDE


class XdgDecorationManagerV1(PtrHasData):
    def __init__(self, ptr) -> None:
        """An XDG decoration manager: wlr_xdg_decoration_manager_v1."""
        self._ptr = ffi.cast("struct wlr_xdg_decoration_manager_v1 *", ptr)

        self.new_toplevel_decoration_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_toplevel_decoration),
            data_wrapper=XdgToplevelDecorationV1,
        )
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    @classmethod
    def create(cls, display: Display):
        """Create a wlr_xdg_decoration_manager_v1 for the given display."""
        ptr = lib.wlr_xdg_decoration_manager_v1_create(display._ptr)
        return cls(ptr)


class XdgToplevelDecorationV1(PtrHasData):
    def __init__(self, ptr) -> None:
        """struct wlr_xdg_toplevel_decoration_v1"""
        self._ptr = ffi.cast("struct wlr_xdg_toplevel_decoration_v1 *", ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
        self.request_mode_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_mode)
        )

    @property
    def surface(self) -> Surface:
        surface_ptr = self._ptr.surface
        _weakkeydict[surface_ptr] = self._ptr
        return Surface(surface_ptr)

    @property
    def manager(self) -> XdgDecorationManagerV1:
        manager_ptr = self._ptr.manager
        _weakkeydict[manager_ptr] = self._ptr
        return XdgDecorationManagerV1(manager_ptr)

    @property
    def added(self) -> bool:
        return self._ptr.added

    @property
    def current_mode(self) -> XdgToplevelDecorationV1Mode:
        return XdgToplevelDecorationV1Mode(self._ptr.current_mode)

    @property
    def client_pending_mode(self) -> XdgToplevelDecorationV1Mode:
        return XdgToplevelDecorationV1Mode(self._ptr.client_pending_mode)

    @property
    def server_pending_mode(self) -> XdgToplevelDecorationV1Mode:
        return XdgToplevelDecorationV1Mode(self._ptr.server_pending_mode)

    def set_mode(self, mode: XdgToplevelDecorationV1Mode) -> int:
        if mode == XdgToplevelDecorationV1Mode.NONE:
            raise ValueError("Toplevel decoration mode cannot be set to NONE.")
        return lib.wlr_xdg_toplevel_decoration_v1_set_mode(self._ptr, mode)
