# Copyright (c) 2022 Sean Vig

from __future__ import annotations

from wlroots import lib, Ptr
from wlroots.renderer import Renderer
from wlroots.backend import Backend


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
