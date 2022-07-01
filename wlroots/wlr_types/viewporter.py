# Copyright (c) 2022 Aakash Sen Sharma

from pywayland.server import Display, Signal
from wlroots import Ptr, ffi, lib


class Viewporter(Ptr):
    def __init__(self, display: Display) -> None:
        """A `struct wlr_viewporter`

        :param display:
            The wayland display
        """

        self._ptr = lib.wlr_viewporter_create(display._ptr)
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
