# Copyright (c) Matt Colligan 2021

from dataclasses import dataclass
from typing import Iterator

from pywayland.server import Display, Signal
from pywayland.protocol.wayland import WlOutput
from pywayland.utils import wl_list_for_each

from wlroots import ffi, lib, Ptr
from .output import Output, OutputMode


@dataclass
class CustomMode:
    """The custom_mode struct member of wlr_output_state"""

    width: int
    height: int
    refresh: int


class OutputHeadV1State(Ptr):
    def __init__(self, ptr) -> None:
        """wlr_output_head_v1_state"""
        self._ptr = ptr

    @property
    def enabled(self) -> bool:
        return self._ptr.enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._ptr.enabled = value

    @property
    def x(self) -> int:
        return self._ptr.x

    @x.setter
    def x(self, value: int) -> None:
        self._ptr.x = value

    @property
    def y(self) -> int:
        return self._ptr.y

    @y.setter
    def y(self, value: int) -> None:
        self._ptr.y = value

    @property
    def scale(self) -> float:
        return self._ptr.scale

    @scale.setter
    def scale(self, value: float) -> None:
        self._ptr.scale = value

    @property
    def output(self) -> Output:
        return Output(self._ptr.output)

    @property
    def mode(self) -> OutputMode:
        return OutputMode(self._ptr.mode)

    @mode.setter
    def mode(self, value: OutputMode) -> None:
        self._ptr.mode = value._ptr

    @property
    def custom_mode(self):
        width = self._ptr.custom_mode.width
        height = self._ptr.custom_mode.height
        refresh = self._ptr.custom_mode.refresh
        return CustomMode(width, height, refresh)

    @custom_mode.setter
    def custom_mode(self):
        width = self._ptr.custom_mode.width
        height = self._ptr.custom_mode.height
        refresh = self._ptr.custom_mode.refresh
        return CustomMode(width, height, refresh)

    @property
    def transform(self) -> WlOutput.transform:
        return WlOutput.transform(self._ptr.transform)

    @transform.setter
    def transform(self, value: WlOutput.transform) -> None:
        self._ptr.transform = value


class OutputConfigurationV1(Ptr):
    def __init__(self, ptr=None) -> None:
        """wlr_output_configuration_v1

        If a pointer is not given, a new instance is created. Pointers are given when
        these are returned by OutputManagerV1's events.
        """
        if ptr is None:
            self._ptr = lib.wlr_output_configuration_v1_create()
        else:
            self._ptr = ffi.cast("struct wlr_output_configuration_v1 *", ptr)

    @property
    def heads(self) -> Iterator["OutputConfigurationHeadV1"]:
        for ptr in wl_list_for_each(
            "struct wlr_output_configuration_head_v1 *",
            self._ptr.heads,
            "link",
            ffi=ffi,
        ):
            yield OutputConfigurationHeadV1(ptr)

    def send_succeeded(self) -> None:
        """
        If the configuration comes from a client request, this sends positive
        feedback to the client (configuration has been applied).
        """
        lib.wlr_output_configuration_v1_send_succeeded(self._ptr)

    def send_failed(self) -> None:
        """
        If the configuration comes from a client request, this sends negative
        feedback to the client (configuration has not been applied).
        """
        lib.wlr_output_configuration_v1_send_failed(self._ptr)

    def destroy(self) -> None:
        """Destroy the instance."""
        lib.wlr_output_configuration_v1_destroy(self._ptr)


class OutputConfigurationHeadV1(Ptr):
    def __init__(self, ptr) -> None:
        """An instance of wlr_output_configuration_head_v1"""
        self._ptr = ptr

    @classmethod
    def create(
        cls, config: OutputConfigurationV1, output: Output
    ) -> "OutputConfigurationHeadV1":
        """Create a new wlr_output_configuration_head_v1"""
        ptr = lib.wlr_output_configuration_head_v1_create(config._ptr, output._ptr)
        return OutputConfigurationHeadV1(ptr)

    @property
    def state(self) -> OutputHeadV1State:
        return OutputHeadV1State(self._ptr.state)


class OutputManagerV1(Ptr):
    def __init__(self, display: Display) -> None:
        """Create a wlr_output_manager_v1

        Create a new output manager. The compositor is responsible for calling
        `wlr_output_manager_v1_set_configuration` whenever the current output
        configuration changes.
        """
        self._ptr = lib.wlr_output_manager_v1_create(display._ptr)

        self.apply_event = Signal(
            ptr=ffi.addressof(self._ptr.events.apply),
            data_wrapper=OutputConfigurationV1,
        )
        self.test_event = Signal(
            ptr=ffi.addressof(self._ptr.events.test), data_wrapper=OutputConfigurationV1
        )

    def set_configuration(self, config: OutputConfigurationV1) -> None:
        """
        Updates the output manager's current configuration. This will broadcast any
        changes to all clients.

        This function takes ownership over `config`. That is, the compositor must not
        access the configuration anymore.
        """
        lib.wlr_output_manager_v1_set_configuration(self._ptr, config._ptr)
