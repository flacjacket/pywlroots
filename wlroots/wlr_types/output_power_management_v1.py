# Copyright (c) 2022

from __future__ import annotations

import enum

from pywayland.server import Display, Signal

from wlroots import Ptr, ffi, lib

from .output import Output


class OutputPowerManagementV1Mode(enum.IntEnum):
    OFF = 0
    ON = 1


class OutputPowerV1(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_output_power_v1 *", ptr)

    @property
    def output(self) -> Output:
        return Output(self._ptr.output)

    @property
    def manager(self) -> OutputPowerManagerV1:
        return OutputPowerManagerV1(self._ptr.manager)


class OutputPowerManagerV1(Ptr):
    def __init__(self, display: Display) -> None:
        self._ptr = lib.wlr_output_power_manager_v1_create(display._ptr)

        self.set_mode_event = Signal(
            ptr=ffi.addressof(self._ptr.events.set_mode),
            data_wrapper=OutputPowerV1SetModeEvent,
        )

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))


class OutputPowerV1SetModeEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_output_power_v1_set_mode_event *", ptr)

    @property
    def output(self) -> Output:
        return Output(self._ptr.output)

    @property
    def mode(self) -> OutputPowerManagementV1Mode:
        return OutputPowerManagementV1Mode(self._ptr.mode)
