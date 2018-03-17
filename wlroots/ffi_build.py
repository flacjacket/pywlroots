# Copyright (c) 2018 Sean Vig

from cffi import FFI

CDEF = """
#define WLR_VERSION_MAJOR ...
#define WLR_VERSION_MICRO ...
#define WLR_VERSION_MINOR ...
"""

SOURCE = """
#include <wlr/version.h>
"""

ffi_builder = FFI()
ffi_builder.set_source(
    "wlroots._ffi",
    SOURCE,
    libraries=["wlroots"],
)
ffi_builder.cdef(CDEF)


if __name__ == "__main__":
    ffi_builder.compile()
