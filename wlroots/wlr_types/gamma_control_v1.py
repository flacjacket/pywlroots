# Copyright (c) 2021 Matt Colligan

from pywayland.server import Display, Signal

from wlroots import ffi, PtrHasData, lib


class GammaControlManagerV1(PtrHasData):
    def __init__(self, display: Display) -> None:
        """Creates a wlr_gamma_control_manager_v1"""
        self._ptr = lib.wlr_gamma_control_manager_v1_create(display._ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
