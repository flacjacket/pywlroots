# Copyright (c) 2021 Matt Colligan

import enum
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple
from weakref import WeakKeyDictionary

from pywayland.server import Signal

from wlroots import ffi, PtrHasData, lib, Ptr
from .output import Output
from .surface import Surface
from .xdg_shell import SurfaceCallback, T

if TYPE_CHECKING:
    from pywayland.server import Display

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class LayerSurfaceV1KeyboardInteractivity(enum.IntEnum):
    NONE = 0
    EXCLUSIVE = 1
    ON_DEMAND = 2


class LayerSurfaceV1Anchor(enum.IntFlag):
    TOP = 1
    BOTTOM = 2
    LEFT = 4
    RIGHT = 8
    VERTICAL = TOP | BOTTOM
    HORIZONTAL = LEFT | RIGHT


class LayerShellV1Layer(enum.IntEnum):
    BACKGROUND = 0
    BOTTOM = 1
    TOP = 2
    OVERLAY = 3


@dataclass
class Margin:
    top: int
    right: int
    bottom: int
    left: int


class LayerSurfaceV1State(Ptr):
    def __init__(self, ptr):
        self._ptr = ptr

    @property
    def anchor(self) -> LayerSurfaceV1Anchor:
        return LayerSurfaceV1Anchor(self._ptr.anchor)

    @property
    def exclusive_zone(self) -> int:
        return self._ptr.exclusive_zone

    @property
    def margin(self) -> Margin:
        margin = self._ptr.margin
        return Margin(margin.top, margin.right, margin.bottom, margin.left)

    @property
    def keyboard_interactive(self) -> LayerSurfaceV1KeyboardInteractivity:
        return LayerSurfaceV1KeyboardInteractivity(self._ptr.keyboard_interactive)

    @property
    def desired_width(self) -> int:
        return self._ptr.desired_width

    @property
    def desired_height(self) -> int:
        return self._ptr.desired_height

    @property
    def actual_width(self) -> int:
        return self._ptr.actual_width

    @property
    def actual_height(self) -> int:
        return self._ptr.actual_height

    @property
    def layer(self) -> LayerShellV1Layer:
        return LayerShellV1Layer(self._ptr.layer)


class LayerSurfaceV1(PtrHasData):
    def __init__(self, ptr):
        self._ptr = ffi.cast("struct wlr_layer_surface_v1 *", ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
        self.map_event = Signal(ptr=ffi.addressof(self._ptr.events.map))
        self.unmap_event = Signal(ptr=ffi.addressof(self._ptr.events.unmap))
        self.new_popup_event = Signal(ptr=ffi.addressof(self._ptr.events.new_popup))

    @property
    def surface(self) -> Surface:
        surface_ptr = self._ptr.surface
        _weakkeydict[surface_ptr] = self._ptr
        return Surface(surface_ptr)

    @property
    def output(self) -> Optional[Output]:
        output_ptr = self._ptr.output
        if output_ptr == ffi.NULL:
            return None
        _weakkeydict[output_ptr] = self._ptr
        return Output(output_ptr)

    @output.setter
    def output(self, output: Output):
        self._ptr.output = output._ptr

    @property
    def added(self) -> bool:
        return self._ptr.added

    @property
    def configured(self) -> bool:
        return self._ptr.configured

    @property
    def mapped(self) -> bool:
        return self._ptr.mapped

    @property
    def closed(self) -> bool:
        return self._ptr.closed

    @property
    def client_pending(self) -> LayerSurfaceV1State:
        state_ptr = self._ptr.client_pending
        _weakkeydict[state_ptr] = self._ptr
        return LayerSurfaceV1State(state_ptr)

    @property
    def server_pending(self) -> LayerSurfaceV1State:
        state_ptr = self._ptr.server_pending
        _weakkeydict[state_ptr] = self._ptr
        return LayerSurfaceV1State(state_ptr)

    @property
    def current(self) -> LayerSurfaceV1State:
        state_ptr = self._ptr.current
        _weakkeydict[state_ptr] = self._ptr
        return LayerSurfaceV1State(state_ptr)

    def configure(self, width: int, height: int) -> None:
        """
        Notifies the layer surface to configure itself with this width/height. The
        layer_surface will signal its map event when the surface is ready to assume
        this size.
        """
        lib.wlr_layer_surface_v1_configure(self._ptr, width, height)

    def close(self) -> None:
        lib.wlr_layer_surface_v1_close(self._ptr)

    @classmethod
    def from_wlr_surface(cls, surface: Surface):
        surface_ptr = lib.wlr_layer_surface_v1_from_wlr_surface(surface._ptr)
        _weakkeydict[surface_ptr] = surface._ptr
        return LayerSurfaceV1(surface_ptr)

    def for_each_surface(
        self, iterator: SurfaceCallback[T], data: Optional[T] = None
    ) -> None:
        """
        Calls the iterator function for each sub-surface and popup of this surface
        """
        py_handle = (iterator, data)
        handle = ffi.new_handle(py_handle)
        lib.wlr_layer_surface_v1_for_each_surface(
            self._ptr, lib.surface_iterator_callback, handle
        )

    def surface_at(
        self, sx: float, sy: float
    ) -> Tuple[Optional[Surface], float, float]:
        """
        Find a surface within this layer-surface tree at the given surface-local
        coordinates. Returns the surface and coordinates in the leaf surface
        coordinate system or None if no surface is found at that location.
        """
        sub_x_data = ffi.new("double*")
        sub_y_data = ffi.new("double*")
        surface_ptr = lib.wlr_layer_surface_v1_surface_at(
            self._ptr, sx, sy, sub_x_data, sub_y_data
        )
        if surface_ptr == ffi.NULL:
            return None, 0.0, 0.0

        return Surface(surface_ptr), sub_x_data[0], sub_y_data[0]


class LayerShellV1(PtrHasData):
    def __init__(self, display: "Display") -> None:
        """Create an wlr_xdg_output_manager_v1"""
        self._ptr = lib.wlr_layer_shell_v1_create(display._ptr)

        self.new_surface_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_surface), data_wrapper=LayerSurfaceV1
        )
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
