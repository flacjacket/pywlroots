# Copyright (c) Sean Vig 2022

from __future__ import annotations

import enum
from typing import Callable, TYPE_CHECKING, TypeVar

from wlroots import Ptr, PtrHasData, ffi, lib
from wlroots.util.region import PixmanRegion32
from wlroots.wlr_types import Surface

if TYPE_CHECKING:
    from wlroots.util.box import Box
    from wlroots.util.clock import Timespec
    from wlroots.wlr_types import Buffer, Output, OutputLayout
    from wlroots.wlr_types.layer_shell_v1 import LayerSurfaceV1
    from wlroots.wlr_types.presentation_time import Presentation
    from wlroots.wlr_types.xdg_shell import XdgSurface


class SceneNodeType(enum.IntEnum):
    TREE = lib.WLR_SCENE_NODE_TREE
    RECT = lib.WLR_SCENE_NODE_RECT
    BUFFER = lib.WLR_SCENE_NODE_BUFFER


class Scene(Ptr):
    def __init__(self) -> None:
        """ "A root scene-graph node."""
        self._ptr = lib.wlr_scene_create()

    @property
    def tree(self) -> SceneTree:
        """The associated scene node."""
        ptr = ffi.addressof(self._ptr.tree)
        return SceneTree(ptr)

    def attach_output_layout(self, output_layout: OutputLayout) -> bool:
        """Get a scene-graph output from a wlr_output."""
        return lib.wlr_scene_attach_output_layout(self._ptr, output_layout._ptr)

    def set_presentation(self, presentation: Presentation) -> None:
        """
        Handle presentation feedback for all surfaces in the scene, assuming that scene
        outputs and the scene rendering functions are used.
        """
        lib.wlr_scene_set_presentation(self._ptr, presentation._ptr)

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

    @staticmethod
    def layer_surface_v1_create(
        parent: SceneTree, layer_surface: LayerSurfaceV1
    ) -> SceneLayerSurfaceV1:
        """
        Add a node displaying a layer_surface_v1 and all of its sub-surfaces to the
        scene-graph.

        The origin of the returned scene-graph node will match the top-left corner of
        the layer surface.
        """
        ptr = lib.wlr_scene_layer_surface_v1_create(parent._ptr, layer_surface._ptr)
        return SceneLayerSurfaceV1(ptr)


class SceneOutput(Ptr):
    def __init__(self, ptr) -> None:
        """A viewport for an output in the scene-graph"""
        self._ptr = ptr

    @classmethod
    def create(cls, scene: Scene, output: Output) -> SceneOutput:
        """
        Add a viewport for the specified output to the scene-graph.

        An output can only be added once to the scene-graph.
        """
        return cls(lib.wlr_scene_output_create(scene._ptr, output._ptr))

    def commit(self) -> None:
        """Render and commit an output."""
        if not lib.wlr_scene_output_commit(self._ptr):
            raise RuntimeError("Unable to commit scene output")

    def destroy(self) -> None:
        """Destroy a scene-graph output."""
        lib.wlr_scene_output_destroy(self._ptr)

    def send_frame_done(self, timespec: Timespec) -> None:
        """Send frame done on scene output.

        Call send_frame_done() on all surfaces in the scene rendered by
        commit() for which scene_surface.primary_output matches the given
        scene_output.
        """
        lib.wlr_scene_output_send_frame_done(self._ptr, timespec._ptr)

    def set_position(self, lx: int, ly: int) -> None:
        """Set the output's position in the scene-graph."""
        lib.wlr_scene_output_set_position(self._ptr, lx, ly)


class SceneTree(PtrHasData):
    def __init__(self, ptr) -> None:
        """struct wlr_scene_tree"""
        self._ptr = ptr

    @property
    def node(self) -> SceneNode:
        """struct wlr_scene_tree"""
        ptr = ffi.addressof(self._ptr.node)
        return SceneNode(ptr)

    @classmethod
    def create(cls, parent: SceneTree) -> SceneTree:
        return SceneTree(lib.wlr_scene_tree_create(parent._ptr))

    @classmethod
    def subsurface_tree_create(cls, parent: SceneTree, surface: Surface) -> SceneTree:
        return SceneTree(
            lib.wlr_scene_subsurface_tree_create(parent._ptr, surface._ptr)
        )


class SceneBuffer(Ptr):
    def __init__(self, ptr) -> None:
        """struct wlr_scene_buffer"""
        self._ptr = ptr

    @classmethod
    def from_node(cls, node: SceneNode) -> SceneBuffer | None:
        ptr = lib.wlr_scene_buffer_from_node(node._ptr)
        if ptr == ffi.NULL:
            return None
        return cls(ptr)

    @classmethod
    def create(cls, parent: SceneTree, buffer: Buffer) -> SceneBuffer | None:
        ptr = lib.wlr_scene_buffer_create(parent._ptr, buffer._ptr)
        if ptr == ffi.NULL:
            return None
        return cls(ptr)

    @property
    def node(self) -> SceneNode:
        ptr = ffi.addressof(self._ptr.node)
        return SceneNode(ptr)

    def set_buffer(self, buffer: Buffer | None) -> None:
        buffer_ptr = buffer._ptr if buffer else ffi.NULL
        lib.wlr_scene_buffer_set_buffer(self._ptr, buffer_ptr)

    def set_buffer_with_damage(
        self, buffer: Buffer | None, region: PixmanRegion32 | None = None
    ) -> None:
        buffer_ptr = buffer._ptr if buffer else ffi.NULL
        region_ptr = region._ptr if region else ffi.NULL
        lib.wlr_scene_buffer_set_buffer_with_damage(self._ptr, buffer_ptr, region_ptr)


T = TypeVar("T")
BufferCallback = Callable[[SceneBuffer, int, int, T], None]


@ffi.def_extern()
def buffer_iterator_callback(buffer_ptr, sx, sy, data_ptr):
    """Callback used to invoke the for_each_buffer method"""
    func, py_data = ffi.from_handle(data_ptr)
    buffer = SceneBuffer(buffer_ptr)
    func(buffer, sx, sy, py_data)


class SceneNode(PtrHasData):
    def __init__(self, ptr) -> None:
        """A node is an object in the scene."""
        self._ptr = ptr

    @property
    def type(self) -> SceneNodeType:
        return SceneNodeType(self._ptr.type)

    @property
    def parent(self) -> SceneTree | None:
        if self._ptr.parent == ffi.NULL:
            return None
        return SceneTree(self._ptr.parent)

    @property
    def x(self) -> int:
        return self._ptr.x

    @property
    def y(self) -> int:
        return self._ptr.y

    @property
    def enabled(self) -> bool:
        return self._ptr.enabled

    def destroy(self) -> None:
        """Immediately destroy the scene-graph node."""
        lib.wlr_scene_node_destroy(self._ptr)

    def set_enabled(self, *, enabled: bool = True) -> None:
        """
        Enable or disable this node. If a node is disabled, all of its children are
        implicitly disabled as well.
        """
        lib.wlr_scene_node_set_enabled(self._ptr, enabled)

    def set_position(self, x: int, y: int) -> None:
        """Set the position of the node relative to its parent."""
        lib.wlr_scene_node_set_position(self._ptr, x, y)

    def place_above(self, sibling: SceneNode) -> None:
        """Move the node right above the specified sibling."""
        lib.wlr_scene_node_place_above(self._ptr, sibling._ptr)

    def place_below(self, sibling: SceneNode) -> None:
        """Move the node right below the specified sibling."""
        lib.wlr_scene_node_place_below(self._ptr, sibling._ptr)

    def raise_to_top(self) -> None:
        """Move the node above all of its sibling nodes."""
        lib.wlr_scene_node_raise_to_top(self._ptr)

    def lower_to_bottom(self) -> None:
        """Move the node below all of its sibling nodes."""
        lib.wlr_scene_node_lower_to_bottom(self._ptr)

    def reparent(self, new_parent: SceneTree) -> None:
        """Move the node below all of its sibling nodes."""
        lib.wlr_scene_node_reparent(self._ptr, new_parent._ptr)

    def node_at(self, lx: float, ly: float) -> tuple[SceneNode, float, float] | None:
        """
        Find the topmost node in this scene-graph that contains the point at the given
        layout-local coordinates.

        (For surface nodes, this means accepting input events at that point.) Returns
        the node and coordinates relative to the returned node, or NULL if no node is
        found at that location.
        """
        nx = ffi.new("double*")
        ny = ffi.new("double*")
        node_ptr = lib.wlr_scene_node_at(self._ptr, lx, ly, nx, ny)
        if node_ptr == ffi.NULL:
            return None
        return SceneNode(node_ptr), nx[0], ny[0]

    def for_each_buffer(
        self, iterator: BufferCallback[T], data: T | None = None
    ) -> None:
        """
        Calls the iterator function for each sub-surface and popup of this surface
        """
        py_handle = (iterator, data)
        handle = ffi.new_handle(py_handle)
        lib.wlr_scene_node_for_each_buffer(
            self._ptr, lib.buffer_iterator_callback, handle
        )


class SceneSurface(Ptr):
    def __init__(self, ptr) -> None:
        """struct wlr_scene_surface"""
        self._ptr = ptr

    @classmethod
    def from_buffer(cls, buffer: SceneBuffer) -> SceneSurface | None:
        ptr = lib.wlr_scene_surface_from_buffer(buffer._ptr)
        if ptr == ffi.NULL:
            return None
        return cls(ptr)

    @property
    def surface(self) -> Surface:
        return Surface(self._ptr.surface)


class SceneRect(Ptr):
    def __init__(
        self, parent: SceneTree, width: int, height: int, color: ffi.CData
    ) -> None:
        """A scene-graph node displaying a solid-colored rectangle"""
        self._ptr = lib.wlr_scene_rect_create(parent._ptr, width, height, color)

    @property
    def node(self) -> SceneNode:
        """struct wlr_scene_tree"""
        ptr = ffi.addressof(self._ptr.node)
        return SceneNode(ptr)

    def set_size(self, width: int, height: int) -> None:
        """Change the width and height of an existing rectangle node."""
        lib.wlr_scene_rect_set_size(self._ptr, width, height)

    def set_color(self, color: ffi.CData) -> None:
        """Change the color of an existing rectangle node."""
        lib.wlr_scene_rect_set_color(self._ptr, color)


class SceneLayerSurfaceV1(Ptr):
    def __init__(self, ptr) -> None:
        self._ptr = ptr

    @property
    def tree(self) -> SceneTree:
        """struct wlr_scene_tree"""
        return SceneTree(self._ptr.tree)

    def configure(self, full_area: Box, usable_area: Box) -> None:
        """
        Configure a layer_surface_v1, position its scene node in accordance to its
        current state, and update the remaining usable area.

        full_area represents the entire area that may be used by the layer surface if
        its exclusive_zone is -1, and is usually the output dimensions. usable_area
        represents what remains of full_area that can be used if exclusive_zone is >= 0.
        usable_area is updated if the surface has a positive exclusive_zone, so that it
        can be used for the next layer surface.
        """
        lib.wlr_scene_layer_surface_v1_configure(
            self._ptr, full_area._ptr, usable_area._ptr
        )
