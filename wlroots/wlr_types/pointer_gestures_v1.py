# Copyright (c) Matt Colligan 2022

from __future__ import annotations

from typing import TYPE_CHECKING

from pywayland.server import Signal

from wlroots import ffi, lib, PtrHasData

if TYPE_CHECKING:
    from pywayland.server import Display

    from .seat import Seat


class PointerGesturesV1(PtrHasData):
    def __init__(self, display: Display) -> None:
        """Manager to relay pointer gestures to clients.

        :param display:
            The display to relay gestures for.
        """
        self._ptr = lib.wlr_pointer_gestures_v1_create(display._ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    def send_swipe_begin(self, seat: Seat, time_msec: int, fingers: int) -> None:
        lib.wlr_pointer_gestures_v1_send_swipe_begin(
            self._ptr,
            seat._ptr,
            time_msec,
            fingers,
        )

    def send_swipe_update(
        self, seat: Seat, time_msec: int, dx: float, dy: float
    ) -> None:
        lib.wlr_pointer_gestures_v1_send_swipe_update(
            self._ptr,
            seat._ptr,
            time_msec,
            dx,
            dy,
        )

    def send_swipe_end(self, seat: Seat, time_msec: int, cancelled: bool) -> None:
        lib.wlr_pointer_gestures_v1_send_swipe_end(
            self._ptr,
            seat._ptr,
            time_msec,
            cancelled,
        )

    def send_pinch_begin(self, seat: Seat, time_msec: int, fingers: int) -> None:
        lib.wlr_pointer_gestures_v1_send_pinch_begin(
            self._ptr,
            seat._ptr,
            time_msec,
            fingers,
        )

    def send_pinch_update(
        self,
        seat: Seat,
        time_msec: int,
        dx: float,
        dy: float,
        scale: float,
        rotation: float,
    ) -> None:
        lib.wlr_pointer_gestures_v1_send_pinch_update(
            self._ptr,
            seat._ptr,
            time_msec,
            dx,
            dy,
            scale,
            rotation,
        )

    def send_pinch_end(self, seat: Seat, time_msec: int, cancelled: bool) -> None:
        lib.wlr_pointer_gestures_v1_send_pinch_end(
            self._ptr,
            seat._ptr,
            time_msec,
            cancelled,
        )

    def send_hold_begin(self, seat: Seat, time_msec: int, fingers: int) -> None:
        lib.wlr_pointer_gestures_v1_send_hold_begin(
            self._ptr,
            seat._ptr,
            time_msec,
            fingers,
        )

    def send_hold_end(self, seat: Seat, time_msec: int, cancelled: bool) -> None:
        lib.wlr_pointer_gestures_v1_send_hold_end(
            self._ptr,
            seat._ptr,
            time_msec,
            cancelled,
        )
