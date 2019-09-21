# Copyright (c) 2019 Sean Vig

from pywayland.server import Display

from wlroots import ffi, lib
from wlroots.renderer import Renderer


class Compositor:
    def __init__(self, display: Display, renderer: Renderer):
        """A compositor for clients to be able to allocate surfaces

        :param display:
            The Wayland server display to attach to the compositor.
        :param renderer:
            The wlroots renderer to attach the compositor to.
        """
        ptr = lib.wlr_compositor_create(display._ptr, renderer._ptr)
        self._ptr = ffi.gc(ptr, lib.wlr_compositor_destroy)

    def destroy(self) -> None:
        """Clean up the compositor"""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    def __enter__(self) -> "Compositor":
        """Context manager to clean up the compositor"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Clean-up the compositor when exiting the context"""
        self.destroy()
