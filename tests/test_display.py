from pywayland.server import Display

from wlroots.backend import Backend, BackendType


def test_run_headless_env_var(headless_backend):
    with Display() as display:
        with Backend(display):
            pass


def test_run_headless_arg(headless_backend):
    with Display() as display:
        with Backend(display, backend_type=BackendType.HEADLESS):
            pass
