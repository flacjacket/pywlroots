# Copyright (c) Sean Vig 2019

from __future__ import annotations

import enum
import weakref
from typing import Callable, TypeVar

from pywayland.server import Display, Signal

from wlroots import ffi, PtrHasData, lib, Ptr, str_or_none
from wlroots.util.box import Box
from wlroots.util.edges import Edges
from .output import Output
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


class XdgShell(PtrHasData):
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


class XdgSurface(PtrHasData):
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
        self.new_popup_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_popup), data_wrapper=XdgPopup
        )
        self.configure_event = Signal(
            ptr=ffi.addressof(self._ptr.events.configure),
            data_wrapper=XdgSurfaceConfigure,
        )
        self.ack_configure_event = Signal(
            ptr=ffi.addressof(self._ptr.events.ack_configure),
            data_wrapper=XdgSurfaceConfigure,
        )

    @classmethod
    def from_surface(cls, surface: Surface) -> XdgSurface:
        """Get the xdg surface associated with the given surface"""
        if not surface.is_xdg_surface:
            raise RuntimeError("Surface is not XDG surface")
        surface_ptr = lib.wlr_xdg_surface_from_wlr_surface(surface._ptr)
        return XdgSurface(surface_ptr)

    @property
    def surface(self) -> Surface:
        """The surface associated with the xdg surface"""
        return Surface(self._ptr.surface)

    @property
    def role(self) -> XdgSurfaceRole:
        """The role for the surface"""
        return XdgSurfaceRole(self._ptr.role)

    @property
    def toplevel(self) -> XdgTopLevel:
        """Return the top level xdg object

        This shell must be a top level role
        """
        if self.role != XdgSurfaceRole.TOPLEVEL:
            raise ValueError(f"xdg surface must be top-level, got: {self.role}")

        toplevel = XdgTopLevel(self._ptr.toplevel)

        # the toplevel does not own the ptr data, ensure the underlying cdata
        # is kept alive
        _weakkeydict[toplevel] = self

        return toplevel

    @property
    def popup(self) -> XdgPopup:
        """Return the popup xdg object

        This shell must be a popup role.
        """
        if self.role != XdgSurfaceRole.POPUP:
            raise ValueError(f"xdg surface must be popup, got: {self.role}")

        popup = XdgPopup(self._ptr.popup)
        _weakkeydict[popup] = self

        return popup

    def get_geometry(self) -> Box:
        """Get the surface geometry

        This is either the geometry as set by the client, or defaulted to the
        bounds of the surface + the subsurfaces (as specified by the protocol).

        The x and y value can be <0
        """
        box_ptr = ffi.new("struct wlr_box *")
        lib.wlr_xdg_surface_get_geometry(self._ptr, box_ptr)
        return Box(box_ptr.x, box_ptr.y, box_ptr.width, box_ptr.height)

    def set_size(self, width: int, height: int) -> int:
        return lib.wlr_xdg_toplevel_set_size(self._ptr, width, height)

    def set_activated(self, activated: bool) -> int:
        if self.role != XdgSurfaceRole.TOPLEVEL:
            raise ValueError(f"xdg surface must be top-level, got: {self.role}")

        return lib.wlr_xdg_toplevel_set_activated(self._ptr, activated)

    def set_tiled(self, tiled: int) -> int:
        return lib.wlr_xdg_toplevel_set_tiled(self._ptr, tiled)

    def set_fullscreen(self, fullscreened: bool) -> int:
        return lib.wlr_xdg_toplevel_set_fullscreen(self._ptr, fullscreened)

    def send_close(self) -> int:
        return lib.wlr_xdg_toplevel_send_close(self._ptr)

    def surface_at(
        self, surface_x: float, surface_y: float
    ) -> tuple[Surface | None, float, float]:
        """Find a surface within this xdg-surface tree at the given surface-local coordinates

        Returns the surface and coordinates in the leaf surface coordinate
        system or None if no surface is found at that location.
        """
        sub_x_data = ffi.new("double*")
        sub_y_data = ffi.new("double*")
        surface_ptr = lib.wlr_xdg_surface_surface_at(
            self._ptr, surface_x, surface_y, sub_x_data, sub_y_data
        )
        if surface_ptr == ffi.NULL:
            return None, 0.0, 0.0

        return Surface(surface_ptr), sub_x_data[0], sub_y_data[0]

    def for_each_surface(
        self, iterator: SurfaceCallback[T], data: T | None = None
    ) -> None:
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


class XdgSurfaceConfigure(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xdg_surface_configure *", ptr)

    @property
    def surface(self) -> XdgSurface:
        # TODO: keep weakref
        return XdgSurface(self._ptr.surface)

    @property
    def serial(self) -> int:
        return self._ptr.serial


class XdgTopLevel(Ptr):
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
            ptr=ffi.addressof(self._ptr.events.request_fullscreen),
            data_wrapper=XdgTopLevelSetFullscreenEvent,
        )
        self.request_minimize_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_minimize)
        )
        self.request_move_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_move),
            data_wrapper=XdgTopLevelMoveEvent,
        )
        self.request_resize_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_resize),
            data_wrapper=XdgTopLevelResizeEvent,
        )
        self.request_show_window_menu_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_show_window_menu),
            data_wrapper=XdgTopLevelShowWindowMenuEvent,
        )
        self.set_parent_event = Signal(ptr=ffi.addressof(self._ptr.events.set_parent))
        self.set_title_event = Signal(ptr=ffi.addressof(self._ptr.events.set_title))
        self.set_app_id_event = Signal(ptr=ffi.addressof(self._ptr.events.set_app_id))

    @property
    def parent(self) -> XdgSurface | None:
        """The surface of the parent of this toplevel"""
        parent_ptr = self._ptr.parent
        if parent_ptr is None:
            return None
        return XdgSurface(parent_ptr)

    @property
    def title(self) -> str | None:
        """The title of the toplevel object"""
        return str_or_none(self._ptr.title)

    @property
    def app_id(self) -> str | None:
        """The app id of the toplevel object"""
        return str_or_none(self._ptr.app_id)


class XdgTopLevelMoveEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xdg_toplevel_move_event *", ptr)

    @property
    def surface(self) -> Surface:
        # TODO: keep weakref
        return Surface(self._ptr.surface)

    # TODO: seat client

    @property
    def serial(self) -> int:
        return self._ptr.serial


class XdgTopLevelResizeEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xdg_toplevel_resize_event *", ptr)

    @property
    def surface(self) -> Surface:
        # TODO: keep weakref
        return Surface(self._ptr.surface)

    # TODO: seat client

    @property
    def serial(self) -> int:
        return self._ptr.serial

    @property
    def edges(self) -> Edges:
        return self._ptr.edges


class XdgTopLevelSetFullscreenEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xdg_toplevel_set_fullscreen_event *", ptr)

    @property
    def surface(self) -> Surface:
        # TODO: keep weakref
        return Surface(self._ptr.surface)

    @property
    def fullscreen(self) -> bool:
        return self._ptr.fullscreen

    @property
    def output(self) -> Output:
        return Output(self._ptr.output)


class XdgTopLevelShowWindowMenuEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xdg_toplevel_show_window_menu_event *", ptr)

    @property
    def surface(self) -> Surface:
        # TODO: keep weakref
        return Surface(self._ptr.surface)

    # TODO: seat client

    @property
    def serial(self) -> int:
        return self._ptr.serial

    @property
    def x(self) -> int:
        return self._ptr.x

    @property
    def y(self) -> int:
        return self._ptr.y


class XdgPopup(Ptr):
    def __init__(self, ptr) -> None:
        """A wlr_xdg_popup

        :param ptr:
            The wlr_xdg_popup cdata pointer
        """
        self._ptr = ffi.cast("struct wlr_xdg_popup *", ptr)

    @property
    def base(self) -> XdgSurface:
        """The xdg surface associated with the popup"""
        return XdgSurface(self._ptr.base)

    @property
    def parent(self) -> Surface:
        """Parent Surface."""
        parent = Surface(self.parent)
        _weakkeydict[parent] = self
        return parent

    def unconstrain_from_box(self, box: Box) -> None:
        """
        Set the geometry of this popup to unconstrain it according to its xdg-positioner
        rules. The box should be in the popup's root toplevel parent surface coordinate
        system.
        """
        lib.wlr_xdg_popup_unconstrain_from_box(self._ptr, box._ptr)
