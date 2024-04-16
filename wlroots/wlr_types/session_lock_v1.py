"""
Support for the ext-session-lock-v1 protocol.

Secure session locking with arbitrary graphics

This protocol allows for a privileged Wayland client to lock the session and
display arbitrary graphics while the session is locked.

The compositor may choose to restrict this protocol to a special client
launched by the compositor itself or expose it to all privileged clients,
this is compositor policy.

The client is responsible for performing authentication and informing the
compositor when the session should be unlocked. If the client dies while the
session is locked the session remains locked, possibly permanently depending
on compositor policy.
"""

from __future__ import annotations

from weakref import WeakKeyDictionary

from pywayland.server import Display, Signal

from wlroots import PtrHasData, ffi, lib
from wlroots.wlr_types.output import Output

from .compositor import Surface

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class SessionLockManagerV1(PtrHasData):

    def __init__(self, display: Display) -> None:
        self._ptr = lib.wlr_session_lock_manager_v1_create(display._ptr)
        self.new_lock_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_lock), data_wrapper=SessionLockV1
        )
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))


class SessionLockV1(PtrHasData):

    def __init__(self, ptr):
        self._ptr = ffi.cast("struct wlr_session_lock_v1 *", ptr)
        self.new_surface_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_surface),
            data_wrapper=SessionLockSurfaceV1,
        )
        self.unlock_event = Signal(ptr=ffi.addressof(self._ptr.events.unlock))
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    def send_locked(self):
        lib.wlr_session_lock_v1_send_locked(self._ptr)

    def destroy(self):
        lib.wlr_session_lock_v1_destroy(self._ptr)


class SessionLockSurfaceV1(PtrHasData):
    """
    A surface displayed while the session is locked
    """

    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_session_lock_surface_v1 *", ptr)
        self.map_event = Signal(ptr=ffi.addressof(self._ptr.events.map))
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    @property
    def output(self) -> Output:
        output_ptr = self._ptr.output
        _weakkeydict[output_ptr] = self._ptr
        return Output(output_ptr)

    @property
    def surface(self) -> Surface:
        surface_ptr = self._ptr.surface
        _weakkeydict[surface_ptr] = self._ptr
        return Surface(surface_ptr)

    @property
    def configured(self) -> bool:
        return self._ptr.configured

    @property
    def mapped(self) -> bool:
        return self._ptr.mapped

    def configure(self, width: int, height: int) -> int:
        """
        Configures the width and height of the surface.

        Returns the configure serial.
        """
        return lib.wlr_session_lock_surface_v1_configure(self._ptr, width, height)

    @staticmethod
    def from_surface(surface: Surface) -> SessionLockSurfaceV1 | None:
        """
        Get a SessionLockSurfaceV1 from a surface.

        Asserts that the surface has the session lock surface role.
        May return None even if the surface has the session lock surface role if the
        corresponding session lock surface has been destroyed.
        """
        surface_ptr = lib.wlr_session_lock_surface_v1_from_wlr_surface(surface._ptr)
        return SessionLockSurfaceV1(surface_ptr) if surface_ptr != ffi.NULL else None


def surface_is_session_lock_surface_v1(surface: Surface) -> bool:
    """
    Returns true if the surface has the session lock surface role.
    """
    return lib.wlr_surface_is_session_lock_surface_v1(surface._ptr)
