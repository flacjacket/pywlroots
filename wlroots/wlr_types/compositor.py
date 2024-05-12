# Copyright (c) 2019 Sean Vig

from __future__ import annotations

from typing import TYPE_CHECKING, Final
from weakref import WeakKeyDictionary

from pywayland.protocol.wayland import WlOutput
from pywayland.server import Display, Signal

from wlroots import Ptr, PtrHasData, ffi, lib
from wlroots.util.clock import Timespec

from .texture import Texture

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()

if TYPE_CHECKING:
    from wlroots.renderer import Renderer


_MAX_COMPOSITOR_VERSION: Final = 5


class Compositor(Ptr):
    def __init__(
        self, display: Display, version: int, renderer: Renderer | None = None
    ) -> None:
        """A compositor for clients to be able to allocate surfaces

        :param display:
            The Wayland server display to attach to the compositor.
        :param version:
            The version of the wlr_compositor interface to use.
        :param renderer:
            The wlroots renderer to attach the compositor to.
        """
        if not 0 < version <= _MAX_COMPOSITOR_VERSION:
            raise ValueError(
                f"Invalid compositor version, should be a value between 1 (inclusive) and {_MAX_COMPOSITOR_VERSION} (inclusive), got: {version}"
            )
        if renderer is None:
            self._ptr = lib.wlr_compositor_create(display._ptr, version, ffi.NULL)
        else:
            self._ptr = lib.wlr_compositor_create(display._ptr, version, renderer._ptr)


class SubCompositor(Ptr):
    def __init__(self, display: Display) -> None:
        self._ptr = lib.wlr_subcompositor_create(display._ptr)


class Surface(PtrHasData):
    def __init__(self, ptr) -> None:
        """Create a wlroots Surface

        :param ptr:
            The cdata for the given surface
        """
        self._ptr = ptr

        self.precommit_event = Signal(
            ptr=ffi.addressof(self._ptr.events.precommit),
            data_wrapper=SurfaceState,
        )
        self.commit_event = Signal(ptr=ffi.addressof(self._ptr.events.commit))
        self.map_event = Signal(ptr=ffi.addressof(self._ptr.events.map))
        self.unmap_event = Signal(ptr=ffi.addressof(self._ptr.events.unmap))
        self.new_subsurface_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_subsurface),
            data_wrapper=SubSurface,
        )
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

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

    @property
    def surface(self) -> Surface:
        """Get the wlr_surface underlying this subsurface"""
        return Surface(self._ptr.surface)
