# Copyright (c) Sean Vig 2019

from pywayland.server import Display

from wlroots import ffi, lib


class XdgShell:
    def __init__(self, display: Display) -> None:
        """Create the shell for protocol windows

        :param display:
            The Wayland server display to create the shell on.
        """
        ptr = lib.wlr_xdg_shell_create(display._ptr)
        self._ptr = ffi.gc(ptr, lib.wlr_xdg_shell_destroy)

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
