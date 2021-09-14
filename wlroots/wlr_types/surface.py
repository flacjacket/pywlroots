# Copyright Sean Vig (c) 2020

from __future__ import annotations

from weakref import WeakKeyDictionary

from pywayland.protocol.wayland import WlOutput
from pywayland.server import Signal

from wlroots import ffi, PtrHasData, lib, Ptr
from wlroots.util.clock import Timespec
from .texture import Texture

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class Surface(PtrHasData):
    def __init__(self, ptr):
        """Create a wlroots Surface

        :param ptr:
            The cdata for the given surface
        """
        self._ptr = ptr

        self.commit_event = Signal(ptr=ffi.addressof(self._ptr.events.commit))
        self.new_subsurface_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_subsurface),
            data_wrapper=SubSurface,
        )
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    def __eq__(self, other: object) -> bool:
        """Check if the other surface is equal by the cdata pointer"""
        if not isinstance(other, Surface):
            return NotImplemented

        return self._ptr == other._ptr

    @property
    def is_xdg_surface(self) -> bool:
        """True if the current surface is an XDG surface"""
        return lib.wlr_surface_is_xdg_surface(self._ptr)

    @property
    def is_layer_surface(self) -> bool:
        """True if the current surface is a layer surface"""
        return lib.wlr_surface_is_layer_surface(self._ptr)

    @property
    def sx(self) -> int:
        """Surface local buffer x position"""
        return self._ptr.sx

    @property
    def sy(self) -> int:
        """Surface local buffer y position"""
        return self._ptr.sy

    @property
    def current(self) -> SurfaceState:
        """The current commited surface state"""
        current_ptr = self._ptr.current
        _weakkeydict[current_ptr] = self._ptr
        return SurfaceState(current_ptr)

    @property
    def previous(self) -> SurfaceState:
        """The state of the previous commit"""
        previous_ptr = self._ptr.previous
        _weakkeydict[previous_ptr] = self._ptr
        return SurfaceState(previous_ptr)

    def get_texture(self):
        """Get the texture of the buffer currently attached to this surface

        Returns None if no buffer is currently attached or if something went
        wrong with uploading the buffer.
        """
        texture_ptr = lib.wlr_surface_get_texture(self._ptr)
        if texture_ptr == ffi.NULL:
            return None

        return Texture(texture_ptr)

    def send_frame_done(self, when: Timespec) -> None:
        """Send a frame done event to the surface"""
        lib.wlr_surface_send_frame_done(self._ptr, when._ptr)


class SurfaceState(Ptr):
    def __init__(self, ptr):
        """The state of a given surface

        :param ptr:
            The cdata of the given surface state.
        """
        self._ptr = ptr

    @property
    def transform(self) -> WlOutput.transform:
        """Get the transform for the selected surface"""
        return WlOutput.transform(self._ptr.transform)

    @property
    def width(self) -> int:
        """In surface local width"""
        return self._ptr.width

    @property
    def height(self) -> int:
        """In surface local height"""
        return self._ptr.height


class SubSurface(PtrHasData):
    def __init__(self, ptr):
        """A wlroots subsurface

        :param ptr:
            The cdata for the given subsurface
        """
        self._ptr = ffi.cast("struct wlr_subsurface *", ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
        self.map_event = Signal(ptr=ffi.addressof(self._ptr.events.map))
        self.unmap_event = Signal(ptr=ffi.addressof(self._ptr.events.unmap))

    @property
    def surface(self) -> Surface:
        """Get the wlr_surface underlying this subsurface"""
        return Surface(self._ptr.surface)
