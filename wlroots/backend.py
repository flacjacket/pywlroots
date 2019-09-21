# Copyright (c) 2019 Sean Vig

import logging
import weakref

from pywayland.server import Display

from wlroots._ffi import ffi, lib

logger = logging.getLogger("wlroots")


class Backend:
    def __init__(self, display: Display) -> None:
        """Create a backend to interact with a Wayland display

        :param display:
            The Wayland server display to create the backend against.  If this
            display is destroyed, the backend will be automatically cleaned-up.
        """
        self._weak_display = weakref.ref(display)
        self._ptr = None

    def destroy(self) -> None:
        """Destroy the backend and clean up all of its resources

        Normally called automatically when the wl_display is destroyed.
        """
        if self._ptr is None:
            logger.warning("Backend already destroyed, doing nothing")
        else:
            maybe_display = self._weak_display()
            if maybe_display is not None and maybe_display._ptr is not None:
                ffi.release(self._ptr)
            else:
                logger.warning("The display has already been cleaned up, clearing backend without destroying")
                self._ptr = ffi.gc(self._ptr, None)

            self._ptr = None

    def start(self) -> None:
        """Start the backend

        This may signal new_input or new_output immediately, but may also wait
        until the display's event loop begins.
        """
        ret = lib.wlr_backend_start(self._ptr)
        if not ret:
            raise RuntimeError("Unable to start backend")

    def __enter__(self) -> "Backend":
        """Context manager to create and clean-up the backend"""
        maybe_display = self._weak_display()
        if maybe_display is None or maybe_display._ptr is None:
            raise RuntimeError("Wayland display destroyed")

        ptr = lib.wlr_backend_autocreate(maybe_display._ptr, ffi.NULL)
        if ptr == ffi.NULL:
            raise RuntimeError("Failed to create wlroots backend")

        self._ptr = ffi.gc(ptr, lib.wlr_backend_destroy)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Destroy the backend on context exit"""
        self.destroy()
