# Copyright (c) 2018 Sean Vig

from cffi import FFI

from pywayland.ffi_build import ffi_builder as pywayland_ffi


# backend.h
CDEF = """
struct wlr_backend_impl;

struct wl_signal {
    struct wl_list listener_list;
};

struct wlr_backend
{
    const struct wlr_backend_impl *impl;

    struct {
        struct wl_signal destroy;
        struct wl_signal new_input;
        struct wl_signal new_output;
    } events;
};

typedef int32_t EGLint;
typedef unsigned int EGLenum;

typedef struct wlr_renderer *(*wlr_renderer_create_func_t)(struct wlr_egl *egl, EGLenum platform,
    void *remote_display, EGLint *config_attribs, EGLint visual_id);

struct wlr_backend *wlr_backend_autocreate(struct wl_display *display,
    wlr_renderer_create_func_t create_renderer_func);

bool wlr_backend_start(struct wlr_backend *backend);
void wlr_backend_destroy(struct wlr_backend *backend);
struct wlr_renderer *wlr_backend_get_renderer(struct wlr_backend *backend);
"""

# render.h
CDEF += """
void wlr_renderer_begin(struct wlr_renderer *r, int width, int height);
void wlr_renderer_end(struct wlr_renderer *r);
void wlr_renderer_clear(struct wlr_renderer *r, const float color[static 4]);
// void wlr_renderer_clear(struct wlr_renderer *r, float (*color)[4]);

// bool wlr_render_with_matrix(
//     struct wlr_renderer *r, struct wlr_texture *texture, float (*matrix)[16], float alpha);
"""

# version.h
CDEF += """
#define WLR_VERSION_MAJOR ...
#define WLR_VERSION_MINOR ...
#define WLR_VERSION_MICRO ...
"""

SOURCE = """
#include <wlr/backend.h>
#include <wlr/render/wlr_renderer.h>
#include <wlr/version.h>

struct wl_listener_container {
    void *handle;
    struct wl_listener destroy_listener;
};
"""

ffi_builder = FFI()
ffi_builder.set_source(
    "wlroots._ffi",
    SOURCE,
    libraries=["wlroots"],
    define_macros=[("WLR_USE_UNSTABLE", None)],
    include_dirs=["/usr/include/pixman-1"],
)
ffi_builder.include(pywayland_ffi)
ffi_builder.cdef(CDEF)

if __name__ == "__main__":
    ffi_builder.compile()
