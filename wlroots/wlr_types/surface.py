# Copyright Sean Vig (c) 2020

from weakref import WeakKeyDictionary

from pywayland.protocol.wayland import WlOutput

from wlroots import ffi, lib
from .texture import Texture

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class Surface:
    def __init__(self, ptr):
        """Create a wlroots Surface

        :param ptr:
            The cdata for the given surface
        """
        self._ptr = ptr

    def get_texture(self):
        """Get the texture of the buffer currently attached to this surface

        Returns None if no buffer is currently attached or if something went
        wrong with uploading the buffer.
        """
        texture_ptr = lib.wlr_surface_get_texture(self._ptr)
        if texture_ptr == ffi.NULL:
            return None

        return Texture(texture_ptr)

    @property
    def current(self) -> "SurfaceState":
        """The current commited surface state"""
        current_ptr = self._ptr.current
        _weakkeydict[current_ptr] = self._ptr
        return SurfaceState(current_ptr)

    @property
    def previous(self) -> "SurfaceState":
        """The state of the previous commit"""
        previous_ptr = self._ptr.previous
        _weakkeydict[previous_ptr] = self._ptr
        return SurfaceState(previous_ptr)


class SurfaceState:
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
