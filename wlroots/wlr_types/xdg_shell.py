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


class XdgTopLevelWMCapabilities(enum.IntFlag):
    WINDOW_MENU = lib.WLR_XDG_TOPLEVEL_WM_CAPABILITIES_WINDOW_MENU
    MAXIMIZE = lib.WLR_XDG_TOPLEVEL_WM_CAPABILITIES_MAXIMIZE
    FULLSCREEN = lib.WLR_XDG_TOPLEVEL_WM_CAPABILITIES_FULLSCREEN
    MINIMIZE = lib.WLR_XDG_TOPLEVEL_WM_CAPABILITIES_MINIMIZE


class XdgShell(PtrHasData):
    def __init__(self, display: Display, version: int = 5) -> None:
        """Create the shell for protocol windows

        :param display:
            The Wayland server display to create the shell on.
        """
        self._ptr = lib.wlr_xdg_shell_create(display._ptr, version)

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
        return lib.wlr_xdg_toplevel_set_size(self._ptr.toplevel, width, height)

    def set_activated(self, activated: bool) -> int:
        if self.role != XdgSurfaceRole.TOPLEVEL:
            raise ValueError(f"xdg surface must be top-level, got: {self.role}")

        return lib.wlr_xdg_toplevel_set_activated(self._ptr.toplevel, activated)

    def set_maximized(self, maximized: bool) -> int:
        return lib.wlr_xdg_toplevel_set_maximized(self._ptr.toplevel, maximized)

    def set_fullscreen(self, fullscreen: bool) -> int:
        return lib.wlr_xdg_toplevel_set_fullscreen(self._ptr.toplevel, fullscreen)

    def set_resizing(self, resizing: bool) -> int:
        return lib.wlr_xdg_toplevel_set_resizing(self._ptr.toplevel, resizing)

    def set_tiled(self, tiled_edges: int) -> int:
        return lib.wlr_xdg_toplevel_set_tiled(self._ptr.toplevel, tiled_edges)

    def set_bounds(self, width: int, height: int) -> int:
        return lib.wlr_xdg_toplevel_set_bounds(self._ptr.toplevel, width, height)

    def set_wm_capabilities(self, caps: XdgTopLevelWMCapabilities) -> int:
        return lib.wlr_xdg_toplevel_set_wm_capabilities(self._ptr.toplevel, caps)

    def send_close(self) -> int:
        return lib.wlr_xdg_toplevel_send_close(self._ptr.toplevel)

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

    def schedule_configure(self) -> int:
        """
        Schedule a surface configuration. This should only be called by protocols
        extending the shell.
        """
        return lib.wlr_xdg_surface_schedule_configure(self._ptr)


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
    def parent(self) -> XdgTopLevel | None:
        """The parent of this toplevel"""
        parent_ptr = self._ptr.parent
        if parent_ptr is None:
            return None
        return XdgTopLevel(parent_ptr)

    @property
    def title(self) -> str | None:
        """The title of the toplevel object"""
        return str_or_none(self._ptr.title)

    @property
    def app_id(self) -> str | None:
        """The app id of the toplevel object"""
        return str_or_none(self._ptr.app_id)

    @property
    def requested(self) -> XdgTopLevelRequested:
        """Requested initial state"""
        return XdgTopLevelRequested(self._ptr.requested)


class XdgTopLevelMoveEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xdg_toplevel_move_event *", ptr)

    @property
    def toplevel(self) -> XdgTopLevel:
        # TODO: keep weakref
        return XdgTopLevel(self._ptr.toplevel)

    # TODO: seat client

    @property
    def serial(self) -> int:
        return self._ptr.serial


class XdgTopLevelResizeEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xdg_toplevel_resize_event *", ptr)

    @property
    def toplevel(self) -> XdgTopLevel:
        # TODO: keep weakref
        return XdgTopLevel(self._ptr.toplevel)

    # TODO: seat client

    @property
    def serial(self) -> int:
        return self._ptr.serial

    @property
    def edges(self) -> Edges:
        return self._ptr.edges


class XdgTopLevelShowWindowMenuEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xdg_toplevel_show_window_menu_event *", ptr)

    @property
    def toplevel(self) -> XdgTopLevel:
        # TODO: keep weakref
        return XdgTopLevel(self._ptr.toplevel)

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

        self.reposition_event = Signal(ptr=ffi.addressof(self._ptr.events.reposition))

    @property
    def base(self) -> XdgSurface:
        """The xdg surface associated with the popup"""
        return XdgSurface(self._ptr.base)

    @property
    def parent(self) -> Surface:
        """Parent Surface."""
        parent_ptr = self._ptr.parent
        _weakkeydict[parent_ptr] = self
        return Surface(parent_ptr)

    @property
    def current(self) -> XdgPopupState:
        return XdgPopupState(self._ptr.current)

    @property
    def pending(self) -> XdgPopupState:
        return XdgPopupState(self._ptr.pending)

    def unconstrain_from_box(self, box: Box) -> None:
        """
        Set the geometry of this popup to unconstrain it according to its xdg-positioner
        rules. The box should be in the popup's root toplevel parent surface coordinate
        system.
        """
        lib.wlr_xdg_popup_unconstrain_from_box(self._ptr, box._ptr)

    def destroy(self) -> None:
        """Request that this popup closes."""
        lib.wlr_xdg_popup_destroy(self._ptr)


class XdgPopupState(Ptr):
    def __init__(self, ptr) -> None:
        """A struct wlr_xdg_popup_state

        :param ptr:
            The wlr_xdg_popup_state cdata pointer
        """
        self._ptr = ffi.cast("struct wlr_xdg_popup_state *", ptr)

    @property
    def geometry(self) -> Box:
        """
        Position of the popup relative to the upper left corner of the window geometry
        of the parent surface.
        """
        return Box(self._ptr.geometry)

    @property
    def reactive(self) -> bool:
        return self._ptr.reactive


class XdgTopLevelRequested(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ptr

    @property
    def maximized(self) -> bool:
        return self._ptr.maximized

    @property
    def minimized(self) -> bool:
        return self._ptr.minimized

    @property
    def fullscreen(self) -> bool:
        return self._ptr.fullscreen

    @property
    def fullscreen_output(self) -> Output | None:
        output_ptr = self._ptr.fullscreen_output
        if output_ptr == ffi.NULL:
            return None
        return Output(output_ptr)
