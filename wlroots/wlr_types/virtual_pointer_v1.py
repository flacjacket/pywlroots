# Copyright (c) 2022 Matt Colligan

from __future__ import annotations

from typing import Iterable
from weakref import WeakKeyDictionary

from pywayland.protocol.wayland.wl_pointer import WlPointer
from pywayland.server import Display, Signal

from wlroots import Ptr, ffi, lib
from wlroots.wlr_types.input_device import InputDevice
from wlroots.wlr_types.pointer import PointerEventAxis

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class VirtualPointerManagerV1(Ptr):
    def __init__(self, display: Display) -> None:
        """A wlr_virtual_pointer_manager_v1 struct."""
        self._ptr = lib.wlr_virtual_pointer_manager_v1_create(display._ptr)

        self.new_virtual_pointer_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_virtual_pointer),
            data_wrapper=VirtualPointerV1NewPointerEvent,
        )
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))


class VirtualPointerV1NewPointerEvent(Ptr):
    def __init__(self, ptr) -> None:
        """A wlr_virtual_pointer_v1_new_pointer_event struct."""
        self._ptr = ffi.cast("struct wlr_virtual_pointer_v1_new_pointer_event *", ptr)

    @property
    def new_pointer(self) -> VirtualPointerV1:
        return VirtualPointerV1(self._ptr.new_pointer)


class VirtualPointerV1(Ptr):
    def __init__(self, ptr) -> None:
        """A wlr_virtual_pointer_v1 struct."""
        self._ptr = ffi.cast("struct wlr_virtual_pointer_v1 *", ptr)

        self.destroy_event = Signal(
            ptr=ffi.addressof(self._ptr.events.destroy), data_wrapper=VirtualPointerV1
        )

    @property
    def input_device(self) -> InputDevice:
        device_ptr = ffi.addressof(self._ptr.input_device)
        _weakkeydict[device_ptr] = self._ptr
        return InputDevice(device_ptr)

    @property
    def axis_event(self) -> Iterable[PointerEventAxis]:
        for axis_event in self._ptr.axis_event:
            yield PointerEventAxis(axis_event)

    @property
    def axis(self) -> WlPointer.axis:
        return WlPointer.axis(self._ptr.axis)

    @property
    def axis_valid(self) -> Iterable[bool]:
        yield from self._ptr.axis_valid
