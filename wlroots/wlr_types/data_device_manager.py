# Copyright (c) Sean Vig 2019
# Copyright (c) Matt Colligan 2021

from weakref import WeakKeyDictionary

from pywayland.server import Display, Signal

from wlroots import ffi, lib, Ptr
from .surface import Surface

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class DataDeviceManager(Ptr):
    def __init__(self, display: Display) -> None:
        """Data manager to handle the clipboard

        :param display:
            The display to handle the clipboard for
        """
        self._ptr = lib.wlr_data_device_manager_create(display._ptr)


class Drag(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_drag *", ptr)

        self.focus_event = Signal(ptr=ffi.addressof(self._ptr.events.focus))
        self.motion_event = Signal(
            ptr=ffi.addressof(self._ptr.events.motion),
            data_wrapper=DragMotionEvent,
        )
        self.drop_event = Signal(
            ptr=ffi.addressof(self._ptr.events.drop),
            data_wrapper=DragDropEvent,
        )
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    @property
    def icon(self) -> "DragIcon":
        icon_ptr = self._ptr.icon
        _weakkeydict[icon_ptr] = self._ptr
        return DragIcon(icon_ptr)

    @property
    def source(self) -> "DataSource":
        source_ptr = self._ptr.source
        _weakkeydict[source_ptr] = self._ptr
        return DataSource(source_ptr)


class DragMotionEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_drag_motion_event *", ptr)

    @property
    def drag(self) -> Drag:
        drag_ptr = self._ptr.drag
        _weakkeydict[drag_ptr] = self._ptr
        return Drag(drag_ptr)

    @property
    def sx(self) -> float:
        return self._ptr.sx

    @property
    def sy(self) -> float:
        return self._ptr.sy


class DragDropEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_drag_motion_event *", ptr)

    @property
    def drag(self) -> Drag:
        drag_ptr = self._ptr.drag
        _weakkeydict[drag_ptr] = self._ptr
        return Drag(drag_ptr)


class DragIcon(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_drag_icon *", ptr)

        self.map_event = Signal(ptr=ffi.addressof(self._ptr.events.map))
        self.unmap_event = Signal(ptr=ffi.addressof(self._ptr.events.unmap))
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    @property
    def drag(self) -> Drag:
        drag_ptr = self._ptr.drag
        _weakkeydict[drag_ptr] = self._ptr
        return Drag(drag_ptr)

    @property
    def surface(self) -> "Surface":
        surface_ptr = self._ptr.surface
        _weakkeydict[surface_ptr] = self._ptr
        return Surface(surface_ptr)

    @property
    def mapped(self) -> bool:
        return self._ptr.mapped


class DataSource(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_data_source *", ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    def destroy(self) -> None:
        lib.wlr_data_source_destroy(self._ptr)
