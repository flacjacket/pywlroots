# Copyright (c) 2022 Sean Vig

from __future__ import annotations

from wlroots import Ptr, ffi, lib
from wlroots.backend import Backend
from wlroots.renderer import Renderer, DRMFormat
from wlroots.wlr_types.buffer import Buffer


class Allocator(Ptr):
    def __init__(self, ptr) -> None:
        """Create an allocator.

        The allocator is the bridge between the renderer and the backend. It
        handles the buffer creation, allowing wlroots to render onto the
        screen.
        """
        self._ptr = ptr

    @classmethod
    def autocreate(cls, backend: Backend, renderer: Renderer) -> Allocator:
        """Creates the adequate allocator given a backend and a renderer."""
        ret = lib.wlr_allocator_autocreate(backend._ptr, renderer._ptr)
        if not ret:
            raise RuntimeError("Unable to create an allocator.")
        return Allocator(ret)

    def create_buffer(self, width: int, height: int, format: DRMFormat) -> Buffer:
        """Creates the adequate allocator given a backend and a renderer."""
        ptr = lib.wlr_allocator_create_buffer(self._ptr, width, height, format._ptr)
        ptr = ffi.gc(ptr, lib.wlr_buffer_drop)
        return Buffer(ptr)
