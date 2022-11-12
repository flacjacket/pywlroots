# Copyright (c) Sean Vig 2022

from __future__ import annotations

from wlroots import ffi, lib, PtrHasData, Ptr
from wlroots.util.clock import Timespec
from wlroots.wlr_types import Output, OutputLayout
from wlroots.wlr_types.xdg_shell import XdgSurface


class Scene(Ptr):
    def __init__(self, output_layout: OutputLayout) -> None:
        """ "A root scene-graph node."""
        self._ptr = lib.wlr_scene_create()
        if not lib.wlr_scene_attach_output_layout(self._ptr, output_layout._ptr):
            raise RuntimeError("Unable to attach scene to output layout")

    @property
    def tree(self) -> SceneTree:
        """The associated scene node."""
        return SceneTree(ffi.addressof(self._ptr.tree))

    def get_scene_output(self, output: Output) -> SceneOutput:
        """Get a scene-graph output from a wlr_output."""
        ptr = lib.wlr_scene_get_scene_output(self._ptr, output._ptr)
        return SceneOutput(ptr)

    @staticmethod
    def xdg_surface_create(parent: SceneTree, xdg_surface: XdgSurface) -> SceneTree:
        """Add a node displaying an xdg_surface and all of its sub-surfaces to the scene-graph.

        The origin of the returned scene-graph node will match the top-left
        corner of the xdg_surface window geometry.
        """
        ptr = lib.wlr_scene_xdg_surface_create(parent._ptr, xdg_surface._ptr)
        return SceneTree(ptr)


class SceneOutput(Ptr):
    def __init__(self, ptr) -> None:
        """A viewport for an output in the scene-graph"""
        self._ptr = ptr

    def commit(self) -> None:
        """Render and commit an output."""
        if not lib.wlr_scene_output_commit(self._ptr):
            raise RuntimeError("Unable to commit scene output")

    def send_frame_done(self, timespec: Timespec) -> None:
        """Send frame done on scene output.

        Call send_frame_done() on all surfaces in the scene rendered by
        commit() for which scene_surface.primary_output matches the given
        scene_output.
        """
        lib.wlr_scene_output_send_frame_done(self._ptr, timespec._ptr)


class SceneTree(PtrHasData):
    def __init__(self, ptr) -> None:
        """struct wlr_scene_tree"""
        self._ptr = ptr

    @property
    def node(self) -> SceneNode:
        """struct wlr_scene_tree"""
        return SceneNode(ffi.addressof(self._ptr.node))


class SceneNode(PtrHasData):
    def __init__(self, ptr) -> None:
        """A node is an object in the scene."""
        self._ptr = ptr

    def set_position(self, x: int, y: int) -> None:
        """Set the output's position in the scene-graph."""
        lib.wlr_scene_node_set_position(self._ptr, x, y)

    def raise_to_top(self) -> None:
        """Move the node above all of its sibling nodes."""
        lib.wlr_scene_node_raise_to_top(self._ptr)

    def lower_to_bottom(self) -> None:
        """Move the node below all of its sibling nodes."""
        lib.wlr_scene_node_lower_to_bottom(self._ptr)

    def place_above(self, sibling: SceneNode) -> None:
        """Move the node right above the specified sibling."""
        lib.wlr_scene_node_place_above(self._ptr, sibling._ptr)

    def place_below(self, sibling: SceneNode) -> None:
        """Move the node right below the specified sibling."""
        lib.wlr_scene_node_place_below(self._ptr, sibling._ptr)
