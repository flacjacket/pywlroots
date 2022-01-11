# Copyright (c) Matt Colligan 2021
#
# This protocol is obsolete and will be removed in a future version. The recommended
# replacement is xdg-decoration.

from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from wlroots import PtrHasData, lib

if TYPE_CHECKING:
    from pywayland.server import Display


class ServerDecorationManagerMode(enum.IntEnum):
    NONE = lib.WLR_SERVER_DECORATION_MANAGER_MODE_NONE
    CLIENT = lib.WLR_SERVER_DECORATION_MANAGER_MODE_CLIENT
    SERVER = lib.WLR_SERVER_DECORATION_MANAGER_MODE_SERVER


class ServerDecorationManager(PtrHasData):
    def __init__(self, ptr) -> None:
        """
        A decoration negotiation interface which implements the KDE protocol:
        wlr_server_decoration_manager.
        """
        self._ptr = ptr

    @classmethod
    def create(cls, display: Display) -> ServerDecorationManager:
        """Create a wlr_server_decoration_manager for the given display."""
        ptr = lib.wlr_server_decoration_manager_create(display._ptr)
        return cls(ptr)

    def set_default_mode(self, default_mode: ServerDecorationManagerMode) -> None:
        """Set the default decoration mode for this server"""
        lib.wlr_server_decoration_manager_set_default_mode(self._ptr, default_mode)
