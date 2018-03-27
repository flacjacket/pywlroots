# Copyright (c) 2018 Sean Vig

from cffi import FFI

from pywayland.ffi_build import ffi_builder as pywayland_ffi

CDEF = ""

# backend.h
CDEF += """
struct wlr_backend_impl;

struct wlr_backend
{
    const struct wlr_backend_impl *impl;

    struct {
        struct wl_signal destroy;
        struct wl_signal new_input;
        struct wl_signal new_output;
    } events;
};

struct wlr_backend *wlr_backend_autocreate(struct wl_display *display);
bool wlr_backend_start(struct wlr_backend *backend);
void wlr_backend_destroy(struct wlr_backend *backend);
struct wlr_egl *wlr_backend_get_egl(struct wlr_backend *backend);
struct wlr_renderer *wlr_backend_get_renderer(struct wlr_backend *backend);
"""

# render.h
CDEF += """
void wlr_renderer_begin(struct wlr_renderer *r, struct wlr_output *output);
void wlr_renderer_end(struct wlr_renderer *r);
//void wlr_renderer_clear(struct wlr_renderer *r, const float (*color)[4]);
void wlr_renderer_clear(struct wlr_renderer *r, float (*color)[4]);

bool wlr_render_with_matrix(
    struct wlr_renderer *r, struct wlr_texture *texture, float (*matrix)[16], float alpha);
"""

# render/matrix.h
CDEF += """
void wlr_matrix_project_box(float (*mat)[16], struct wlr_box *box, enum wl_output_transform transform, float rotation, float (*projection)[16]);
"""

# types/wlr_box.h
CDEF += """
struct wlr_box {
    int x, y;
    int width, height;
};
"""

# types/wlr_compositor.h
CDEF += """
struct wlr_compositor *wlr_compositor_create(struct wl_display *display,struct wlr_renderer *renderer);
void wlr_compositor_destroy(struct wlr_compositor *wlr_compositor);
"""

# types/wlr_gamma_control.h
CDEF += """
struct wlr_gamma_control_manager *wlr_gamma_control_manager_create(struct wl_display *display);
void wlr_gamma_control_manager_destroy(struct wlr_gamma_control_manager *gamma_control_manager);
"""

# types/wlr_idle.h
CDEF += """
struct wlr_idle *wlr_idle_create(struct wl_display *display);
void wlr_idle_destroy(struct wlr_idle *idle);
"""

# types/wlr_primary_selection.h
CDEF += """
struct wlr_primary_selection_device_manager *wlr_primary_selection_device_manager_create(struct wl_display *display);
void wlr_primary_selection_device_manager_destroy(struct wlr_primary_selection_device_manager *manager);
"""

# types/wlr_screenshooter.h
CDEF += """
struct wlr_screenshooter *wlr_screenshooter_create(struct wl_display *display);
void wlr_screenshooter_destroy(struct wlr_screenshooter *screenshooter);
"""

# types/wlr_surface.h
CDEF += """
bool wlr_surface_has_buffer(struct wlr_surface *surface);

void wlr_surface_send_frame_done(struct wlr_surface *surface, const struct timespec *when);

struct wlr_surface *wlr_surface_from_resource(struct wl_resource *resource);
"""

# types/wlr_output.h
CDEF += """
typedef struct pixman_region32 pixman_region32_t;

void wlr_output_enable(struct wlr_output *output, bool enable);
void wlr_output_create_global(struct wlr_output *output);
void wlr_output_destroy_global(struct wlr_output *output);
bool wlr_output_set_mode(struct wlr_output *output, struct wlr_output_mode *mode);

bool wlr_output_make_current(struct wlr_output *output, int *buffer_age);

bool wlr_output_swap_buffers(struct wlr_output *output, struct timespec *when, pixman_region32_t *damage);
"""

# types/wlr_xdg_shell_v6.h
CDEF += """
struct wlr_xdg_shell_v6 *wlr_xdg_shell_v6_create(struct wl_display *display);
void wlr_xdg_shell_v6_destroy(struct wlr_xdg_shell_v6 *xdg_shell);
"""

# version.h
CDEF += """
#define WLR_VERSION_MAJOR ...
#define WLR_VERSION_MICRO ...
#define WLR_VERSION_MINOR ...
"""

SOURCE = """
#include <wlr/backend.h>
#include <wlr/render.h>
#include <wlr/render/matrix.h>
#include <wlr/types/wlr_box.h>
#include <wlr/types/wlr_compositor.h>
#include <wlr/types/wlr_gamma_control.h>
#include <wlr/types/wlr_idle.h>
#include <wlr/types/wlr_primary_selection.h>
#include <wlr/types/wlr_screenshooter.h>
#include <wlr/types/wlr_surface.h>
#include <wlr/types/wlr_output.h>
#include <wlr/types/wlr_xdg_shell_v6.h>
#include <wlr/version.h>
"""

ffi_builder = FFI()
ffi_builder.set_source(
    "wlroots._ffi",
    SOURCE,
    libraries=["wlroots"],
    include_dirs=["/usr/include/pixman-1"],
)
ffi_builder.include(pywayland_ffi)
ffi_builder.cdef(CDEF)

if __name__ == "__main__":
    ffi_builder.compile()
