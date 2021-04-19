# Copyright (c) 2019 Sean Vig

from typing import Any, List, Tuple, Union

from pywayland.server import Display

from wlroots import ffi, lib, Ptr
from wlroots.backend import Backend
from wlroots.wlr_types import Box, Matrix, Texture

ColorType = Union[List, Tuple, ffi.CData]


class Renderer(Ptr):
    def __init__(self, backend: Backend, display: Display) -> None:
        """Obtains the renderer this backend is using

        The renderer is automatically destroyed as the backend is destroyed.

        :param backend:
            The wlroots backend to get the renderer for.
        :param display:
            The Wayland display to initialize the renderer against.
        """
        self._ptr: Any = lib.wlr_backend_get_renderer(backend._ptr)
        lib.wlr_renderer_init_wl_display(self._ptr, display._ptr)

    def begin(self, width: int, height: int) -> None:
        """Begin rendering with the given height and width"""
        lib.wlr_renderer_begin(self._ptr, width, height)

    def end(self):
        """Finish rendering"""
        lib.wlr_renderer_end(self._ptr)

    def clear(self, color: ColorType) -> None:
        """Clear the renderer to the given RGBA color"""
        if not isinstance(color, ffi.CData):
            color = ffi.new("float[4]", color)
        lib.wlr_renderer_clear(self._ptr, color)

    def render_texture(
        self, texture: Texture, projection: Matrix, x: int, y: int, alpha: float
    ) -> None:
        """Renders the requested texture"""
        ret = lib.wlr_render_texture(
            self._ptr, texture._ptr, projection._ptr, x, y, alpha
        )
        if not ret:
            # TODO: get a better exception type
            raise Exception("Bad render")

    def render_texture_with_matrix(
        self, texture: Texture, matrix: Matrix, alpha: float
    ) -> None:
        """Renders the requested texture using the provided matrix"""
        ret = lib.wlr_render_texture_with_matrix(
            self._ptr, texture._ptr, matrix._ptr, alpha
        )
        if not ret:
            # TODO: get a better exception type
            raise Exception("Bad render")

    def render_rect(self, box: Box, color: ColorType, projection: Matrix) -> None:
        """Renders a solid rectangle in the specified color."""
        if not isinstance(color, ffi.CData):
            color = ffi.new("float[4]", color)
        lib.wlr_render_rect(self._ptr, box._ptr, color, projection._ptr)
