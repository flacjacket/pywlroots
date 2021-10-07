# Copyright (c) 2021 Graeme Holliday

from pywayland.server import Display, Signal

from wlroots import ffi, Ptr, lib


class InputInhibitManager(Ptr):
    def __init__(self, display: Display) -> None:
        """Creates a wlr_input_inhibit_manager"""
        self._ptr = lib.wlr_input_inhibit_manager_create(display._ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    def is_inactive(self) -> bool:
        return not self._ptr.active_inhibitor
