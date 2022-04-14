# Copyright (c) 2022 Matt Colligan

from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from pywayland.server import Signal

from wlroots import ffi, lib, Ptr, PtrHasData, str_or_none
from wlroots.wlr_types.surface import Surface as WlrSurface

if TYPE_CHECKING:
    from typing import TypeVar

    from pywayland.server import Display

    from wlroots.wlr_types import Compositor, Seat
    from wlroots.wlr_types.xdg_shell import SurfaceCallback

    T = TypeVar("T")


class ServerOptions(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ptr

    @classmethod
    def new(
        cls, lazy: bool, enable_wm: bool, no_touch_pointer_emulation: bool
    ) -> ServerOptions:
        ptr = ffi.new("struct wlr_xwayland_server_options *")
        ptr.lazy = lazy
        ptr.enable_wm = enable_wm
        ptr.no_touch_pointer_emulation = no_touch_pointer_emulation
        return cls(ptr)

    @property
    def lazy(self) -> bool:
        return self._ptr.lazy

    @lazy.setter
    def lazy(self, lazy: bool) -> None:
        self._ptr.lazy = lazy

    @property
    def enable_wm(self) -> bool:
        return self._ptr.enable_wm

    @enable_wm.setter
    def enable_wm(self, enable_wm: bool) -> None:
        self._ptr.enable_wm = enable_wm

    @property
    def no_touch_pointer_emulation(self) -> bool:
        return self._ptr.no_touch_pointer_emulation

    @no_touch_pointer_emulation.setter
    def no_touch_pointer_emulation(self, no_touch_pointer_emulation: bool) -> None:
        self._ptr.no_touch_pointer_emulation = no_touch_pointer_emulation


class Server(PtrHasData):
    def __init__(self, display: Display, options: ServerOptions) -> None:
        ptr = lib.wlr_xwayland_server_create(display._ptr, options._ptr)
        if ptr == ffi.NULL:
            raise RuntimeError("Unable to create a wlr_xwayland_server.")

        self._ptr = ffi.gc(ptr, lib.wlr_xwayland_server_destroy)

        self.ready_event = Signal(ptr=ffi.addressof(self._ptr.events.ready))
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))


class XWayland(PtrHasData):
    def __init__(self, display: Display, compositor: Compositor, lazy: bool) -> None:
        ptr = lib.wlr_xwayland_create(display._ptr, compositor._ptr, lazy)

        if ptr == ffi.NULL:
            raise RuntimeError("Unable to create a wlr_xwayland.")

        self._ptr = ffi.gc(ptr, lib.wlr_xwayland_destroy)

        self.ready_event = Signal(ptr=ffi.addressof(self._ptr.events.ready))
        self.new_surface_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_surface),
            data_wrapper=Surface,
        )
        self.remove_startup_info_event = Signal(
            ptr=ffi.addressof(self._ptr.events.remove_startup_info)
        )

    @property
    def display_name(self) -> str | None:
        return str_or_none(self._ptr.display_name)

    def destroy(self) -> None:
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    def set_seat(self, seat: Seat) -> None:
        lib.wlr_xwayland_set_seat(self._ptr, seat._ptr)

    def set_cursor(
        self,
        pixels: list[int],
        stride: int,
        width: int,
        height: int,
        hotspot_x: int,
        hotspot_y: int,
    ) -> None:
        lib.wlr_xwayland_set_cursor(
            self._ptr, pixels, stride, width, height, hotspot_x, hotspot_y
        )

    def get_atom(self, name: str) -> int:
        """Helper method to fetch an atom by name."""
        conn = lib.xcb_connect(self._ptr.display_name, ffi.NULL)
        error = lib.xcb_connection_has_error(conn)
        if error:
            raise RuntimeError(f"xcb_connect failed with code {error}")

        name_bytes = name.encode()
        cookie = lib.xcb_intern_atom(conn, 0, len(name_bytes), name_bytes)
        atom = 0
        reply = lib.xcb_intern_atom_reply(conn, cookie, ffi.NULL)
        if reply:
            atom = reply.atom
        lib.xcb_disconnect(conn)
        return atom


class SurfaceDecorations(enum.IntEnum):
    ALL = lib.WLR_XWAYLAND_SURFACE_DECORATIONS_ALL
    NO_BORDER = lib.WLR_XWAYLAND_SURFACE_DECORATIONS_NO_BORDER
    NO_TITLE = lib.WLR_XWAYLAND_SURFACE_DECORATIONS_NO_TITLE


class ICCCMInputModel(enum.IntEnum):
    NONE = lib.WLR_ICCCM_INPUT_MODEL_NONE
    PASSIVE = lib.WLR_ICCCM_INPUT_MODEL_PASSIVE
    LOCAL = lib.WLR_ICCCM_INPUT_MODEL_LOCAL
    GLOBAL = lib.WLR_ICCCM_INPUT_MODEL_GLOBAL


class Surface(PtrHasData):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xwayland_surface *", ptr)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
        self.request_configure_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_configure),
            data_wrapper=SurfaceConfigureEvent,
        )
        self.request_move_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_move)
        )
        self.request_resize_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_resize)
        )
        self.request_minimize_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_minimize)
        )
        self.request_maximize_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_maximize)
        )
        self.request_fullscreen_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_fullscreen)
        )
        self.request_activate_event = Signal(
            ptr=ffi.addressof(self._ptr.events.request_activate)
        )
        self.map_event = Signal(ptr=ffi.addressof(self._ptr.events.map))
        self.unmap_event = Signal(ptr=ffi.addressof(self._ptr.events.unmap))
        self.set_title_event = Signal(ptr=ffi.addressof(self._ptr.events.set_title))
        self.set_class_event = Signal(ptr=ffi.addressof(self._ptr.events.set_class))
        self.set_role_event = Signal(ptr=ffi.addressof(self._ptr.events.set_role))
        self.set_parent_event = Signal(ptr=ffi.addressof(self._ptr.events.set_parent))
        self.set_pid_event = Signal(ptr=ffi.addressof(self._ptr.events.set_pid))
        self.set_startup_id_event = Signal(
            ptr=ffi.addressof(self._ptr.events.set_startup_id)
        )
        self.set_window_type_event = Signal(
            ptr=ffi.addressof(self._ptr.events.set_window_type)
        )
        self.set_hints_event = Signal(ptr=ffi.addressof(self._ptr.events.set_hints))
        self.set_decorations_event = Signal(
            ptr=ffi.addressof(self._ptr.events.set_decorations)
        )
        self.set_override_redirect_event = Signal(
            ptr=ffi.addressof(self._ptr.events.set_override_redirect)
        )
        self.set_geometry_event = Signal(
            ptr=ffi.addressof(self._ptr.events.set_geometry)
        )
        self.ping_timeout_event = Signal(
            ptr=ffi.addressof(self._ptr.events.ping_timeout)
        )

    def activate(self, activated: bool) -> None:
        lib.wlr_xwayland_surface_activate(self._ptr, activated)

    def restack(self, sibling: Surface | None, mode: int) -> None:
        if sibling:
            lib.wlr_xwayland_surface_restack(self._ptr, sibling._ptr, mode)
        else:
            lib.wlr_xwayland_surface_restack(self._ptr, ffi.NULL, mode)

    def configure(self, x: int, y: int, width: int, height: int) -> None:
        lib.wlr_xwayland_surface_configure(self._ptr, x, y, width, height)

    def close(self) -> None:
        lib.wlr_xwayland_surface_close(self._ptr)

    def set_minimized(self, minimized: bool) -> None:
        lib.wlr_xwayland_surface_set_minimized(self._ptr, minimized)

    def set_maximized(self, maximized: bool) -> None:
        lib.wlr_xwayland_surface_set_maximized(self._ptr, maximized)

    def set_fullscreen(self, fullscreen: bool) -> None:
        lib.wlr_xwayland_surface_set_fullscreen(self._ptr, fullscreen)

    @classmethod
    def from_wlr_surface(cls, surface: WlrSurface) -> Surface:
        return cls(lib.wlr_xwayland_surface_from_wlr_surface(surface._ptr))

    def ping(self) -> None:
        lib.wlr_xwayland_surface_ping(self._ptr)

    def or_surface_wants_focus(self) -> bool:
        return lib.wlr_xwayland_or_surface_wants_focus(self._ptr)

    def icccm_input_model(self) -> int:
        return lib.wlr_xwayland_icccm_input_model(self._ptr)

    @property
    def surface(self) -> WlrSurface:
        return WlrSurface(self._ptr.surface)

    @property
    def x(self) -> int:
        return self._ptr.x

    @property
    def y(self) -> int:
        return self._ptr.y

    @property
    def width(self) -> int:
        return self._ptr.width

    @property
    def height(self) -> int:
        return self._ptr.height

    @property
    def override_redirect(self) -> bool:
        return self._ptr.override_redirect

    @property
    def mapped(self) -> bool:
        return self._ptr.mapped

    @property
    def title(self) -> str | None:
        return str_or_none(self._ptr.title)

    @property
    def wm_class(self) -> str | None:
        # `self._ptr.class` is invalid syntax but this works.
        return str_or_none(getattr(self._ptr, "class"))

    @property
    def wm_instance(self) -> str | None:
        return str_or_none(self._ptr.wm_instance)

    @property
    def role(self) -> str | None:
        return str_or_none(self._ptr.role)

    @property
    def startup_id(self) -> str | None:
        return str_or_none(self._ptr.startup_id)

    @property
    def pid(self) -> int:
        return self._ptr.pid

    @property
    def parent(self) -> Surface | None:
        ptr = self._ptr.parent
        if ptr == ffi.NULL:
            return None
        return Surface(ptr)

    @property
    def window_type(self) -> list[int]:
        """This is an array of xcb_atom_t."""
        if self._ptr.window_type_len == 0:
            return []
        return ffi.unpack(self._ptr.window_type, self._ptr.window_type_len)

    @property
    def protocols(self) -> list[int]:
        """This is an array of xcb_atom_t."""
        return ffi.unpack(self._ptr.protocols, self._ptr.protocols_len)

    @property
    def hints_urgency(self) -> int:
        return self._ptr.hints_urgency

    @property
    def size_hints(self) -> SizeHints | None:
        ptr = self._ptr.size_hints
        if ptr == ffi.NULL:
            return None
        return SizeHints(ptr)

    @property
    def modal(self) -> bool:
        return self._ptr.modal

    @property
    def fullscreen(self) -> bool:
        return self._ptr.fullscreen

    @property
    def maximized_vert(self) -> bool:
        return self._ptr.maximized_vert

    @property
    def maximized_horz(self) -> bool:
        return self._ptr.maximized_horz

    @property
    def minimized(self) -> bool:
        return self._ptr.minimized

    @property
    def has_alpha(self) -> bool:
        return self._ptr.has_alpha

    def surface_at(
        self, surface_x: float, surface_y: float
    ) -> tuple[WlrSurface | None, float, float]:
        """A convenience method to match the method of WlrSurface and XdgSurface."""
        if (
            surface_x < 0
            or surface_y < 0
            or surface_x > self._ptr.width
            or surface_y > self._ptr.height
        ):
            return None, 0.0, 0.0
        return self.surface, surface_x, surface_y

    def for_each_surface(
        self, iterator: SurfaceCallback[T | None], data: T | None = None
    ) -> None:
        """
        A convenience method to match the method of XdgSurface and LayerSurfaceV1.

        The iterator is called using the only wlr_surface and it's local coordinates.
        """
        iterator(self.surface, 0, 0, data)


class SurfaceConfigureEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xwayland_surface_configure_event *", ptr)

    @property
    def surface(self) -> Surface:
        return Surface(self._ptr.surface)

    @property
    def x(self) -> int:
        return self._ptr.x

    @property
    def y(self) -> int:
        return self._ptr.y

    @property
    def width(self) -> int:
        return self._ptr.width

    @property
    def height(self) -> int:
        return self._ptr.height

    @property
    def mask(self) -> int:
        return self._ptr.mask


class ResizeEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xwayland_resize_event *", ptr)

    @property
    def surface(self) -> Surface:
        return Surface(self._ptr.surface)

    @property
    def edges(self) -> int:
        return self._ptr.edges


class MinimizeEvent(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xwayland_minimize_event *", ptr)

    @property
    def surface(self) -> Surface:
        return Surface(self._ptr.surface)

    @property
    def minimize(self) -> bool:
        return self._ptr.minimize


class SizeHints(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ffi.cast("struct wlr_xwayland_surface_size_hints *", ptr)

    @property
    def flags(self) -> int:
        return self._ptr.flags

    @property
    def x(self) -> int:
        return self._ptr.x

    @property
    def y(self) -> int:
        return self._ptr.y

    @property
    def width(self) -> int:
        return self._ptr.width

    @property
    def height(self) -> int:
        return self._ptr.height

    @property
    def min_width(self) -> int:
        return self._ptr.min_width

    @property
    def min_height(self) -> int:
        return self._ptr.min_height

    @property
    def max_width(self) -> int:
        return self._ptr.max_width

    @property
    def max_height(self) -> int:
        return self._ptr.max_height
