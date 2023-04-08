# Copyright (c) Charbel Assaad 2023
from pywayland.server import Display

from wlroots import lib, Ptr

from .seat import Seat


class IdleNotifierV1(Ptr):
    def __init__(self, display: Display) -> None:
        self._ptr = lib.wlr_idle_notifier_v1_create(display._ptr)

    @property
    def inhibited(self) -> bool:
        return bool(self._ptr.inhibited)

    def set_inhibited(self, inhibited: bool) -> None:
        """
        Inhibit idle.

        Compositors should call this function when the idle state is disabled, e.g.
        because a visible client is using the idle-inhibit protocol.
        """
        lib.wlr_idle_notifier_v1_set_inhibited(self._ptr, inhibited)

    def notify_activity(self, seat: Seat) -> None:
        """
        Notify for user activity on a seat.

        Compositors should call this function whenever an input event is triggered
        on a seat.
        """
        lib.wlr_idle_notifier_v1_notify_activity(self._ptr, seat._ptr)
