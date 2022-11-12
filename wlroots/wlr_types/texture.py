# Copyright (c) Sean Vig 2020
# Copyright (c) Matt Colligan 2021

from __future__ import annotations

import typing

from wlroots import Ptr, ffi, lib

if typing.TYPE_CHECKING:
    from wlroots.renderer import Renderer
    from wlroots.util.region import PixmanRegion32
    from wlroots.wlr_types.buffer import Buffer


class Texture(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ptr

    @classmethod
    def from_pixels(
        cls,
        renderer: Renderer,
        fmt: int,
        stride: int,
        width: int,
        height: int,
        data: ffi.CData,
    ) -> Texture:
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

    @classmethod
    def from_buffer(
        cls,
        renderer: Renderer,
        buffer: Buffer,
    ) -> Texture:
        """Create a new texture from a wlr_buffer."""
        ptr = lib.wlr_texture_from_buffer(renderer._ptr, buffer._ptr)
        ptr = ffi.gc(ptr, lib.wlr_texture_destroy)
        return Texture(ptr)

    def update_from_buffer(
        self,
        buffer: Buffer,
        damage: PixmanRegion32 | None = None,
    ) -> bool:
        """
        Update a texture with a struct wlr_buffer's contents.

        The damage can be used by the renderer as an optimization: only the supplied
        region needs to be updated.
        """
        if damage is None:
            damage_ptr = ffi.NULL
        else:
            damage_ptr = damage._ptr
        return lib.wlr_texture_update_from_buffer(self._ptr, buffer._ptr, damage_ptr)

    def destroy(self) -> None:
        """Destroys this wlr_texture."""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None
