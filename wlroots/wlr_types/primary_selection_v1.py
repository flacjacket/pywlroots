# Copyright (c) Matt Colligan 2021

from pywayland.server import Display

from wlroots import lib, Ptr


class PrimarySelectionV1DeviceManager(Ptr):
    def __init__(self, display: Display) -> None:
        """Data manager to handle the primary selection

        :param display:
            The display to handle the clipboard for
        """
        self._ptr = lib.wlr_primary_selection_v1_device_manager_create(display._ptr)
