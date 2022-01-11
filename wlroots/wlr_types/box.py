# Copyright Matt Colligan (c) 2021
#
# The contents of this module has been moved to ../util/box.py for wlroots 0.15.0 and
# this file will be removed in the future.

import warnings

from wlroots.util.box import *  # noqa: F401,F403

warnings.warn(
    "wlroots.types.box has moved to wlroots.util.box and will be removed in the future.",
    DeprecationWarning,
    stacklevel=1,
)
