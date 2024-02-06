from __future__ import annotations

import logging
import signal
from typing import TYPE_CHECKING, cast
from weakref import WeakKeyDictionary

from pywayland.protocol.wayland import WlKeyboard, WlSeat
from pywayland.server import Display, Listener
from xkbcommon import xkb

from wlroots import ffi, lib
from wlroots.allocator import Allocator
from wlroots.backend import Backend
from wlroots.renderer import Renderer
from wlroots.util.box import Box
from wlroots.util.clock import Timespec
from wlroots.util.edges import Edges
from wlroots.util.log import logger
from wlroots.wlr_types import (
    Cursor,
    Keyboard,
    Output,
    OutputLayout,
    OutputState,
    Scene,
    SceneBuffer,
    SceneNodeType,
    SceneOutput,
    SceneSurface,
    SceneTree,
    Seat,
    Surface,
    XCursorManager,
    XdgShell,
    idle_notify_v1,
)
from wlroots.wlr_types.cursor import WarpMode
from wlroots.wlr_types.input_device import ButtonState, InputDeviceType
from wlroots.wlr_types.keyboard import KeyboardModifier
from wlroots.wlr_types.pointer import (
    PointerButtonEvent,
    PointerMotionAbsoluteEvent,
    PointerMotionEvent,
)
from wlroots.wlr_types.seat import RequestSetSelectionEvent
from wlroots.wlr_types.xdg_shell import XdgSurface, XdgSurfaceRole

from .cursor_mode import CursorMode
from .keyboard_handler import KeyboardHandler
from .view import View

if TYPE_CHECKING:
    from wlroots.wlr_types import InputDevice
    from wlroots.wlr_types.keyboard import KeyboardKeyEvent, KeyboardModifiers
    from wlroots.wlr_types.output import OutputEventRequestState

_weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


def get_keysyms(xkb_state, keycode):
    syms_out = ffi.new("const xkb_keysym_t **")
    nsyms = lib.xkb_state_key_get_syms(xkb_state, keycode, syms_out)
    if nsyms > 0:
        assert syms_out[0] != ffi.NULL

    syms = [syms_out[0][i] for i in range(nsyms)]
    print(f"got {nsyms} syms: {syms}")
    return syms


class TinywlServer:
    def __init__(
        self,
        *,
        display: Display,
        backend: Backend,
        allocator: Allocator,
        renderer: Renderer,
        scene: Scene,
        xdg_shell: XdgShell,
        cursor: Cursor,
        cursor_manager: XCursorManager,
        seat: Seat,
        output_layout: OutputLayout,
    ) -> None:
        # elements that we need to hold on to
        self._display = display
        self._backend = backend
        self._allocator = allocator
        self._renderer = renderer
        self._scene = scene

        self._event_loop = self._display.get_event_loop()
        self._event_loop.add_signal(
            signal.SIGINT, self._terminate_signal_callback, self._display
        )

        # the xdg shell will generate new surfaces
        self._xdg_shell = xdg_shell
        self.views: list[View] = []

        # new pointing devices are attached to the cursor, and rendered with the manager
        self._cursor = cursor
        self._cursor_manager = cursor_manager

        # idle_notify_v1 support
        self.idle_notify = idle_notify_v1.IdleNotifierV1(self._display)

        # the seat manages the keyboard focus information
        self._seat = seat
        self.keyboards: list[KeyboardHandler] = []
        self.cursor_mode = CursorMode.PASSTHROUGH
        self.grabbed_view: View | None = None
        self.grab_x = 0.0
        self.grab_y = 0.0
        self.grab_geobox: Box | None = None
        self.resize_edges: Edges = Edges.NONE

        self._output_layout = output_layout
        self.outputs: list[Output] = []

        xdg_shell.new_surface_event.add(Listener(self.server_new_xdg_surface))

        backend.new_output_event.add(Listener(self.server_new_output))

        cursor.motion_event.add(Listener(self.server_cursor_motion))
        cursor.motion_absolute_event.add(Listener(self.server_cursor_motion_absolute))
        cursor.button_event.add(Listener(self.server_cursor_button))
        cursor.axis_event.add(Listener(self.server_cursor_axis))
        cursor.frame_event.add(Listener(self.server_cursor_frame))

        seat.request_set_cursor_event.add(Listener(self.seat_request_cursor))
        seat.request_set_selection_event.add(Listener(self.seat_request_set_selection))

        backend.new_input_event.add(Listener(self.server_new_input))

    def _terminate_signal_callback(self, sig_num: int, display: Display):
        logging.info("Terminating event loop.")
        display.terminate()

    def view_at(
        self, layout_x, layout_y
    ) -> tuple[View | None, Surface | None, float, float]:
        maybe_node = self._scene.tree.node.node_at(
            layout_x,
            layout_y,
        )
        if maybe_node is None or maybe_node[0].type != SceneNodeType.BUFFER:
            return None, None, 0, 0

        node, sx, sy = maybe_node
        scene_buffer = SceneBuffer.from_node(node)
        if scene_buffer is None:
            return None, None, 0, 0
        scene_surface = SceneSurface.from_buffer(scene_buffer)
        if scene_surface is None:
            return None, None, 0, 0

        surface = scene_surface.surface
        tree = cast(SceneTree, node.parent)
        # Find the node corresponding to the view at the root of this tree
        while tree.node.data is None:
            tree = cast(SceneTree, tree.node.parent)
        return tree.node.data, surface, sx, sy

    def _process_cursor_move(self) -> None:
        # Move the grabbed view to the new position
        assert self.grabbed_view is not None
        x = self.grabbed_view.x = self._cursor.x - self.grab_x
        y = self.grabbed_view.y = self._cursor.y - self.grab_y
        self.grabbed_view.scene_node.set_position(int(x), int(y))

    def _process_cursor_resize(self) -> None:
        assert self.grabbed_view is not None
        assert self.grab_geobox is not None

        new_left = self.grab_geobox.x
        new_right = self.grab_geobox.x + self.grab_geobox.width
        new_top = self.grab_geobox.y
        new_bottom = self.grab_geobox.y + self.grab_geobox.height

        border_x = int(self._cursor.x - self.grab_x)
        border_y = int(self._cursor.y - self.grab_y)

        if self.resize_edges & Edges.TOP:
            new_top = min(border_y, new_bottom - 1)
        elif self.resize_edges & Edges.BOTTOM:
            new_bottom = max(border_y, new_top + 1)

        if self.resize_edges & Edges.LEFT:
            new_left = min(border_x, new_right - 1)
        elif self.resize_edges & Edges.RIGHT:
            new_right = max(border_x, new_left + 1)

        geo_box = self.grabbed_view.xdg_surface.get_geometry()
        self.grabbed_view.x = new_left - geo_box.x
        self.grabbed_view.y = new_top - geo_box.y

        new_width = new_right - new_left
        new_height = new_bottom - new_top

        self.grabbed_view.xdg_surface.set_size(new_width, new_height)

    def process_cursor_motion(self, time) -> None:
        self.idle_notify.notify_activity(self._seat)
        if self.cursor_mode == CursorMode.MOVE:
            self._process_cursor_move()
            return
        elif self.cursor_mode == CursorMode.RESIZE:
            print("RESIZING")
            self._process_cursor_resize()
            return

        view, surface, sx, sy = self.view_at(self._cursor.x, self._cursor.y)
        logging.debug("Processing cursor motion: %s, %s", sx, sy)

        if view is None:
            self._cursor.set_xcursor(self._cursor_manager, "default")

        if surface is None:
            # Clear pointer focus so future button events and such are not sent
            # to the last client to have the cursor over it.
            self._seat.pointer_clear_focus()
        else:
            # Send pointer enter and motion events.
            self._seat.pointer_notify_enter(surface, sx, sy)
            self._seat.pointer_notify_motion(time, sx, sy)

    def send_modifiers(
        self, modifiers: KeyboardModifiers, input_device: InputDevice
    ) -> None:
        keyboard = Keyboard.from_input_device(input_device)
        self._seat.set_keyboard(keyboard)
        self._seat.keyboard_notify_modifiers(modifiers)

    def send_key(self, key_event: KeyboardKeyEvent, input_device: InputDevice) -> None:
        self.idle_notify.notify_activity(self._seat)
        keyboard = Keyboard.from_input_device(input_device)
        keyboard_modifier = keyboard.modifier

        handled = False
        # If alt is held down and this button was _pressed_, we attempt to
        # process it as a compositor keybinding
        if (
            keyboard_modifier == KeyboardModifier.ALT
            and key_event.state == WlKeyboard.key_state.pressed
        ):
            # translate libinput keycode -> xkbcommon
            keycode = key_event.keycode + 8
            keysyms = get_keysyms(keyboard._ptr.xkb_state, keycode)

            for keysym in keysyms:
                if self.handle_keybinding(keysym):
                    handled = True
                    break

        # Otherwise, we pass it along to the client
        if not handled:
            self._seat.set_keyboard(keyboard)
            self._seat.keyboard_notify_key(key_event)

    def handle_keybinding(self, keysym: int) -> bool:
        if keysym == xkb.keysym_from_name("Escape"):
            self._display.terminate()
        elif keysym == xkb.keysym_from_name("F1"):
            if len(self.views) >= 2:
                *rest, new_view, prev_view = self.views
                self.focus_view(new_view)
                self.views = [prev_view, *rest, new_view]

        else:
            return False
        return True

    def focus_view(self, view: View, surface: Surface | None = None) -> None:
        """Focus a given XDG surface

        Moves the surface to the front of the list for rendering.  Sets the
        surface to receive keyboard events.
        """
        logging.info("focus surface")
        if surface is None:
            surface = view.xdg_surface.surface

        previous_surface = self._seat.keyboard_state.focused_surface
        if previous_surface == surface:
            # Don't re-focus an already focused surface
            logging.info("Focus unchanged, exiting")
            return

        if previous_surface is not None:
            # Deactivate the previously focused surface
            logging.info("Un-focusing previous")
            if previous_xdg_surface := XdgSurface.try_from_surface(previous_surface):
                previous_xdg_surface.set_activated(False)

        view.scene_node.raise_to_top()
        # roll the given surface to the front of the list, copy and modify the
        # list, then save back to prevent any race conditions on list
        # modification
        views = self.views[:]
        views.remove(view)
        views.append(view)
        self.views = views
        # activate the new surface
        view.xdg_surface.set_activated(True)

        # Tell the seat to have the keyboard enter this surface. wlroots will
        # keep track of this and automatically send key events to the
        # appropriate clients without additional work on your part.
        keyboard = self._seat.keyboard
        if keyboard:
            self._seat.keyboard_notify_enter(view.xdg_surface.surface, keyboard)

    # #############################################################
    # surface handling callbacks

    def server_new_xdg_surface(self, listener, xdg_surface: XdgSurface) -> None:
        logger.info("new surface")

        if xdg_surface.role == XdgSurfaceRole.POPUP:
            # We must add xdg popups to the scene graph so they get rendered.
            # The wlroots scene graph provides a helper for this, but to use it
            # we must provide the proper parent scene node of the xdg popup. To
            # enable this, we always set the user data field of xdg_surfaces to
            # the corresponding scene node.
            if parent_xdg_surface := XdgSurface.try_from_surface(
                xdg_surface.popup.parent
            ):
                parent_scene_tree = cast(SceneTree, parent_xdg_surface.data)
                scene_tree = Scene.xdg_surface_create(parent_scene_tree, xdg_surface)
                xdg_surface.data = scene_tree
            return

        assert xdg_surface.role == XdgSurfaceRole.TOPLEVEL

        scene_tree = Scene.xdg_surface_create(self._scene.tree, xdg_surface)
        view = View(xdg_surface, self, scene_tree.node)
        self.views.append(view)

        # Keep the node alive for as long as the view, so that the view is accessible at
        # its data struct member.
        scene_node = scene_tree.node
        scene_node.data = view
        _weakkeydict[view] = scene_node

    # #############################################################
    # output and frame handling callbacks

    def server_new_output(self, listener, output: Output) -> None:
        SceneOutput.create(self._scene, output)
        output.init_render(self._allocator, self._renderer)

        state = OutputState()
        state.set_enabled()
        if mode := output.preferred_mode():
            state.set_mode(mode)

        output.commit_state(state)
        state.finish()

        self.outputs.append(output)
        if not self._output_layout.add_auto(output):
            logging.warning("Failed to add output to layout.")
            return

        output.frame_event.add(Listener(self.output_frame))
        output.request_state_event.add(Listener(self.output_request_state))

    def output_frame(self, listener, data) -> None:
        output = self.outputs[0]
        scene_output = self._scene.get_scene_output(output)
        scene_output.commit()

        now = Timespec.get_monotonic_time()
        scene_output.send_frame_done(now)

    def output_request_state(self, listener, request: OutputEventRequestState) -> None:
        output = self.outputs[0]
        output.commit_state(request.state)

    # #############################################################
    # input handling callbacks

    def server_new_input(self, listener, input_device: InputDevice) -> None:
        if input_device.type == InputDeviceType.POINTER:
            self._server_new_pointer(input_device)
        elif input_device.type == InputDeviceType.KEYBOARD:
            self._server_new_keyboard(input_device)

        capabilities = WlSeat.capability.pointer
        if len(self.keyboards) > 0:
            capabilities |= WlSeat.capability.keyboard

        logging.info("new input %s", input_device.type)
        logging.info("capabilities %s", capabilities)

        self._seat.set_capabilities(capabilities)

    def _server_new_pointer(self, input_device: InputDevice) -> None:
        self._cursor.attach_input_device(input_device)

    def _server_new_keyboard(self, input_device: InputDevice) -> None:
        keyboard = Keyboard.from_input_device(input_device)

        xkb_context = xkb.Context()
        keymap = xkb_context.keymap_new_from_names()

        keyboard.set_keymap(keymap)
        keyboard.set_repeat_info(25, 600)

        keyboard_handler = KeyboardHandler(keyboard, input_device, self)
        self.keyboards.append(keyboard_handler)

        self._seat.set_keyboard(keyboard)

    # #############################################################
    # cursor motion callbacks

    def server_cursor_motion(self, listener, event_motion: PointerMotionEvent) -> None:
        logging.debug("cursor motion")
        self._cursor.move(
            event_motion.delta_x,
            event_motion.delta_y,
            input_device=event_motion.pointer.base,
        )
        self.process_cursor_motion(event_motion.time_msec)

    def server_cursor_motion_absolute(
        self, listener, event_motion_absolute: PointerMotionAbsoluteEvent
    ) -> None:
        logging.debug("cursor abs motion")
        self._cursor.warp(
            WarpMode.AbsoluteClosest,
            event_motion_absolute.x,
            event_motion_absolute.y,
            input_device=event_motion_absolute.pointer.base,
        )
        self.process_cursor_motion(event_motion_absolute.time_msec)

    def server_cursor_button(self, listener, event: PointerButtonEvent) -> None:
        logging.info("Got button click event %s", event.button_state)
        self._seat.pointer_notify_button(
            event.time_msec, event.button, event.button_state
        )

        view, surface, _, _ = self.view_at(self._cursor.x, self._cursor.y)
        if event.button_state == ButtonState.RELEASED:
            # exit interactive move/resize
            self.cursor_mode = CursorMode.PASSTHROUGH
        elif view is not None:
            self.focus_view(view, surface)

    def server_cursor_axis(self, listener, event) -> None:
        self._seat.pointer_notify_axis(
            event.time_msec,
            event.orientation,
            event.delta,
            event.delta_discrete,
            event.source,
        )

    def server_cursor_frame(self, listener, data) -> None:
        self._seat.pointer_notify_frame()

    # #############################################################
    # seat callbacks

    def seat_request_cursor(self, listener, event):
        # This event is rasied by the seat when a client provides a cursor image
        # TODO: check that seat client is correct
        self._cursor.set_surface(event.surface, event.hotspot)

    def seat_request_set_selection(
        self, listener, event: RequestSetSelectionEvent
    ) -> None:
        print("request set selection")
        self._seat.set_selection(event._ptr.source, event.serial)
