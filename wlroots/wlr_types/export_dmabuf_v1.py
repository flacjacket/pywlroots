# Copyright (c) 2022 Aakash Sen Sharma

from pywayland.server import Display, Signal
from wlroots import Ptr, ffi, lib


class ExportDmabufManagerV1(Ptr):
    def __init__(self, display: Display) -> None:
        """A `struct wlr_export_dmabuf_manager_v1`

        :param display:
            The wayland display
        """

        self._ptr = lib.wlr_export_dmabuf_manager_v1_create(display._ptr)
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
