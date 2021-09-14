from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pywayland.server import Listener

from wlroots.util.box import Box
from wlroots.util.edges import Edges
from .cursor_mode import CursorMode

if TYPE_CHECKING:
    from wlroots.wlr_types import SceneNode, Surface
    from wlroots.wlr_types.xdg_shell import XdgSurface
    from .server import TinywlServer


class View:
    def __init__(
        self,
        xdg_surface: XdgSurface,
        tinywl_server: TinywlServer,
        scene_node: SceneNode,
    ) -> None:
        self.xdg_surface = xdg_surface
        self.tinywl_server = tinywl_server
        self.scene_node = scene_node
        self.mapped = False
        self.x = 0.0
        self.y = 0.0

        xdg_surface.map_event.add(Listener(self.xdg_toplevel_map))
        xdg_surface.unmap_event.add(Listener(self.xdg_toplevel_unmap))
        xdg_surface.destroy_event.add(Listener(self.xdg_toplevel_destroy))

        toplevel = xdg_surface.toplevel
        toplevel.request_move_event.add(Listener(self.xdg_toplevel_request_move))
        toplevel.request_resize_event.add(Listener(self.xdg_toplevel_request_resize))

    def xdg_toplevel_map(self, listener, data) -> None:
        logging.info("mapped new view")
        self.mapped = True
        self.tinywl_server.focus_view(self)

    def xdg_toplevel_unmap(self, listener, data) -> None:
        logging.info("unmapped view")
        self.mapped = False

    def xdg_toplevel_destroy(self, listener, data) -> None:
        logging.info("destroyed view")
        self.tinywl_server.views.remove(self)

    def xdg_toplevel_request_move(self, listener, data) -> None:
        # This event is raised when a client would like to begin an interactive
        # move, typically because the user clicked on their client-side
        # decorations. Note that a more sophisticated compositor should check
        # the provied serial against a list of button press serials sent to
        # this client, to prevent the client from requesting this whenever they
        # want.
        logging.info("request move start")
        self._begin_interactive(CursorMode.MOVE, Edges.NONE)

    def xdg_toplevel_request_resize(self, listener, event) -> None:
        # This event is raised when a client would like to begin an interactive
        # resize, typically because the user clicked on their client-side
        # decorations. Note that a more sophisticated compositor should check
        # the provied serial against a list of button press serials sent to
        # this client, to prevent the client from requesting this whenever they
        # want.
        logging.info("request resize start")
        self._begin_interactive(CursorMode.RESIZE, event.edges)

    def _begin_interactive(self, cursor_mode: CursorMode, edges: Edges) -> None:
        """This function sets up an interactive move or resize operation"""
        focused_surface = self.tinywl_server._seat.pointer_state.focused_surface
        if self.xdg_surface.surface != focused_surface:
            # Deny move/resize requests from unfocused clients
            logging.info("Denied begin interactive")
            # TODO: this doesn't seem to be correct for alacritty, should return here

        self.tinywl_server.grabbed_view = self
        self.tinywl_server.cursor_mode = cursor_mode

        if cursor_mode == CursorMode.MOVE:
            self.tinywl_server.grab_x = self.tinywl_server._cursor.x - self.x
            self.tinywl_server.grab_y = self.tinywl_server._cursor.y - self.y
        elif cursor_mode == CursorMode.RESIZE:
            box = self.xdg_surface.get_geometry()

            border_x = self.x + box.x + (box.width if edges & Edges.RIGHT else 0)
            border_y = self.y + box.y + (box.height if edges & Edges.BOTTOM else 0)

            self.tinywl_server.grab_x = self.tinywl_server._cursor.x - border_x
            self.tinywl_server.grab_y = self.tinywl_server._cursor.y - border_y
            self.tinywl_server.grab_geobox = Box(
                box.x + int(self.x), box.y + int(self.y), box.width, box.height
            )
            self.tinywl_server.resize_edges = edges

    def view_at(
        self, layout_x: int, layout_y: int
    ) -> tuple[Surface | None, float, float]:
        view_x = layout_x - self.x
        view_y = layout_y - self.y
        return self.xdg_surface.surface_at(view_x, view_y)
