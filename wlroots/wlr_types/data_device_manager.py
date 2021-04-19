# Copyright (c) Sean Vig 2019

from pywayland.server import Display

from wlroots import lib, Ptr


class DataDeviceManager(Ptr):
    def __init__(self, display: Display) -> None:
        """Data manager to handle the clipboard

        :param display:
            The display to handle the clipboard for
        """
        self._ptr = lib.wlr_data_device_manager_create(display._ptr)
