from pywayland.server import Display

from wlroots.backend import BackendType
from wlroots.helper import build_compositor


def test_build_compositor():
    with Display() as display:
        build_compositor(display, backend_type=BackendType.HEADLESS)
