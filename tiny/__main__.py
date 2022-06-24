"""An example basic compositor

To run this example, install the wlroots required dependencies, build the ffi
bindings (`python wlroots/ffi_build.py`), and launch the main (`python -m tiny`).
"""
from __future__ import annotations

import logging
import sys

from pywayland.server import Display
from wlroots.helper import build_compositor
from wlroots.util.log import log_init
from wlroots.wlr_types import (
    Cursor,
    DataDeviceManager,
    OutputLayout,
    Scene,
    Seat,
    XCursorManager,
    XdgShell,
)

from .server import TinywlServer


def main(argv) -> None:
    with Display() as display:
        compositor, allocator, renderer, backend = build_compositor(display)
        device_manager = DataDeviceManager(display)  # noqa: F841
        xdg_shell = XdgShell(display)
        with OutputLayout() as output_layout, Cursor(
            output_layout
        ) as cursor, XCursorManager(24) as xcursor_manager, Seat(
            display, "seat0"
        ) as seat:
            scene = Scene(output_layout)
            tinywl_server = TinywlServer(  # noqa: F841
                display=display,
                backend=backend,
                allocator=allocator,
                renderer=renderer,
                scene=scene,
                xdg_shell=xdg_shell,
                cursor=cursor,
                cursor_manager=xcursor_manager,
                seat=seat,
                output_layout=output_layout,
            )

            socket = display.add_socket()
            print("socket:", socket.decode())
            with backend:
                display.run()


if __name__ == "__main__":
    log_init(logging.DEBUG)
    logging.basicConfig(level=logging.INFO)

    main(sys.argv[1:])
