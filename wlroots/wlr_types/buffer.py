# Copyright (c) Matt Colligan 2022

from __future__ import annotations

import enum

from wlroots import Ptr, ffi, lib


class BufferDataPtrAccessFlag(enum.IntFlag):
    READ = lib.WLR_BUFFER_DATA_PTR_ACCESS_READ
    WRITE = lib.WLR_BUFFER_DATA_PTR_ACCESS_WRITE


class Buffer(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ptr

    def drop(self) -> None:
        """Destroys this wlr_texture."""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    def begin_data_ptr_access(
        self, flags: BufferDataPtrAccessFlag
    ) -> tuple[ffi.CData, int, int]:
        """Access a pointer to the underlying data"""
        data = ffi.new('void**')
        format_ptr = ffi.new("uint32_t *")
        stride_ptr = ffi.new("size_t *")

        if not lib.wlr_buffer_begin_data_ptr_access(
            self._ptr, flags, data, format_ptr, stride_ptr
        ):
            raise RuntimeError("Failed to get buffer data")

        return data[0], format_ptr[0], stride_ptr[0]

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Finish accessing data pointer"""
        lib.wlr_buffer_end_data_ptr_access(self._ptr)
