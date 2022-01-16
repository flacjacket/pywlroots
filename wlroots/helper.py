# Copyright (c) 2021 Sean Vig

from __future__ import annotations

from pywayland.server import Display

from wlroots.allocator import Allocator
from wlroots.backend import Backend, BackendType
from wlroots.renderer import Renderer
from wlroots.wlr_types import Compositor


def build_compositor(
    display: Display, *, backend_type=BackendType.AUTO
) -> tuple[Compositor, Allocator, Renderer, Backend]:
    """Build and run a compositor

    :param display:
        The Wayland display to attatch to the backend, renderer, and
        compositor.
    :param backend_type:
        The type of the backend to setup the compositor for, by default use the
        auto-detected backend.
    :return:
        The compositor, allocator, renderer, and the backend.
    """
    backend = Backend(display, backend_type=backend_type)
    renderer = Renderer.autocreate(backend)
    renderer.init_display(display)
    allocator = Allocator.autocreate(backend, renderer)
    compositor = Compositor(display, renderer)

    return compositor, allocator, renderer, backend
