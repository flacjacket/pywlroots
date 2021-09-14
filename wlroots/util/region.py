# Copyright (c) Matt Colligan 2021

from __future__ import annotations

from pywayland.protocol.wayland import WlOutput
from wlroots import ffi, lib, Ptr
from wlroots.util.box import Box


class PixmanRegion32(Ptr):
    def __init__(self, ptr=None) -> None:
        """This is a convenience wrapper around pixman_region32_t

        :param ptr:
            The pixman_region32_t cdata pointer
        """
        if ptr is None:
            self._ptr = ffi.new("struct pixman_region32 *")
        else:
            self._ptr = ptr

    def __enter__(self) -> PixmanRegion32:
        """Use the pixman_region32 in a context manager"""
        lib.pixman_region32_init(self._ptr)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Finish up when exiting the context"""
        lib.pixman_region32_fini(self._ptr)

    def rectangles_as_boxes(self) -> list[Box]:
        nrects_ptr = ffi.new("int *")
        rects = lib.pixman_region32_rectangles(self._ptr, nrects_ptr)
        nrects = nrects_ptr[0]

        boxes = []
        for i in range(nrects):
            boxes.append(
                Box(rects.x1, rects.y1, rects.x2 - rects.x1, rects.y2 - rects.y1)
            )
            rects += 1
        return boxes

    def transform(
        self,
        src: PixmanRegion32,
        transform: WlOutput.transform,
        width: int,
        height: int,
    ) -> None:
        """
        Applies a transform to a region inside a box of size `width` x `height`.
        """
        lib.wlr_region_transform(self._ptr, src._ptr, transform, width, height)

    def not_empty(self) -> bool:
        """
        Wrapper around pixman_region32_not_empty
        """
        return lib.pixman_region32_not_empty(self._ptr)
