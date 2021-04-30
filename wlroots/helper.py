# Copyright (c) 2021 Sean Vig

from typing import Tuple

from pywayland.server import Display

from wlroots.backend import Backend, BackendType
from wlroots.wlr_types import Compositor


def build_compositor(
    display: Display, *, backend_type=BackendType.AUTO
) -> Tuple[Compositor, Backend]:
    """Build and run a compositor

    :param display:
        The Wayland display to attatch to the backend, renderer, and
        compositor.
    :param backend_type:
        The type of the backend to setup the compositor for, by default use the
        auto-detected backend.
    :return:
        The compositor and the backend.
    """
    backend = Backend(display, backend_type=backend_type)
    renderer = backend.renderer
    renderer.init_display(display)
    compositor = Compositor(display, renderer)

    return compositor, backend
