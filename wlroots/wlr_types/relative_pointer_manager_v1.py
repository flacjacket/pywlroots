# Copyright (c) Matt Colligan 2021

from __future__ import annotations

import typing

from pywayland.server import Signal

from wlroots import Ptr, ffi, lib

if typing.TYPE_CHECKING:
    from pywayland.server import Display

    from .seat import Seat


class RelativePointerManagerV1(Ptr):
    def __init__(self, display: Display) -> None:
        """A global interface used for getting the relative pointer object for a given
        pointer.

        :param display:
            The display to manage relative pointer events on.
        """
        self._ptr = lib.wlr_relative_pointer_manager_v1_create(display._ptr)

        self.destroy_event = Signal(
            ptr=ffi.addressof(self._ptr.events.destroy),
        )
        self.new_relative_pointer_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_relative_pointer),
            data_wrapper=RelativePointerV1,
        )

    def send_relative_motion(
        self,
        seat: Seat,
        time_usec: int,
        dx: float,
        dy: float,
        dx_unaccel: float,
        dy_unaccel: float,
    ) -> None:
        lib.wlr_relative_pointer_manager_v1_send_relative_motion(
            self._ptr, seat._ptr, time_usec, dx, dy, dx_unaccel, dy_unaccel
        )


class RelativePointerV1(Ptr):
    def __init__(self, ptr) -> None:
        """A `struct wlr_relative_pointer_v1` instance."""
        self._ptr = ffi.cast("struct wlr_relative_pointer_v1 *", ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
