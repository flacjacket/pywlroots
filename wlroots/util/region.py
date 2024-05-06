# Copyright (c) Matt Colligan 2021

from __future__ import annotations

from pywayland.protocol.wayland import WlOutput

from wlroots import Ptr, ffi, lib
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

    def init(self) -> None:
        lib.pixman_region32_init(self._ptr)

    def init_rect(self, x: int, y: int, width: int, height: int) -> None:
        lib.pixman_region32_init_rect(self._ptr, x, y, width, height)

    def fini(self) -> None:
        lib.pixman_region32_fini(self._ptr)

    def __enter__(self) -> PixmanRegion32:
        """Use the pixman_region32 in a context manager"""
        self.init()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Finish up when exiting the context"""
        self.fini()

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

    @property
    def extents(self) -> Box:
        rect = lib.pixman_region32_extents(self._ptr)
        return Box(rect.x1, rect.y1, rect.x2 - rect.x1, rect.y2 - rect.y1)

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

    def intersect_rect(self, other: PixmanRegion32,
                       x: int, y: int, width: int, height: int) -> bool:
        """
        Wrapper around pixman_region32_intersect_rect
        """
        return lib.pixman_region32_intersect_rect(self._ptr, other._ptr, x, y, width, height)

    def union_rect(self, other: PixmanRegion32,
                   x: int, y: int, width: int, height: int) -> bool:
        """
        Wrapper around pixman_region32_union_rect
        """
        return lib.pixman_region32_union_rect(self._ptr, other._ptr, x, y, width, height)

    def intersect(self, reg1: PixmanRegion32, reg2: PixmanRegion32) -> bool:
        """
        Wrapper around pixman_region32_intersect
        """
        return lib.pixman_region32_intersect(self._ptr, reg1._ptr, reg2._ptr)

    def union(self, reg1: PixmanRegion32, reg2: PixmanRegion32) -> bool:
        """
        Wrapper around pixman_region32_union
        """
        return lib.pixman_region32_union(self._ptr, reg1._ptr, reg2._ptr)

    def subtract(self, reg1: PixmanRegion32, reg2: PixmanRegion32) -> bool:
        """
        Wrapper around pixman_region32_subtract
        """
        return lib.pixman_region32_subtract(self._ptr, reg1._ptr, reg2._ptr)

    def copy_from(self, other: PixmanRegion32) -> bool:
        """
        Wrapper around pixman_region32_copy
        """
        return lib.pixman_region32_copy(self._ptr, other._ptr)

    def translate(self, x: int, y: int) -> None:
        """
        Wrapper around pixman_region32_translate
        """
        lib.pixman_region32_translate(self._ptr, x, y)

    def scale(self, other: PixmanRegion32, scale: float) -> None:
        """
        Wrapper around wlr_region_scale
        """
        lib.wlr_region_scale(self._ptr, other._ptr, scale)

    def scale_xy(self, other: PixmanRegion32, scale_x: float, scale_y: float) -> None:
        """
        Wrapper around wlr_region_scale_xy
        """
        lib.wlr_region_scale_xy(self._ptr, other._ptr, scale_x, scale_y)

    def expand(self, other: PixmanRegion32, distance: int) -> None:
        """
        Wrapper around wlr_region_expand
        """
        lib.wlr_region_expand(self._ptr, other._ptr, distance)

    def clear(self) -> None:
        """
        Wrapper around pixman_region32_clear
        """
        lib.pixman_region32_clear(self._ptr)
