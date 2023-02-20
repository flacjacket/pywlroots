# Copyright Sean Vig (c) 2020
#
# The contents of this module has been moved to compositor.py for wlroots 0.16.0 and
# this file will be removed in the future.

import warnings

from wlroots.wlr_types.compositor import *  # noqa: F401,F403

warnings.warn(
    "wlroots.wlr_types.surface has moved to wlroots.wlr_types.compositor and will be removed in the future.",
    DeprecationWarning,
    stacklevel=1,
)
