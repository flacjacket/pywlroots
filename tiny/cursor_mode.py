import enum


@enum.unique
class CursorMode(enum.Enum):
    """The behavior for cursor moves"""

    PASSTHROUGH = enum.auto()
    MOVE = enum.auto()
    RESIZE = enum.auto()
