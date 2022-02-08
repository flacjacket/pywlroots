from pywayland.server import Display, Signal

from wlroots import Ptr, ffi, lib

from .seat import Seat


class IdleTimeout(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_idle_timeout *", ptr)

        self.idle_event = Signal(ptr=ffi.addressof(self._ptr.events.idle))
        self.resume_event = Signal(ptr=ffi.addressof(self._ptr.events.resume))
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    @property
    def idle_state(self) -> bool:
        return self._ptr.idle_state

    @property
    def enabled(self) -> bool:
        return self._ptr.enabled

    @property
    def timeout(self) -> int:
        return self._ptr.timeout

    def destroy(self) -> None:
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None


class Idle(Ptr):
    def __init__(self, display: Display) -> None:
        self._ptr = lib.wlr_idle_create(display._ptr)

        self.activity_notify_event = Signal(
            ptr=ffi.addressof(self._ptr.events.activity_notify)
        )
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    @property
    def enabled(self) -> bool:
        return self._ptr.enabled

    def notify_activity(self, seat: Seat) -> None:
        """
        Send notification to restart all timers for the given seat. Called by
        compositor when there is an user activity event on that seat.
        """
        lib.wlr_idle_notify_activity(self._ptr, seat._ptr)

    def set_enabled(self, seat: Seat, enabled: bool):
        """
        Enable or disable timers for a given idle resource by seat.
        Passing a NULL seat means update timers for all seats.
        """
        lib.wlr_idle_set_enabled(self._ptr, seat._ptr, enabled)

    def idle_timeout_create(self, seat: Seat, timeout: int) -> IdleTimeout:
        """
        Create a new timer on the given seat. The idle event will be called after
        the given amount of milliseconds of inactivity, and the resumed event will
        be sent at the first user activity after the fired event.
        """
        return IdleTimeout(lib.wlr_idle_timeout_create(self._ptr, seat._ptr, timeout))
