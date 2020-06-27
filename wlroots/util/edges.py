# Copyright (c) Sean Vig 2020

import enum

from wlroots import lib


@enum.unique
class Edges(enum.IntFlag):
    NONE = lib.WLR_EDGE_NONE
    TOP = lib.WLR_EDGE_TOP
    BOTTOM = lib.WLR_EDGE_BOTTOM
    LEFT = lib.WLR_EDGE_LEFT
    RIGHT = lib.WLR_EDGE_RIGHT
