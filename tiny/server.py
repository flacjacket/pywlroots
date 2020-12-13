from __future__ import annotations

import logging
from typing import List, Optional, Tuple, TYPE_CHECKING

from pywayland.server import Display, Listener
from pywayland.protocol.wayland import WlSeat
from xkbcommon import xkb

from wlroots import ffi, lib
from wlroots.backend import Backend
from wlroots.renderer import Renderer
from wlroots.util.edges import Edges
from wlroots.wlr_types import (
    Box,
    Cursor,
    Matrix,
    Output,
    OutputLayout,
    Seat,
    Surface,
    XCursorManager,
    XdgShell,
)
from wlroots.wlr_types.cursor import WarpMode
from wlroots.wlr_types.input_device import ButtonState, InputDeviceType
from wlroots.wlr_types.keyboard import KeyState, KeyboardModifier
from wlroots.wlr_types.pointer import (
    PointerEventButton,
    PointerEventMotion,
    PointerEventMotionAbsolute,
)
from wlroots.wlr_types.seat import RequestSetSelectionEvent
from wlroots.wlr_types.xdg_shell import XdgSurface, XdgSurfaceRole
from wlroots.util.log import logger
from wlroots.util.clock import Timespec

from .cursor_mode import CursorMode
from .keyboard_handler import KeyboardHandler
from .view import View

if TYPE_CHECKING:
    from wlroots.wlr_types import InputDevice
    from wlroots.wlr_types.keyboard import KeyboardKeyEvent, KeyboardModifiers


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
        renderer: Renderer,
        xdg_shell: XdgShell,
        cursor: Cursor,
        cursor_manager: XCursorManager,
        seat: Seat,
        output_layout: OutputLayout,
    ) -> None:
        # elements that we need to hold on to
        self._display = display
        self._backend = backend
        self._renderer = renderer

        # the xdg shell will generate new surfaces
        self._xdg_shell = xdg_shell
        self.views: List[View] = []

        # new pointing devices are attached to the cursor, and rendered with the manager
        self._cursor = cursor
        self._cursor_manager = cursor_manager

        # the seat manages the keyboard focus information
        self._seat = seat
        self.keyboards: List[KeyboardHandler] = []
        self.cursor_mode = CursorMode.PASSTHROUGH
        self.grabbed_view: Optional[View] = None
        self.grab_x = 0.0
        self.grab_y = 0.0
        self.grab_geobox: Optional[Box] = None
        self.resize_edges: Edges = Edges.NONE

        self._output_layout = output_layout
        self.outputs: List[Output] = []

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

    def view_at(
        self, layout_x, layout_y
    ) -> Tuple[Optional[View], Optional[Surface], float, float]:
        for view in self.views[::-1]:
            surface, x, y = view.view_at(layout_x, layout_y)
            if surface is not None:
                return view, surface, x, y
        return None, None, 0, 0

    def _process_cursor_move(self) -> None:
        # Move the grabbed view to the new position
        assert self.grabbed_view is not None
        self.grabbed_view.x = self._cursor.x - self.grab_x
        self.grabbed_view.y = self._cursor.y - self.grab_y

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
        if self.cursor_mode == CursorMode.MOVE:
            self._process_cursor_move()
        elif self.cursor_mode == CursorMode.RESIZE:
            print("RESIZING")
            self._process_cursor_resize()
        else:
            view, surface, sx, sy = self.view_at(self._cursor.x, self._cursor.y)
            logging.debug(f"Processing cursor motion: {sx} {sy}")

            if view is None or surface is None:
                self._cursor_manager.set_cursor_image("left_ptr", self._cursor)
                self._seat.pointer_clear_focus()
            else:
                focus_changed = self._seat.pointer_state.focused_surface != surface

                # "Enter" the surface if necessary. This lets the client know
                # that the cursor has entered one of its surfaces
                self._seat.pointer_notify_enter(surface, sx, sy)
                if not focus_changed:
                    # The enter event contains coordinates, so we only need to
                    # notify on motion if the focus did not change
                    self._seat.pointer_notify_motion(time, sx, sy)

    def send_modifiers(
        self, modifiers: KeyboardModifiers, input_device: InputDevice
    ) -> None:
        self._seat.set_keyboard(input_device)
        self._seat.keyboard_notify_modifiers(modifiers)

    def send_key(self, key_event: KeyboardKeyEvent, input_device: InputDevice) -> None:
        keyboard = input_device.keyboard
        keyboard_modifier = keyboard.modifier

        handled = False
        # If alt is held down and this button was _pressed_, we attempt to
        # process it as a compositor keybinding
        if (
            keyboard_modifier == KeyboardModifier.ALT
            and key_event.state == KeyState.KEY_PRESSED
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
            self._seat.set_keyboard(input_device)
            self._seat.keyboard_notify_key(key_event)

    def handle_keybinding(self, keysym: int) -> bool:
        if keysym == xkb.keysym_from_name("Escape"):
            self._display.terminate()
        elif keysym == xkb.keysym_from_name("F1"):
            if len(self.views) >= 2:
                *rest, new_view, prev_view = self.views
                self.focus_view(new_view)
                self.views = [prev_view] + rest + [new_view]

        else:
            return False
        return True

    def focus_view(self, view: View, surface: Optional[Surface] = None) -> None:
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
            previous_xdg_surface = XdgSurface.from_surface(previous_surface)
            previous_xdg_surface.set_activated(False)

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
        self._seat.keyboard_notify_enter(view.xdg_surface.surface, keyboard)

    # #############################################################
    # surface handling callbacks

    def server_new_xdg_surface(self, listener, xdg_surface: XdgSurface) -> None:
        logger.info("new surface")

        if xdg_surface.role != XdgSurfaceRole.TOPLEVEL:
            logger.info("Surface is not top level")
            return

        view = View(xdg_surface, self)
        self.views.append(view)

    # #############################################################
    # output and frame handling callbacks

    def server_new_output(self, listener, output: Output) -> None:
        if output.modes != []:
            mode = output.preferred_mode()
            if mode is None:
                logger.error("Got no output mode")
                return
            output.set_mode(mode)
            output.enable()

            if not output.commit():
                logger.error("Unable to commit output")
                return

        self.outputs.append(output)
        self._output_layout.add_auto(output)

        output.frame_event.add(Listener(self.output_frame))

    def output_frame(self, listener, data) -> None:
        now = Timespec.get_monotonic_time()

        output = self.outputs[0]
        if not output.attach_render():
            logger.error("could not attach renderer")
            return

        width, height = output.effective_resolution()

        self._renderer.begin(width, height)
        self._renderer.clear([0.3, 0.3, 0.3, 1.0])

        for view in self.views:
            if not view.mapped:
                continue

            data = output, view, now
            view.xdg_surface.for_each_surface(self._render_surface, data)

        output.render_software_cursors()

        self._renderer.end()
        output.commit()

    def _render_surface(
        self, surface: Surface, sx: int, sy: int, data: Tuple[Output, View, Timespec]
    ) -> None:
        output, view, now = data

        texture = surface.get_texture()
        if texture is None:
            return

        ox, oy = self._output_layout.output_coords(output)
        ox += view.x + sx
        oy += view.y + sy
        box = Box(
            int(ox * output.scale),
            int(oy * output.scale),
            int(surface.current.width * output.scale),
            int(surface.current.height * output.scale),
        )

        transform = surface.current.transform
        inverse = Output.transform_invert(transform)

        matrix = Matrix.project_box(box, inverse, 0, output.transform_matrix)

        self._renderer.render_texture_with_matrix(texture, matrix, 1)
        surface.send_frame_done(now)

    # #############################################################
    # input handling callbacks

    def server_new_input(self, listener, input_device: InputDevice) -> None:
        if input_device.device_type == InputDeviceType.POINTER:
            self._server_new_pointer(input_device)
        elif input_device.device_type == InputDeviceType.KEYBOARD:
            self._server_new_keyboard(input_device)

        capabilities = WlSeat.capability.pointer
        if len(self.keyboards) > 0:
            capabilities |= WlSeat.capability.keyboard

        logging.info(f"new input {str(input_device.device_type)}")
        logging.info(f"capabilities {str(capabilities)}")

        self._seat.set_capabilities(capabilities)

    def _server_new_pointer(self, input_device: InputDevice) -> None:
        self._cursor.attach_input_device(input_device)

    def _server_new_keyboard(self, input_device: InputDevice) -> None:
        keyboard = input_device.keyboard

        xkb_context = xkb.Context()
        keymap = xkb_context.keymap_new_from_names()

        keyboard.set_keymap(keymap)
        keyboard.set_repeat_info(25, 600)

        keyboard_handler = KeyboardHandler(keyboard, input_device, self)
        self.keyboards.append(keyboard_handler)

        self._seat.set_keyboard(input_device)

    # #############################################################
    # cursor motion callbacks

    def server_cursor_motion(self, listener, event_motion: PointerEventMotion) -> None:
        logging.debug("cursor motion")
        # self._cursor.move(event_motion_absolute.device
        self._cursor.move(
            event_motion.delta_x, event_motion.delta_y, input_device=event_motion.device
        )
        self.process_cursor_motion(event_motion.time_msec)

    def server_cursor_motion_absolute(
        self, listener, event_motion_absolute: PointerEventMotionAbsolute
    ) -> None:
        logging.debug("cursor abs motion")
        self._cursor.warp(
            WarpMode.AbsoluteClosest,
            event_motion_absolute.x,
            event_motion_absolute.y,
            input_device=event_motion_absolute.device,
        )
        self.process_cursor_motion(event_motion_absolute.time_msec)

    def server_cursor_button(self, listener, event: PointerEventButton) -> None:
        logging.info(f"Got button click event {event.button_state}")
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
