from pywayland.server import Display

from wlroots.backend import BackendType
from wlroots.helper import build_compositor


def test_build_compositor():
    with Display() as display:
        _, _, _, backend, _ = build_compositor(
            display, backend_type=BackendType.HEADLESS
        )
        backend.destroy()
