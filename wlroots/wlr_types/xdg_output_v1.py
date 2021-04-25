# Copyright (c) 2021 Matt Colligan

from pywayland.server import Display, Signal

from wlroots import ffi, lib, Ptr
from .output_layout import OutputLayout


class XdgOutputManagerV1(Ptr):
    def __init__(self, display: "Display", layout: "OutputLayout") -> None:
        """Create an wlr_xdg_output_manager_v1"""
        self._ptr = lib.wlr_xdg_output_manager_v1_create(display._ptr, layout._ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
