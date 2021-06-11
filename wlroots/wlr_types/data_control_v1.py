# Copyright (c) Matt Colligan 2021

from pywayland.server import Display

from wlroots import lib, Ptr


class DataControlManagerV1(Ptr):
    def __init__(self, display: Display) -> None:
        """A `struct wlr_data_control_manager_v1`

        :param display:
            The display
        """
        self._ptr = lib.wlr_data_control_manager_v1_create(display._ptr)
