# Copyright (c) Sean Vig 2019

from pywayland.server import Display

from wlroots import ffi, lib


class DataDeviceManager:
    def __init__(self, display: Display) -> None:
        """Data manager to handle the clipboard

        :param display:
            The display to handle the clipboard for
        """
        ptr = lib.wlr_data_device_manager_create(display._ptr)
        self._ptr = ffi.gc(ptr, lib.wlr_data_device_manager_destroy)

    def destroy(self) -> None:
        """Clean-up the device manager"""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    def __enter__(self) -> "DataDeviceManager":
        """Context manager to clean up the device manager"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Clean-up the device manager when exiting the context"""
        self.destroy()
