# Copyright (c) Antonin Riha 2022
from pywayland.server import Display, Signal

from wlroots import Ptr, ffi, lib, PtrHasData

from .surface import Surface


class IdleInhibitorManagerV1(Ptr):
    def __init__(self, display: Display) -> None:
        self._ptr = lib.wlr_idle_inhibit_v1_create(display._ptr)

        self.new_inhibitor_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_inhibitor),
            data_wrapper=IdleInhibitorV1,
        )
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))


class IdleInhibitorV1(PtrHasData):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_idle_inhibitor_v1 *", ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    @property
    def surface(self) -> Surface:
        return Surface(self._ptr.surface)
