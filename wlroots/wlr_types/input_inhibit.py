# Copyright (c) 2021 Graeme Holliday

import warnings

from pywayland.server import Client, Display, Signal

from wlroots import Ptr, ffi, lib


class InputInhibitManager(Ptr):
    def __init__(self, display: Display) -> None:
        """Creates a wlr_input_inhibit_manager"""
        warnings.warn(
            "Following the protocol deprecation, wlr/types/wlr_input_inhibitor.h is"
            " deprecated and will be removed in the next release.",
            DeprecationWarning,
            stacklevel=1,
        )

        self._ptr = lib.wlr_input_inhibit_manager_create(display._ptr)

        self.activate_event = Signal(ptr=ffi.addressof(self._ptr.events.activate))
        self.deactivate_event = Signal(ptr=ffi.addressof(self._ptr.events.deactivate))
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    def is_inactive(self) -> bool:
        return not self._ptr.active_inhibitor

    @property
    def active_client(self) -> Client:
        return Client(ptr=self._ptr.active_client)
