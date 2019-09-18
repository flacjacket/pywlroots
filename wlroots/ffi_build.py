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

typedef int EGLint;
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

void wlr_renderer_init_wl_display(struct wlr_renderer *r, struct wl_display *wl_display);
"""

# types/wlr_compositor.h
CDEF += """
void wlr_compositor_destroy(struct wlr_compositor *wlr_compositor);
struct wlr_compositor *wlr_compositor_create(struct wl_display *display,
    struct wlr_renderer *renderer);
"""

# types/wlr_data_device.h
CDEF += """
struct wlr_data_device_manager *wlr_data_device_manager_create(
    struct wl_display *display);
void wlr_data_device_manager_destroy(struct wlr_data_device_manager *manager);
"""

# types/wlr_linux_dmabuf_v1.h
CDEF += """
struct wlr_linux_dmabuf_v1 *wlr_linux_dmabuf_v1_create(struct wl_display *display,
    struct wlr_renderer *renderer);
void wlr_linux_dmabuf_v1_destroy(struct wlr_linux_dmabuf_v1 *linux_dmabuf);
"""

# types/wlr_output_layout
CDEF += """
struct wlr_output_layout *wlr_output_layout_create(void);
void wlr_output_layout_destroy(struct wlr_output_layout *layout);

void wlr_output_layout_output_coords(struct wlr_output_layout *layout,
    struct wlr_output *reference, double *lx, double *ly);

void wlr_output_layout_add_auto(struct wlr_output_layout *layout,
    struct wlr_output *output);
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
#include <wlr/types/wlr_compositor.h>
#include <wlr/types/wlr_data_device.h>
#include <wlr/types/wlr_linux_dmabuf_v1.h>
#include <wlr/types/wlr_output_layout.h>
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
