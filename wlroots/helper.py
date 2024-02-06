# Copyright (c) 2021 Sean Vig

from __future__ import annotations

from pywayland.server import Display

from wlroots.allocator import Allocator
from wlroots.backend import Backend, BackendType
from wlroots.renderer import Renderer
from wlroots.wlr_types import Compositor, SubCompositor


def build_compositor(
    display: Display,
    *,
    backend_type=BackendType.AUTO,
    compositor_version: int = 5,
) -> tuple[Compositor, Allocator, Renderer, Backend, SubCompositor]:
    """Build and run a compositor

    :param display:
        The Wayland display to attatch to the backend, renderer, and
        compositor.
    :param backend_type:
        The type of the backend to setup the compositor for, by default use the
        auto-detected backend.
    :param compositor_version:
        The version of the wlr_compositor interface to use.
    :return:
        The compositor, allocator, renderer, and the backend.
    """
    backend = Backend(display, backend_type=backend_type)
    renderer = Renderer.autocreate(backend)
    renderer.init_display(display)
    allocator = Allocator.autocreate(backend, renderer)
    compositor = Compositor(display, compositor_version, renderer)
    subcompositor = SubCompositor(display)

    return compositor, allocator, renderer, backend, subcompositor
