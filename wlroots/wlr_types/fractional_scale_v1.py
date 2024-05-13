# Copyright (c) 2024 Jeroen Wijenbergh

from pywayland.server import Display

from wlroots import PtrHasData, lib

from .compositor import Surface


class FractionalScaleManagerV1(PtrHasData):
    def __init__(self, display: Display, version: int = 1) -> None:
        """Create a wlr_fractional_scale_manager_v1"""
        self._ptr = lib.wlr_fractional_scale_manager_v1_create(display._ptr, version)


def notify_scale(surface: Surface, scale: float):
    lib.wlr_fractional_scale_v1_notify_scale(surface._ptr, scale)
