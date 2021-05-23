# Copyright (c) Sean Vig 2020
# Copyright (c) Matt Colligan 2021


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
        ptr = ffi.gc(ptr, lib.wlr_texture_destroy)
        return Texture(ptr)

    def write_pixels(
        self,
        stride: int,
        width: int,
        height: int,
        data: ffi.CData,
        src_x: int = 0,
        src_y: int = 0,
        dst_x: int = 0,
        dst_y: int = 0,
    ) -> bool:
        """
        Update a texture with raw pixels. The texture must be mutable, and the input
        data must have the same pixel format that the texture was created with.

        Should not be called in a rendering block like renderer_begin()/end() or
        between attaching a renderer to an output and committing it.

        data must be a CData pointer to pixel data.
        """
        return lib.wlr_texture_write_pixels(
            self._ptr,
            stride,
            width,
            height,
            src_x,
            src_y,
            dst_x,
            dst_y,
            data,
        )

    def destroy(self) -> None:
        """Destroys this wlr_texture."""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None
