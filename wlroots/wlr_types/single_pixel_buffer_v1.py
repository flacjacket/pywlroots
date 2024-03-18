from pywayland.server import Display

from wlroots import Ptr, lib


class SinglePixelBufferManagerV1(Ptr):
    """Global factory for single-pixel buffers.

    This protocol extension allows clients to create single-pixel buffers.

    Compositors supporting this protocol extension should also support the
    viewporter protocol extension (see wlr_types.viewporter.Viewporter).

    Clients may use viewporter to scale a single-pixel buffer to a desired size.
    """

    def __init__(self, display: Display) -> None:
        """Binds the manager to the provided display.

        :param display: The wayland display
        """
        self._ptr = lib.wlr_single_pixel_buffer_manager_v1_create(display._ptr)
