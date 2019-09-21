# Copyright (c) Sean Vig 2019


class Output:
    def __init__(self, ptr):
        """A compositor output region

        This typically corresponds to a monitor that displays part of the
        compositor space.

        The `frame` event will be emitted when it is a good time for the
        compositor to submit a new frame.

        To render a new frame, compositors should call
        `wlr_output_attach_render`, render and call `wlr_output_commit`. No
        rendering should happen outside a `frame` event handler or before
        `wlr_output_attach_render`.

        :param ptr:
            The wlr_output cdata pointer
        """
        self._ptr = ptr
