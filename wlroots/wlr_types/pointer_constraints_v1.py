# Copyright (c) Matt Colligan 2021

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

from pywayland.server import Signal

from wlroots import ffi, lib, Ptr
from .surface import Surface
from wlroots.util.region import PixmanRegion32

if TYPE_CHECKING:
    from pywayland.server import Display

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class PointerConstraintV1Type(enum.IntEnum):
    LOCKED = lib.WLR_POINTER_CONSTRAINT_V1_LOCKED
    CONFINED = lib.WLR_POINTER_CONSTRAINT_V1_CONFINED


class PointerConstraintV1StateField(enum.IntEnum):
    REGION = lib.WLR_POINTER_CONSTRAINT_V1_STATE_REGION
    CURSOR_HINT = lib.WLR_POINTER_CONSTRAINT_V1_STATE_CURSOR_HINT


class PointerConstraintsV1(Ptr):
    def __init__(self, display: Display) -> None:
        """Manager to handle pointer constraint requests.

        :param display:
            The display to manage pointer constraints on.
        """
        self._ptr = lib.wlr_pointer_constraints_v1_create(display._ptr)

        self.new_constraint_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_constraint),
            data_wrapper=PointerConstraintV1,
        )


class PointerConstraintV1(Ptr):
    def __init__(self, ptr) -> None:
        """A `struct wlr_pointer_constraint_v1` instance."""
        self._ptr = ffi.cast("struct wlr_pointer_constraint_v1 *", ptr)

        self.set_region_event = Signal(
            ptr=ffi.addressof(self._ptr.events.set_region),
        )
        self.destroy_event = Signal(
            ptr=ffi.addressof(self._ptr.events.destroy),
            data_wrapper=PointerConstraintV1,
        )

    def send_activated(self) -> None:
        lib.wlr_pointer_constraint_v1_send_activated(self._ptr)

    def send_deactivated(self) -> None:
        lib.wlr_pointer_constraint_v1_send_deactivated(self._ptr)

    @property
    def surface(self) -> Surface:
        surface_ptr = self._ptr.surface
        _weakkeydict[surface_ptr] = self._ptr
        return Surface(surface_ptr)

    @property
    def type(self) -> PointerConstraintV1Type:
        return PointerConstraintV1Type(self._ptr.type)

    @property
    def region(self) -> PixmanRegion32:
        region_ptr = ffi.addressof(self._ptr, "region")
        return PixmanRegion32(region_ptr)

    @property
    def current(self) -> PointerConstraintV1State:
        return PointerConstraintV1State(self._ptr.current)

    @property
    def pending(self) -> PointerConstraintV1State:
        return PointerConstraintV1State(self._ptr.pending)


class PointerConstraintV1State(Ptr):
    def __init__(self, ptr):
        self._ptr = ptr

    @property
    def committed(self) -> PointerConstraintV1StateField:
        return PointerConstraintV1StateField(self._ptr.committed)

    @property
    def region(self) -> PixmanRegion32:
        return PixmanRegion32(self._ptr.region)

    @property
    def cursor_hint(self) -> tuple[float, float]:
        return self._ptr.cursor_hint.x, self._ptr.cursor_hint.y
