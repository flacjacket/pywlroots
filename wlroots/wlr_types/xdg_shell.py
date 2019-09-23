# Copyright (c) Sean Vig 2019

import enum

from pywayland.server import Display, Signal

from wlroots import ffi, lib


class XdgSurfaceRole(enum.IntEnum):
    NONE = lib.WLR_XDG_SURFACE_ROLE_NONE
    TOPLEVEL = lib.WLR_XDG_SURFACE_ROLE_TOPLEVEL
    POPUP = lib.WLR_XDG_SURFACE_ROLE_POPUP


class XdgShell:
    def __init__(self, display: Display) -> None:
        """Create the shell for protocol windows

        :param display:
            The Wayland server display to create the shell on.
        """
        ptr = lib.wlr_xdg_shell_create(display._ptr)
        self._ptr = ffi.gc(ptr, lib.wlr_xdg_shell_destroy)

        self.new_surface_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_surface), data_wrapper=XdgSurface
        )
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    def destroy(self) -> None:
        """Destroy the xdg shell"""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    def __enter__(self) -> "XdgShell":
        """Setup the xdg shell in a context manager"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Clean up the xdg shell on context manager exit"""
        self.destroy()


class XdgSurface:
    def __init__(self, ptr) -> None:
        """A user interface element requiring management by the compositor

        An xdg-surface is a user interface element requiring management by the
        compositor. An xdg-surface alone isn't useful, a role should be
        assigned to it in order to map it.

        When a surface has a role and is ready to be displayed, the `map` event
        is emitted. When a surface should no longer be displayed, the `unmap`
        event is emitted. The `unmap` event is guaranteed to be emitted before
        the `destroy` event if the view is destroyed when mapped
        """
        self._ptr = ffi.cast("struct wlr_xdg_surface *", ptr)

        self.map_event = Signal(
            ptr=ffi.addressof(self._ptr.events.map)
        )
        self.unmap_event = Signal(
            ptr=ffi.addressof(self._ptr.events.unmap)
        )
        self.destroy_event = Signal(
            ptr=ffi.addressof(self._ptr.events.destroy)
        )

    @property
    def role(self) -> XdgSurfaceRole:
        """The role for the surface"""
        return XdgSurfaceRole(self._ptr.role)
