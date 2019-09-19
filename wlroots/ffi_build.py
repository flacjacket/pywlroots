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

# types/wlr_cursor.h
CDEF += """
struct wlr_cursor *wlr_cursor_create(void);
void wlr_cursor_destroy(struct wlr_cursor *cur);

bool wlr_cursor_warp(struct wlr_cursor *cur, struct wlr_input_device *dev,
    double lx, double ly);
void wlr_cursor_warp_absolute(struct wlr_cursor *cur,
    struct wlr_input_device *dev, double x, double y);
void wlr_cursor_move(struct wlr_cursor *cur, struct wlr_input_device *dev,
    double delta_x, double delta_y);
void wlr_cursor_set_surface(struct wlr_cursor *cur, struct wlr_surface *surface,
    int32_t hotspot_x, int32_t hotspot_y);
void wlr_cursor_attach_input_device(struct wlr_cursor *cur,
    struct wlr_input_device *dev);
void wlr_cursor_attach_output_layout(struct wlr_cursor *cur,
    struct wlr_output_layout *l);
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

# types/wlr_keyboard.h
CDEF += """
void wlr_keyboard_set_keymap(struct wlr_keyboard *kb,
    struct xkb_keymap *keymap);
void wlr_keyboard_set_repeat_info(struct wlr_keyboard *kb, int32_t rate,
    int32_t delay);
uint32_t wlr_keyboard_get_modifiers(struct wlr_keyboard *keyboard);
"""

# types/wlr_linux_dmabuf_v1.h
CDEF += """
struct wlr_linux_dmabuf_v1 *wlr_linux_dmabuf_v1_create(struct wl_display *display,
    struct wlr_renderer *renderer);
void wlr_linux_dmabuf_v1_destroy(struct wlr_linux_dmabuf_v1 *linux_dmabuf);
"""

# types/wlr_matrix.h
CDEF += """
void wlr_matrix_project_box(float mat[static 9], const struct wlr_box *box,
    enum wl_output_transform transform, float rotation,
    const float projection[static 9]);
"""

# types/wlr_output.h
CDEF += """
bool wlr_output_enable(struct wlr_output *output, bool enable);

bool wlr_output_attach_render(struct wlr_output *output, int *buffer_age);
void wlr_output_effective_resolution(struct wlr_output *output,
    int *width, int *height);
bool wlr_output_commit(struct wlr_output *output);
bool wlr_output_set_mode(struct wlr_output *output,
    struct wlr_output_mode *mode);
enum wl_output_transform wlr_output_transform_invert(
    enum wl_output_transform tr);

void wlr_output_create_global(struct wlr_output *output);
void wlr_output_destroy_global(struct wlr_output *output);
"""

# types/wlr_output_layout.h
CDEF += """
struct wlr_output_layout *wlr_output_layout_create(void);
void wlr_output_layout_destroy(struct wlr_output_layout *layout);

void wlr_output_layout_output_coords(struct wlr_output_layout *layout,
    struct wlr_output *reference, double *lx, double *ly);

void wlr_output_layout_add_auto(struct wlr_output_layout *layout,
    struct wlr_output *output);
"""

# types/wlr_seat.h
CDEF += """
struct wlr_seat *wlr_seat_create(struct wl_display *display, const char *name);
void wlr_seat_destroy(struct wlr_seat *wlr_seat);

void wlr_seat_set_capabilities(struct wlr_seat *wlr_seat,
    uint32_t capabilities);

void wlr_seat_pointer_clear_focus(struct wlr_seat *wlr_seat);
void wlr_seat_pointer_notify_enter(struct wlr_seat *wlr_seat,
    struct wlr_surface *surface, double sx, double sy);
void wlr_seat_pointer_notify_motion(struct wlr_seat *wlr_seat,
    uint32_t time_msec, double sx, double sy);
uint32_t wlr_seat_pointer_notify_button(struct wlr_seat *wlr_seat,
    uint32_t time_msec, uint32_t button, enum wlr_button_state state);
void wlr_seat_pointer_notify_axis(struct wlr_seat *wlr_seat, uint32_t time_msec,
    enum wlr_axis_orientation orientation, double value,
    int32_t value_discrete, enum wlr_axis_source source);

void wlr_seat_set_keyboard(struct wlr_seat *seat, struct wlr_input_device *dev);
struct wlr_keyboard *wlr_seat_get_keyboard(struct wlr_seat *seat);

void wlr_seat_keyboard_notify_key(struct wlr_seat *seat, uint32_t time_msec,
    uint32_t key, uint32_t state);
void wlr_seat_keyboard_notify_modifiers(struct wlr_seat *seat,
    struct wlr_keyboard_modifiers *modifiers);
void wlr_seat_keyboard_notify_enter(struct wlr_seat *seat,
    struct wlr_surface *surface, uint32_t keycodes[], size_t num_keycodes,
    struct wlr_keyboard_modifiers *modifiers);
"""

# types/wlr_xcursor_manager.h
CDEF += """
struct wlr_xcursor_manager *wlr_xcursor_manager_create(const char *name,
    uint32_t size);
void wlr_xcursor_manager_destroy(struct wlr_xcursor_manager *manager);

int wlr_xcursor_manager_load(struct wlr_xcursor_manager *manager,
    float scale);
void wlr_xcursor_manager_set_cursor_image(struct wlr_xcursor_manager *manager,
    const char *name, struct wlr_cursor *cursor);
"""

# types/wlr_xdg_shell.h
CDEF += """
struct wlr_xdg_shell *wlr_xdg_shell_create(struct wl_display *display);
void wlr_xdg_shell_destroy(struct wlr_xdg_shell *xdg_shell);
"""

# util/log.h
CDEF += """
enum wlr_log_importance {
    WLR_SILENT,
    WLR_ERROR,
    WLR_INFO,
    WLR_DEBUG,
    ...
};

extern "Python" void log_func_callback(enum wlr_log_importance importance, const char *log_str);

typedef void (*wrapped_log_func_t)(enum wlr_log_importance importance, const char *log_str);

void wrapped_log_init(enum wlr_log_importance verbosity, wrapped_log_func_t callback);
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
#include <wlr/types/wlr_cursor.h>
#include <wlr/types/wlr_compositor.h>
#include <wlr/types/wlr_data_device.h>
#include <wlr/types/wlr_keyboard.h>
#include <wlr/types/wlr_linux_dmabuf_v1.h>
#include <wlr/types/wlr_matrix.h>
#include <wlr/types/wlr_output.h>
#include <wlr/types/wlr_output_layout.h>
#include <wlr/types/wlr_seat.h>
#include <wlr/types/wlr_xcursor_manager.h>
#include <wlr/types/wlr_xdg_shell.h>
#include <wlr/util/log.h>
#include <wlr/version.h>

struct wl_listener_container {
    void *handle;
    struct wl_listener destroy_listener;
};

typedef void (*wrapped_log_func_t)(enum wlr_log_importance importance, const char *log_str);

wrapped_log_func_t py_callback = NULL;

void wrapped_log_callback(enum wlr_log_importance importance, const char *fmt, va_list args)
{
    char formatted_str[4096];
    vsnprintf(formatted_str, 4096, fmt, args);
    py_callback(importance, formatted_str);
}

void wrapped_log_init(enum wlr_log_importance verbosity, wrapped_log_func_t callback)
{
    if (callback == NULL)
    {
        wlr_log_init(verbosity, NULL);
    }
    else
    {
        py_callback = callback;
        wlr_log_init(verbosity, wrapped_log_callback);
    }
}
"""

ffi_builder = FFI()
ffi_builder.set_source(
    "wlroots._ffi",
    SOURCE,
    libraries=["wlroots"],
    define_macros=[("WLR_USE_UNSTABLE", None)],
    include_dirs=["/usr/include/pixman-1", "include"],
)
ffi_builder.include(pywayland_ffi)
ffi_builder.cdef(CDEF)

if __name__ == "__main__":
    ffi_builder.compile()
