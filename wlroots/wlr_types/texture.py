# Copyright (c) Sean Vig 2020


import typing

from wlroots import ffi, lib, Ptr

if typing.TYPE_CHECKING:
    from wlroots.renderer import Renderer


class Texture(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ptr

    @classmethod
    def from_pixels(
        cls,
        renderer: "Renderer",
        fmt: int,
        stride: int,
        width: int,
        height: int,
        data: ffi.CData,
    ) -> "Texture":
        """
        Create a new texture from raw pixel data. `stride` is in bytes. The returned
        texture is mutable.

        Should not be called in a rendering block like renderer_begin()/end() or
        between attaching a renderer to an output and committing it.
        """
        ptr = lib.wlr_texture_from_pixels(
            renderer._ptr, fmt, stride, width, height, data
        )
        return Texture(ptr)
