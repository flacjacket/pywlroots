# Copyright (c) 2019 Sean Vig

from .compositor import Compositor  # noqa: F401
from .cursor import Cursor  # noqa: F401
from .data_control_v1 import DataControlManagerV1  # noqa: F401
from .data_device_manager import DataDeviceManager  # noqa: F401
from .foreign_toplevel_management_v1 import ForeignToplevelManagerV1  # noqa: F401
from .gamma_control_v1 import GammaControlManagerV1  # noqa: F401
from .input_device import InputDevice  # noqa: F401
from .input_inhibit import InputInhibitManager  # noqa: F401
from .keyboard import Keyboard  # noqa: F401
from .layer_shell_v1 import LayerShellV1  # noqa: F401
from .matrix import Matrix  # noqa: F401
from .output import Output  # noqa: F401
from .output_damage import OutputDamage  # noqa: F401
from .output_layout import OutputLayout  # noqa: F401
from .pointer import (  # noqa: F401
    PointerEventAxis,
    PointerEventButton,
    PointerEventMotion,
    PointerEventMotionAbsolute,
)
from .pointer_constraints_v1 import (  # noqa: F401
    PointerConstraintsV1,
    PointerConstraintV1,
)
from .primary_selection_v1 import PrimarySelectionV1DeviceManager  # noqa: F401
from .relative_pointer_manager_v1 import RelativePointerManagerV1  # noqa: F401
from .scene import Scene, SceneNode  # noqa: F401
from .screencopy_v1 import ScreencopyManagerV1  # noqa: F401
from .seat import Seat  # noqa: F401
from .surface import Surface, SurfaceState  # noqa: F401
from .texture import Texture  # noqa: F401
from .virtual_keyboard_v1 import VirtualKeyboardManagerV1  # noqa: F401
from .xcursor_manager import XCursorManager  # noqa: F401
from .xdg_decoration_v1 import XdgDecorationManagerV1  # noqa: F401
from .xdg_output_v1 import XdgOutputManagerV1  # noqa: F401
from .xdg_shell import XdgShell  # noqa: F401


def __getattr__(name: str):
    if name == "Box":
        from .box import Box  # noqa: F401

        return Box
    try:
        return globals()[name]
    except KeyError:
        raise ImportError(f"cannot import name '{name}' from wlroots.wlr_types")
