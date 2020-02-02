# Copyright (c) Sean Vig 2019

import enum
import weakref
from typing import Callable, TypeVar

from pywayland.server import Display, Signal

from wlroots import ffi, lib
from .surface import Surface

_weakkeydict: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()

T = TypeVar("T")
SurfaceCallback = Callable[[Surface, int, int, T], None]


@ffi.def_extern()
def surface_iterator_callback(surface_ptr, sx, sy, data_ptr):
    """Callback used to invoke the for_each_surface method"""
    func, py_data = ffi.from_handle(data_ptr)
    surface = Surface(surface_ptr)
    func(surface, sx, sy, py_data)


class XdgSurfaceRole(enum.IntEnum):
    NONE = lib.WLR_XDG_SURFACE_ROLE_NONE
    TOPLEVEL = lib.WLR_XDG_SURFACE_ROLE_TOPLEVEL
    POPUP = lib.WLR_XDG_SURFACE_ROLE_POPUP


class XdgShell:
    def __init__(self, display: Display) -> None:
        """Create the shell for protocol windows

        :param display:
            The Wayland server display to create the shell on.
        """
        self._ptr = lib.wlr_xdg_shell_create(display._ptr)

        self.new_surface_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_surface), data_wrapper=XdgSurface
        )
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))


class XdgSurface:
    def __init__(self, ptr) -> None:
        """A user interface element requiring management by the compositor

        An xdg-surface is a user interface element requiring management by the
        compositor. An xdg-surface alone isn't useful, a role should be
        assigned to it in order to map it.

        When a surface has a role and is ready to be displayed, the `map` event
        is emitted. When a surface should no longer be displayed, the `unmap`
        event is emitted. The `unmap` event is guaranteed to be emitted before
        the `destroy` event if the view is destroyed when mapped
        """
        self._ptr = ffi.cast("struct wlr_xdg_surface *", ptr)

        self.map_event = Signal(ptr=ffi.addressof(self._ptr.events.map))
        self.unmap_event = Signal(ptr=ffi.addressof(self._ptr.events.unmap))
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    @property
    def role(self) -> XdgSurfaceRole:
        """The role for the surface"""
        return XdgSurfaceRole(self._ptr.role)

    @property
    def toplevel(self) -> "XdgTopLevel":
        """Return the top level xdg object

        This shell must be a top level role
        """
        if self.role != XdgSurfaceRole.TOPLEVEL:
            raise ValueError(f"xdg surface must be top-level, got: {self.role}")

        toplevel = XdgTopLevel(self._ptr.toplevel)

        # the toplevel does not own the ptr data, ensure the underlying cdata
        # is kept alive
        _weakkeydict[toplevel] = self._ptr

        return toplevel

    def for_each_surface(self, iterator: SurfaceCallback[T], data: T = None) -> None:
        """Call iterator on each surface and popup in the xdg-surface tree

        Call `iterator` on each surface and popup in the xdg-surface tree, with
        the surface's position relative to the root xdg-surface. The function
        is called from root to leaves (in rendering order).

        :param iterator:
            The method that should be invoked
        :param data:
            The data that is passed as the last argument to the iterator method
        """
        py_handle = (iterator, data)
        handle = ffi.new_handle(py_handle)
        lib.wlr_xdg_surface_for_each_surface(
            self._ptr, lib.surface_iterator_callback, handle
        )


class XdgTopLevel:
    def __init__(self, ptr) -> None:
        """A top level surface object

        :param ptr:
            The wlr_xdg_toplevel cdata pointer
        """
        self._ptr = ptr

        self.request_maximize_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_maximize)
        )
        self.request_fullscreen_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_fullscreen)
        )
        self.request_minimize_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_minimize)
        )
        self.request_move_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_move)
        )
        self.request_resize_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_resize)
        )
        self.request_show_window_menu_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_show_window_menu)
        )
        self.set_parent_event = Signal(ptr=ffi.addressof(self._ptr.events.set_parent))
        self.set_title_event = Signal(ptr=ffi.addressof(self._ptr.events.set_title))
        self.set_app_id_event = Signal(ptr=ffi.addressof(self._ptr.events.set_app_id))
