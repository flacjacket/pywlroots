# Copyright (c) 2019 Sean Vig

import logging

from pywayland.server import Display

from wlroots.backend import Backend
from ._ffi import ffi, lib

logger = logging.getLogger("wlroots")


class Renderer:
    def __init__(self, backend: Backend, display: Display) -> None:
        """Obtains the renderer this backend is using

        The renderer is automatically destroyed as the backend is destroyed.

        :param backend:
            The wlroots backend to get the renderer for.
        :param display:
            The Wayland display to initialize the renderer against.
        """
        self._ptr = lib.wlr_backend_get_renderer(backend._ptr)
        lib.wlr_renderer_init_wl_display(self._ptr, display._ptr)
