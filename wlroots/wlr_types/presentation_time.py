# Copyright (c) Matt Colligan 2023

from __future__ import annotations

from typing import TYPE_CHECKING

from wlroots import ffi, Ptr, lib

if TYPE_CHECKING:
    from pywayland.server import Display

    from wlroots.backend import Backend


class Presentation(Ptr):
    def __init__(self, ptr) -> None:
        """A presentation time manager: struct wlr_presentation."""
        self._ptr = ffi.cast("struct wlr_presentation *", ptr)

    @classmethod
    def create(cls, display: Display, backend: Backend) -> Presentation:
        """Create a `struct wlr_xdg_activation_v1` for the given display."""
        ptr = lib.wlr_presentation_create(display._ptr, backend._ptr)
        return cls(ptr)
