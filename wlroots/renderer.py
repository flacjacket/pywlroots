# Copyright (c) 2019 Sean Vig

from __future__ import annotations

import contextlib
from typing import Iterator, Union

from pywayland.server import Display

from wlroots import Ptr, ffi, lib
from wlroots.backend import Backend
from wlroots.util.box import Box
from wlroots.wlr_types import Matrix, Texture

ColorType = Union[list, tuple, ffi.CData]


class Renderer(Ptr):
    def __init__(self, ptr) -> None:
        """Obtains the renderer this backend is using

        The renderer is automatically destroyed as the backend is destroyed.
        """
        self._ptr = ptr

    @staticmethod
    def autocreate(backend: Backend) -> Renderer:
        """Creates a suitable renderer for a backend."""
        renderer_ptr = lib.wlr_renderer_autocreate(backend._ptr)
        if renderer_ptr == ffi.NULL:
            raise RuntimeError("Unable to create a renderer.")
        return Renderer(renderer_ptr)

    def init_display(self, display: Display) -> None:
        """Creates necessary shm and invokes the initialization of the implementation

        :param display:
            The Wayland display to initialize the renderer against.
        """
        ret = lib.wlr_renderer_init_wl_display(self._ptr, display._ptr)
        if not ret:
            raise RuntimeError("Unable to initialize renderer for display")

    @contextlib.contextmanager
    def render(self, width: int, height: int) -> Iterator[Renderer]:
        """Render within the generated context"""
        self.begin(width, height)
        try:
            yield self
        finally:
            self.end()

    def begin(self, width: int, height: int) -> bool:
        """Begin rendering with the given height and width"""
        return lib.wlr_renderer_begin(self._ptr, width, height)

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
    ) -> bool:
        """Renders the requested texture"""
        return lib.wlr_render_texture(
            self._ptr, texture._ptr, projection._ptr, x, y, alpha
        )

    def render_texture_with_matrix(
        self, texture: Texture, matrix: Matrix, alpha: float
    ) -> bool:
        """Renders the requested texture using the provided matrix"""
        return lib.wlr_render_texture_with_matrix(
            self._ptr, texture._ptr, matrix._ptr, alpha
        )

    def render_rect(self, box: Box, color: ColorType, projection: Matrix) -> None:
        """Renders a solid rectangle in the specified color."""
        if not isinstance(color, ffi.CData):
            color = ffi.new("float[4]", color)
        lib.wlr_render_rect(self._ptr, box._ptr, color, projection._ptr)

    def scissor(self, box: Box | None) -> None:
        """
        Defines a scissor box. Only pixels that lie within the scissor box can be
        modified by drawing functions. Providing a NULL `box` disables the scissor
        box.
        """
        lib.wlr_renderer_scissor(self._ptr, box._ptr if box else ffi.NULL)


class DRMFormatSet(Ptr):
    """struct wlr_drm_format_set"""

    def __init__(self, ptr) -> None:
        self._ptr = ptr

    def get(self, format: int) -> DRMFormat | None:
        ptr = lib.wlr_drm_format_set_get(self._ptr, format)
        if ptr == ffi.NULL:
            return None
        return DRMFormat(ptr)


class DRMFormat(Ptr):
    """struct wlr_drm_format"""

    def __init__(self, ptr) -> None:
        self._ptr = ptr
