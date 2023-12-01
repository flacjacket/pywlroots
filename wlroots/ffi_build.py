# Copyright (c) 2018 Sean Vig
# Copyright (c) 2022 Aakash Sen Sharma

import importlib.util
import os
import sys
from pathlib import Path

from cffi import FFI, VerificationError
from pywayland.ffi_build import ffi_builder as pywayland_ffi
from xkbcommon.ffi_build import ffibuilder as xkb_ffi

include_dir = (Path(__file__).parent / "include").resolve()
assert include_dir.is_dir(), f"missing {include_dir}"


def load_version():
    """Load the current pywlroots version"""
    dirname = os.path.dirname(__file__)
    spec = importlib.util.spec_from_file_location(
        "wlroots.version", os.path.join(dirname, "version.py")
    )
    assert spec is not None
    assert spec.loader is not None
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)
    return version_module.version


def load_wlroots_version():
    """Load the current wlroots version

    Load the version from the in-line cffi module.
    """
    ffi = FFI()
    ffi.cdef(CDEF_VERSION)

    try:
        lib = ffi.verify("#include <wlr/version.h>")
    except (PermissionError, OSError):
        lib = importlib.import_module("wlroots").lib

    return f"{lib.WLR_VERSION_MAJOR}.{lib.WLR_VERSION_MINOR}.{lib.WLR_VERSION_MICRO}"  # type: ignore[attr-defined]


def check_version():
    """Check for wlroots version compatibility"""
    # When importing a system-level installed package, we may not be able to
    # create neighboring files, which is done by the `.verify` step.  If this
    # error is hit, we check with the compiled `wlroots.lib`.
    version = load_version()
    wlroots_version = load_wlroots_version()

    if version.split(".")[:2] != wlroots_version.split(".")[:2]:
        major, minor = list(map(int, version.split(".")[:2]))
        print(
            f"Installing wlroots v{version} requires wlroots v{major}.{minor}.x, found v{wlroots_version}",
            file=sys.stderr,
        )


def has_xwayland() -> bool:
    """
    Check for XWayland headers. If present, wlroots was built with XWayland support, so
    pywlroots can be too.
    """
    try:
        return importlib.import_module("wlroots._build").has_xwayland
    except ModuleNotFoundError:
        pass

    try:
        FFI().verify(
            "#include <wlr/xwayland.h>",
            define_macros=[("WLR_USE_UNSTABLE", 1)],
            include_dirs=["/usr/include/pixman-1", include_dir.as_posix()],
        )
        has_xwayland = True
    except VerificationError:
        print("If XWayland support is not required, ignore the above error message.")
        print(
            "If support is required, ensure wlroots was built with -Dxwayland=enabled."
        )
        has_xwayland = False

    with (Path(__file__).parent / "_build.py").open("w") as f:
        f.write(f"has_xwayland = {has_xwayland}\n")

    return has_xwayland


# typedef helpers
CDEF = """
typedef int32_t clockid_t;
"""

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
    ...;
};

struct wlr_backend *wlr_backend_autocreate(struct wl_display *display,
    struct wlr_session **session_ptr);

bool wlr_backend_start(struct wlr_backend *backend);
void wlr_backend_destroy(struct wlr_backend *backend);
"""

# backend/libinput.h
CDEF += """
struct libinput_device *wlr_libinput_get_device_handle(struct wlr_input_device *dev);
bool wlr_input_device_is_libinput(struct wlr_input_device *device);
"""

# backend/session.h
CDEF += """
bool wlr_session_change_vt(struct wlr_session *session, unsigned vt);
"""

# wlr/render/allocator.h
CDEF += """
struct wlr_allocator {
    ...;
};

struct wlr_allocator *wlr_allocator_autocreate(struct wlr_backend *backend,
    struct wlr_renderer *renderer);

struct wlr_buffer *wlr_allocator_create_buffer(struct wlr_allocator *alloc,
    int width, int height, const struct wlr_drm_format *format);
"""

# wlr/render/wlr_renderer.h
CDEF += """
struct wlr_renderer *wlr_renderer_autocreate(struct wlr_backend *backend);

bool wlr_renderer_begin(struct wlr_renderer *r, int width, int height);
void wlr_renderer_end(struct wlr_renderer *r);
void wlr_renderer_clear(struct wlr_renderer *r, const float color[static 4]);

void wlr_renderer_scissor(struct wlr_renderer *r, struct wlr_box *box);

bool wlr_render_texture(struct wlr_renderer *r, struct wlr_texture *texture,
    const float projection[static 9], int x, int y, float alpha);
bool wlr_render_texture_with_matrix(struct wlr_renderer *r,
    struct wlr_texture *texture, const float matrix[static 9], float alpha);

void wlr_render_rect(struct wlr_renderer *r, const struct wlr_box *box,
    const float color[static 4], const float projection[static 9]);

const uint32_t *wlr_renderer_get_shm_texture_formats(
    struct wlr_renderer *r, size_t *len);

bool wlr_renderer_init_wl_display(struct wlr_renderer *r, struct wl_display *wl_display);
void wlr_renderer_destroy(struct wlr_renderer *renderer);
"""

# wlr/render/drm_format_set.h
CDEF += """
struct wlr_drm_format_set {
    ...;
};
struct wlr_drm_format {
    ...;
};
const struct wlr_drm_format *wlr_drm_format_set_get(
    const struct wlr_drm_format_set *set, uint32_t format);
"""

# wlr/render/wlr_texture.h
CDEF += """
struct wlr_texture *wlr_texture_from_pixels(struct wlr_renderer *renderer,
    uint32_t fmt, uint32_t stride, uint32_t width, uint32_t height,
    const void *data);

bool wlr_texture_update_from_buffer(struct wlr_texture *texture,
    struct wlr_buffer *buffer, struct pixman_region32 *damage);

void wlr_texture_destroy(struct wlr_texture *texture);
struct wlr_texture *wlr_texture_from_buffer(struct wlr_renderer *renderer,
    struct wlr_buffer *buffer);
"""

# types/wlr_box.h
CDEF += """
struct wlr_box {
    int x, y;
    int width, height;
    ...;
};

struct wlr_fbox {
    double x, y;
    double width, height;
    ...;
};

void wlr_box_closest_point(const struct wlr_box *box, double x, double y,
    double *dest_x, double *dest_y);

bool wlr_box_intersection(struct wlr_box *dest, const struct wlr_box *box_a,
    const struct wlr_box *box_b);

bool wlr_box_contains_point(const struct wlr_box *box, double x, double y);

bool wlr_box_empty(const struct wlr_box *box);

void wlr_box_transform(struct wlr_box *dest, const struct wlr_box *box,
    enum wl_output_transform transform, int width, int height);
"""

# types/wlr_buffer.h
CDEF += """
struct wlr_buffer {
    ...;
};

void wlr_buffer_drop(struct wlr_buffer *buffer);

enum wlr_buffer_data_ptr_access_flag {
    WLR_BUFFER_DATA_PTR_ACCESS_READ = 1 << 0,
    WLR_BUFFER_DATA_PTR_ACCESS_WRITE = 1 << 1,
};

bool wlr_buffer_begin_data_ptr_access(struct wlr_buffer *buffer, uint32_t flags,
    void **data, uint32_t *format, size_t *stride);
void wlr_buffer_end_data_ptr_access(struct wlr_buffer *buffer);
struct wlr_buffer *wlr_buffer_lock(struct wlr_buffer *buffer);
void wlr_buffer_unlock(struct wlr_buffer *buffer);
"""

# types/wlr_cursor.h
CDEF += """
struct wlr_cursor {
    struct wlr_cursor_state *state;
    double x, y;

    struct {
        struct wl_signal motion;
        struct wl_signal motion_absolute;
        struct wl_signal button;
        struct wl_signal axis;
        struct wl_signal frame;
        struct wl_signal swipe_begin;
        struct wl_signal swipe_update;
        struct wl_signal swipe_end;
        struct wl_signal pinch_begin;
        struct wl_signal pinch_update;
        struct wl_signal pinch_end;
        struct wl_signal hold_begin;
        struct wl_signal hold_end;

        struct wl_signal touch_up;
        struct wl_signal touch_down;
        struct wl_signal touch_motion;
        struct wl_signal touch_cancel;
        struct wl_signal touch_frame;

        struct wl_signal tablet_tool_axis;
        struct wl_signal tablet_tool_proximity;
        struct wl_signal tablet_tool_tip;
        struct wl_signal tablet_tool_button;
    } events;

    void *data;
    ...;
};

struct wlr_cursor *wlr_cursor_create(void);
void wlr_cursor_destroy(struct wlr_cursor *cur);

bool wlr_cursor_warp(struct wlr_cursor *cur, struct wlr_input_device *dev,
    double lx, double ly);
void wlr_cursor_warp_closest(struct wlr_cursor *cur,
    struct wlr_input_device *dev, double x, double y);
void wlr_cursor_warp_absolute(struct wlr_cursor *cur,
    struct wlr_input_device *dev, double x, double y);
void wlr_cursor_absolute_to_layout_coords(struct wlr_cursor *cur,
    struct wlr_input_device *dev, double x, double y, double *lx, double *ly);
void wlr_cursor_move(struct wlr_cursor *cur, struct wlr_input_device *dev,
    double delta_x, double delta_y);
void wlr_cursor_set_surface(struct wlr_cursor *cur, struct wlr_surface *surface,
    int32_t hotspot_x, int32_t hotspot_y);
void wlr_cursor_attach_input_device(struct wlr_cursor *cur,
    struct wlr_input_device *dev);
void wlr_cursor_attach_output_layout(struct wlr_cursor *cur,
    struct wlr_output_layout *l);
void wlr_cursor_map_to_output(struct wlr_cursor *cur,
    struct wlr_output *output);
void wlr_cursor_map_input_to_output(struct wlr_cursor *cur,
    struct wlr_input_device *dev, struct wlr_output *output);
void wlr_cursor_set_xcursor(struct wlr_cursor *cur,
    struct wlr_xcursor_manager *manager, const char *name);
"""

# types/wlr_compositor.h
CDEF += """
struct wlr_compositor {
    struct wl_global *global;
    struct wlr_renderer *renderer;

    struct wl_listener display_destroy;

    struct {
        struct wl_signal new_surface;
        struct wl_signal destroy;
    } events;
    ...;
};

struct wlr_compositor *wlr_compositor_create(struct wl_display *display,
    uint32_t version, struct wlr_renderer *renderer);

struct wlr_surface_state {
    uint32_t committed;
    uint32_t seq;

    struct wlr_buffer *buffer;
    int32_t dx, dy;
    struct pixman_region32 surface_damage, buffer_damage;
    struct pixman_region32 opaque, input;
    enum wl_output_transform transform;
    int32_t scale;
    struct wl_list frame_callback_list;

    int width, height;
    int buffer_width, buffer_height;

    struct wl_list subsurfaces_below;
    struct wl_list subsurfaces_above;
    ...;
};

struct wlr_surface_role {
    const char *name;
    bool no_object;
    void (*commit)(struct wlr_surface *surface);
    void (*unmap)(struct wlr_surface *surface);
    void (*destroy)(struct wlr_surface *surface);
    ...;
};

struct wlr_surface_output {
    struct wlr_surface *surface;
    struct wlr_output *output;
    struct wl_list link;
    struct wl_listener bind;
    struct wl_listener destroy;
    ...;
};

struct wlr_surface {
    struct wl_resource *resource;
    struct wlr_renderer *renderer;
    struct wlr_client_buffer *buffer;
    struct pixman_region32 buffer_damage;
    struct pixman_region32 external_damage;
    struct pixman_region32 opaque_region;
    struct pixman_region32 input_region;
    struct wlr_surface_state current, pending;

    struct wl_list cached;
    bool mapped;

    const struct wlr_surface_role *role;
    struct wl_resource *role_resource;

    struct {
        struct wl_signal client_commit;
        struct wl_signal precommit;
        struct wl_signal commit;
        struct wl_signal map;
        struct wl_signal unmap;
        struct wl_signal new_subsurface;
        struct wl_signal destroy;
    } events;

    struct wl_list current_outputs;
    struct wlr_addon_set addons;
    void *data;
    ...;
};

typedef void (*wlr_surface_iterator_func_t)(struct wlr_surface *surface,
    int sx, int sy, void *data);

bool wlr_surface_set_role(struct wlr_surface *surface, const struct wlr_surface_role *role,
    struct wl_resource *error_resource, uint32_t error_code);

void wlr_surface_destroy_role_object(struct wlr_surface *surface);

bool wlr_surface_has_buffer(struct wlr_surface *surface);

struct wlr_texture *wlr_surface_get_texture(struct wlr_surface *surface);

struct wlr_surface *wlr_surface_get_root_surface(struct wlr_surface *surface);

bool wlr_surface_point_accepts_input(struct wlr_surface *surface,
    double sx, double sy);

struct wlr_surface *wlr_surface_surface_at(struct wlr_surface *surface,
    double sx, double sy, double *sub_x, double *sub_y);

void wlr_surface_send_enter(struct wlr_surface *surface,
    struct wlr_output *output);

void wlr_surface_send_leave(struct wlr_surface *surface,
    struct wlr_output *output);

void wlr_surface_send_frame_done(struct wlr_surface *surface,
    const struct timespec *when);

void wlr_surface_get_extends(struct wlr_surface *surface, struct wlr_box *box);

struct wlr_surface *wlr_surface_from_resource(struct wl_resource *resource);

void wlr_surface_for_each_surface(struct wlr_surface *surface,
    wlr_surface_iterator_func_t iterator, void *user_data);

void wlr_surface_get_effective_damage(struct wlr_surface *surface,
    struct pixman_region32 *damage);

void wlr_surface_get_buffer_source_box(struct wlr_surface *surface,
    struct wlr_fbox *box);

uint32_t wlr_surface_lock_pending(struct wlr_surface *surface);

void wlr_surface_unlock_cached(struct wlr_surface *surface, uint32_t seq);

extern "Python" void surface_iterator_callback(struct wlr_surface *surface, int sx, int sy, void *data);
"""

# types/wlr_subcompositor.h
CDEF += """
struct wlr_subsurface_parent_state {
    int32_t x, y;
    ...;
};

struct wlr_subsurface {
    struct wl_resource *resource;
    struct wlr_surface *surface;
    struct wlr_surface *parent;

    struct wlr_subsurface_parent_state current, pending;

    uint32_t cached_seq;
    bool has_cache;

    bool synchronized;
    bool reordered;
    bool added;

    struct wl_listener surface_client_commit;
    struct wl_listener parent_destroy;

    struct {
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_subcompositor {
    struct wl_global *global;
    ...;
};

struct wlr_subcompositor *wlr_subcompositor_create(struct wl_display *display);
"""

# types/wlr_damage_ring.h
CDEF += """
struct wlr_damage_ring {
    int32_t width, height;
    struct pixman_region32 current;
    ...;
};
"""

# types/wlr_data_control_v1.h
CDEF += """
struct wlr_data_control_manager_v1 {
    struct wl_global *global;
    struct wl_list devices; // wlr_data_control_device_v1::link

    struct {
        struct wl_signal destroy;
        struct wl_signal new_device; // wlr_data_control_device_v1
    } events;

    struct wl_listener display_destroy;
    ...;
};
struct wlr_data_control_manager_v1 *wlr_data_control_manager_v1_create(
    struct wl_display *display);
"""

# types/wlr_data_device.h
CDEF += """
struct wlr_data_device_manager *wlr_data_device_manager_create(
    struct wl_display *display);

void wlr_seat_set_selection(struct wlr_seat *seat,
    struct wlr_data_source *source, uint32_t serial);

void wlr_seat_start_pointer_drag(struct wlr_seat *seat, struct wlr_drag *drag,
    uint32_t serial);

struct wlr_drag_icon {
    struct wlr_drag *drag;
    struct wlr_surface *surface;
    struct {
        struct wl_signal destroy;
    } events;
    struct wl_listener surface_destroy;
    void *data;
    ...;
};

struct wlr_drag {
    enum wlr_drag_grab_type grab_type;
    struct wlr_seat_keyboard_grab keyboard_grab;
    struct wlr_seat_pointer_grab pointer_grab;
    struct wlr_seat_touch_grab touch_grab;
    struct wlr_seat *seat;
    struct wlr_seat_client *seat_client;
    struct wlr_seat_client *focus_client;
    struct wlr_drag_icon *icon; // can be NULL
    struct wlr_surface *focus; // can be NULL
    struct wlr_data_source *source; // can be NULL
    bool started, dropped, cancelling;
    int32_t grab_touch_id, touch_id; // if WLR_DRAG_GRAB_TOUCH
    struct {
        struct wl_signal focus;
        struct wl_signal motion; // wlr_drag_motion_event
        struct wl_signal drop; // wlr_drag_drop_event
        struct wl_signal destroy;
    } events;
    struct wl_listener source_destroy;
    struct wl_listener seat_client_destroy;
    struct wl_listener icon_destroy;
    void *data;
    ...;
};

struct wlr_drag_motion_event {
    struct wlr_drag *drag;
    uint32_t time;
    double sx, sy;
    ...;
};

struct wlr_drag_drop_event {
    struct wlr_drag *drag;
    uint32_t time;
    ...;
};

struct wlr_data_source {
    const struct wlr_data_source_impl *impl;
    struct wl_array mime_types;
    int32_t actions;
    bool accepted;
    enum wl_data_device_manager_dnd_action current_dnd_action;
    uint32_t compositor_action;
    struct {
        struct wl_signal destroy;
    } events;
    ...;
};

void wlr_data_source_destroy(struct wlr_data_source *source);
"""

# types/wlr_export_dmabuf_v1.h
CDEF += """
struct wlr_export_dmabuf_manager_v1 {
    struct wl_global *global;
    struct wl_list frames; // wlr_export_dmabuf_frame_v1::link

    struct wl_listener display_destroy;

    struct {
        struct wl_signal destroy;
    } events;
    ...;
};

struct wlr_export_dmabuf_frame_v1 {
    struct wl_resource *resource;
    struct wlr_export_dmabuf_manager_v1 *manager;
    struct wl_list link; // wlr_export_dmabuf_manager_v1::frames

    struct wlr_output *output;

    bool cursor_locked;

    struct wl_listener output_commit;
    ...;
};

struct wlr_export_dmabuf_manager_v1 *wlr_export_dmabuf_manager_v1_create(
    struct wl_display *display);
"""

# types/wlr_viewporter.h
CDEF += """
struct wlr_viewporter {
    struct wl_global *global;

    struct {
        struct wl_signal destroy;
    } events;

    struct wl_listener display_destroy;
    ...;
};

struct wlr_viewporter *wlr_viewporter_create(struct wl_display *display);
"""

# types/wlr_foreign_toplevel_management_v1.h
CDEF += """
struct wlr_foreign_toplevel_manager_v1 {
    struct wl_event_loop *event_loop;
    struct wl_global *global;
    struct wl_list resources; // wl_resource_get_link
    struct wl_list toplevels; // wlr_foreign_toplevel_handle_v1::link

    struct wl_listener display_destroy;

    struct {
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_foreign_toplevel_handle_v1 {
    struct wlr_foreign_toplevel_manager_v1 *manager;
    struct wl_list resources;
    struct wl_list link;
    struct wl_event_source *idle_source;

    char *title;
    char *app_id;
    struct wlr_foreign_toplevel_handle_v1 *parent;
    struct wl_list outputs; // wlr_foreign_toplevel_v1_output
    uint32_t state; // wlr_foreign_toplevel_v1_state

    struct {
        struct wl_signal request_maximize;
        struct wl_signal request_minimize;
        struct wl_signal request_activate;
        struct wl_signal request_fullscreen;
        struct wl_signal request_close;
        struct wl_signal set_rectangle;
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_foreign_toplevel_handle_v1_maximized_event {
    struct wlr_foreign_toplevel_handle_v1 *toplevel;
    bool maximized;
};
struct wlr_foreign_toplevel_handle_v1_minimized_event {
    struct wlr_foreign_toplevel_handle_v1 *toplevel;
    bool minimized;
};
struct wlr_foreign_toplevel_handle_v1_activated_event {
    struct wlr_foreign_toplevel_handle_v1 *toplevel;
    struct wlr_seat *seat;
};
struct wlr_foreign_toplevel_handle_v1_fullscreen_event {
    struct wlr_foreign_toplevel_handle_v1 *toplevel;
    bool fullscreen;
    struct wlr_output *output;
};
struct wlr_foreign_toplevel_handle_v1_set_rectangle_event {
    struct wlr_foreign_toplevel_handle_v1 *toplevel;
    struct wlr_surface *surface;
    int32_t x, y, width, height;
};

struct wlr_foreign_toplevel_manager_v1 *wlr_foreign_toplevel_manager_v1_create(
    struct wl_display *display);
struct wlr_foreign_toplevel_handle_v1 *wlr_foreign_toplevel_handle_v1_create(
    struct wlr_foreign_toplevel_manager_v1 *manager);
void wlr_foreign_toplevel_handle_v1_destroy(
    struct wlr_foreign_toplevel_handle_v1 *toplevel);
void wlr_foreign_toplevel_handle_v1_set_title(
    struct wlr_foreign_toplevel_handle_v1 *toplevel, const char *title);
void wlr_foreign_toplevel_handle_v1_set_app_id(
    struct wlr_foreign_toplevel_handle_v1 *toplevel, const char *app_id);
void wlr_foreign_toplevel_handle_v1_output_enter(
    struct wlr_foreign_toplevel_handle_v1 *toplevel, struct wlr_output *output);
void wlr_foreign_toplevel_handle_v1_output_leave(
    struct wlr_foreign_toplevel_handle_v1 *toplevel, struct wlr_output *output);
void wlr_foreign_toplevel_handle_v1_set_maximized(
    struct wlr_foreign_toplevel_handle_v1 *toplevel, bool maximized);
void wlr_foreign_toplevel_handle_v1_set_minimized(
    struct wlr_foreign_toplevel_handle_v1 *toplevel, bool minimized);
void wlr_foreign_toplevel_handle_v1_set_activated(
    struct wlr_foreign_toplevel_handle_v1 *toplevel, bool activated);
void wlr_foreign_toplevel_handle_v1_set_fullscreen(
    struct wlr_foreign_toplevel_handle_v1* toplevel, bool fullscreen);
void wlr_foreign_toplevel_handle_v1_set_parent(
    struct wlr_foreign_toplevel_handle_v1 *toplevel,
    struct wlr_foreign_toplevel_handle_v1 *parent);
"""

# types/wlr_gamma_control_v1.h
CDEF += """
struct wlr_gamma_control_manager_v1 {
    struct wl_global *global;
    struct wl_list controls; // wlr_gamma_control_v1::link

    struct wl_listener display_destroy;

    struct {
        struct wl_signal destroy;
        struct wl_signal set_gamma;
    } events;

    void *data;
    ...;
};
struct wlr_gamma_control_manager_v1 *wlr_gamma_control_manager_v1_create(
    struct wl_display *display);
"""

# types/wlr_idle.h
CDEF += """
struct wlr_idle {
    struct wl_global *global;
    struct wl_list idle_timers; // wlr_idle_timeout::link
    struct wl_event_loop *event_loop;
    bool enabled;

    struct wl_listener display_destroy;
    struct {
        struct wl_signal activity_notify;
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_idle_timeout {
    struct wl_resource *resource;
    struct wl_list link;
    struct wlr_seat *seat;

    struct wl_event_source *idle_source;
    bool idle_state;
    bool enabled;
    uint32_t timeout; // milliseconds

    struct {
        struct wl_signal idle;
        struct wl_signal resume;
        struct wl_signal destroy;
    } events;

    struct wl_listener input_listener;
    struct wl_listener seat_destroy;

    void *data;
    ...;
};

struct wlr_idle *wlr_idle_create(struct wl_display *display);

/**
 * Send notification to restart all timers for the given seat. Called by
 * compositor when there is an user activity event on that seat.
 */
void wlr_idle_notify_activity(struct wlr_idle *idle, struct wlr_seat *seat);

/**
 * Enable or disable timers for a given idle resource by seat.
 * Passing a NULL seat means update timers for all seats.
 */
void wlr_idle_set_enabled(struct wlr_idle *idle, struct wlr_seat *seat,
    bool enabled);

/**
 * Create a new timer on the given seat. The idle event will be called after
 * the given amount of milliseconds of inactivity, and the resumed event will
 * be sent at the first user activity after the fired event.
 */
struct wlr_idle_timeout *wlr_idle_timeout_create(struct wlr_idle *idle,
    struct wlr_seat *seat, uint32_t timeout);

void wlr_idle_timeout_destroy(struct wlr_idle_timeout *timeout);
"""

# types/wlr_input_inhibit_v1.h
CDEF += """
struct wlr_idle_inhibit_manager_v1 {
    struct wl_list inhibitors; // wlr_idle_inhibit_inhibitor_v1::link
    struct wl_global *global;

    struct wl_listener display_destroy;

    struct {
        struct wl_signal new_inhibitor;
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_idle_inhibitor_v1 {
    struct wlr_surface *surface;
    struct wl_resource *resource;
    struct wl_listener surface_destroy;

    struct wl_list link; // wlr_idle_inhibit_manager_v1::inhibitors;

    struct {
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_idle_inhibit_manager_v1 *wlr_idle_inhibit_v1_create(struct wl_display *display);
"""

# types/wlr_idle_notify_v1.h
CDEF += """
struct wlr_idle_notifier_v1;

struct wlr_idle_notifier_v1 *wlr_idle_notifier_v1_create(struct wl_display *display);

void wlr_idle_notifier_v1_set_inhibited(struct wlr_idle_notifier_v1 *notifier,
    bool inhibited);

void wlr_idle_notifier_v1_notify_activity(struct wlr_idle_notifier_v1 *notifier,
    struct wlr_seat *seat);
"""

# types/wlr_input_device.h
CDEF += """
enum wlr_button_state {
    WLR_BUTTON_RELEASED,
    WLR_BUTTON_PRESSED,
    ...
};

enum wlr_input_device_type {
    WLR_INPUT_DEVICE_KEYBOARD,
    WLR_INPUT_DEVICE_POINTER,
    WLR_INPUT_DEVICE_TOUCH,
    WLR_INPUT_DEVICE_TABLET_TOOL,
    WLR_INPUT_DEVICE_TABLET_PAD,
    WLR_INPUT_DEVICE_SWITCH,
    ...
};

struct wlr_input_device {
    enum wlr_input_device_type type;
    unsigned int vendor, product;
    char *name;

    struct {
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};
"""

# types/wlr_input_inhibitor.h
CDEF += """
struct wlr_input_inhibit_manager {
    struct wl_global *global;
    struct wl_client *active_client;
    struct wl_resource *active_inhibitor;

    struct wl_listener display_destroy;

    struct {
        struct wl_signal activate;   // struct wlr_input_inhibit_manager *
        struct wl_signal deactivate; // struct wlr_input_inhibit_manager *
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_input_inhibit_manager *wlr_input_inhibit_manager_create(
    struct wl_display *display);
"""

# types/wlr_keyboard.h
CDEF += """
#define WLR_LED_COUNT 3
#define WLR_MODIFIER_COUNT 8
#define WLR_KEYBOARD_KEYS_CAP 32

enum wlr_keyboard_led {
    WLR_LED_NUM_LOCK = ...,
    WLR_LED_CAPS_LOCK = ...,
    WLR_LED_SCROLL_LOCK = ...,
    ...
};

enum wlr_keyboard_modifier {
    WLR_MODIFIER_SHIFT = ...,
    WLR_MODIFIER_CAPS = ...,
    WLR_MODIFIER_CTRL = ...,
    WLR_MODIFIER_ALT = ...,
    WLR_MODIFIER_MOD2 = ...,
    WLR_MODIFIER_MOD3 = ...,
    WLR_MODIFIER_LOGO = ...,
    WLR_MODIFIER_MOD5 = ...,
    ...
};

struct wlr_keyboard_modifiers {
    xkb_mod_mask_t depressed;
    xkb_mod_mask_t latched;
    xkb_mod_mask_t locked;
    xkb_mod_mask_t group;
    ...;
};

struct wlr_keyboard {
    struct wlr_input_device base;

    const struct wlr_keyboard_impl *impl;
    struct wlr_keyboard_group *group;

    char *keymap_string;
    size_t keymap_size;
    int keymap_fd;
    struct xkb_keymap *keymap;
    struct xkb_state *xkb_state;
    xkb_led_index_t led_indexes[WLR_LED_COUNT];
    xkb_mod_index_t mod_indexes[WLR_MODIFIER_COUNT];

    uint32_t leds;
    uint32_t keycodes[WLR_KEYBOARD_KEYS_CAP];
    size_t num_keycodes;
    struct wlr_keyboard_modifiers modifiers;

    struct {
        int32_t rate;
        int32_t delay;
    } repeat_info;

    struct {
        struct wl_signal key;
        struct wl_signal modifiers;
        struct wl_signal keymap;
        struct wl_signal repeat_info;
    } events;

    void *data;
    ...;
};

struct wlr_keyboard_key_event {
    uint32_t time_msec;
    uint32_t keycode;
    bool update_state;
    enum wl_keyboard_key_state state;
    ...;
};

void wlr_keyboard_set_keymap(struct wlr_keyboard *kb,
    struct xkb_keymap *keymap);
void wlr_keyboard_set_repeat_info(struct wlr_keyboard *kb, int32_t rate,
    int32_t delay);
uint32_t wlr_keyboard_get_modifiers(struct wlr_keyboard *keyboard);
struct wlr_keyboard *wlr_keyboard_from_input_device(
    struct wlr_input_device *input_device);
"""

# wlr/interfaces/wlr_keyboard.h
CDEF += """
void wlr_keyboard_notify_modifiers(struct wlr_keyboard *keyboard,
    uint32_t mods_depressed, uint32_t mods_latched, uint32_t mods_locked,
    uint32_t group);
"""

# types/wlr_linux_dmabuf_v1.h
CDEF += """
struct wlr_linux_dmabuf_v1 *wlr_linux_dmabuf_v1_create(struct wl_display *display,
    uint32_t version, const struct wlr_linux_dmabuf_feedback_v1 *default_feedback);
"""

# types/wlr_matrix.h
CDEF += """
void wlr_matrix_identity(float mat[static 9]);

void wlr_matrix_multiply(float mat[static 9], const float a[static 9],
    const float b[static 9]);

void wlr_matrix_transpose(float mat[static 9], const float a[static 9]);

void wlr_matrix_translate(float mat[static 9], float x, float y);

void wlr_matrix_scale(float mat[static 9], float x, float y);

void wlr_matrix_rotate(float mat[static 9], float rad);

void wlr_matrix_transform(float mat[static 9],
    enum wl_output_transform transform);

void wlr_matrix_project_box(float mat[static 9], const struct wlr_box *box,
    enum wl_output_transform transform, float rotation,
    const float projection[static 9]);
"""

# Adapted from /usr/include/pixman-1/pixman.h
# Used for some wlr_output methods
CDEF += """
struct pixman_region32 {
    ...;
};

struct pixman_box32 {
    int32_t x1, y1, x2, y2;
    ...;
};

void pixman_region32_init(struct pixman_region32 *region);
void pixman_region32_init_rect(struct pixman_region32 *region, int x, int y,
    unsigned int width, unsigned int height);

void pixman_region32_fini(struct pixman_region32 *region);

struct pixman_box32* pixman_region32_rectangles(struct pixman_region32 *region,
    int *n_rects);

bool pixman_region32_not_empty(struct pixman_region32 *region);
"""

# types/wlr_output.h
CDEF += """
struct wlr_output_mode {
    int32_t width, height;
    int32_t refresh; // mHz
    bool preferred;
    struct wl_list link;
    ...;
};

struct wlr_output_state {
    ...;
};

struct wlr_output {
    const struct wlr_output_impl *impl;
    struct wlr_backend *backend;
    struct wl_display *display;

    struct wl_global *global;
    struct wl_list resources;

    char *name;
    char *description; // may be NULL
    char *make, *model, *serial;
    int32_t phys_width, phys_height; // mm

    // Note: some backends may have zero modes
    struct wl_list modes; // wlr_output_mode::link
    struct wlr_output_mode *current_mode;
    int32_t width, height;
    int32_t refresh; // mHz, may be zero

    bool enabled;
    float scale;
    enum wl_output_subpixel subpixel;
    enum wl_output_transform transform;
    enum wlr_output_adaptive_sync_status adaptive_sync_status;
    uint32_t render_format;

    bool needs_frame;
    bool frame_pending;
    float transform_matrix[9];
    bool non_desktop;

    struct wlr_output_state pending;

    // Commit sequence number. Incremented on each commit, may overflow.
    uint32_t commit_seq;

    struct {
        struct wl_signal frame;
        struct wl_signal damage;
        struct wl_signal needs_frame;
        struct wl_signal precommit;
        struct wl_signal commit;
        struct wl_signal present;
        struct wl_signal bind;
        struct wl_signal description;
        struct wl_signal request_state;
        struct wl_signal destroy;
    } events;

    struct wl_event_source *idle_frame;
    struct wl_event_source *idle_done;
    int attach_render_locks;
    struct wl_list cursors;
    struct wlr_output_cursor *hardware_cursor;
    struct wlr_swapchain *cursor_swapchain;
    struct wlr_buffer *cursor_front_buffer;
    int software_cursor_locks;
    struct wlr_allocator *allocator;
    struct wlr_renderer *renderer;
    struct wlr_swapchain *swapchain;
    struct wlr_buffer *back_buffer;
    struct wl_listener display_destroy;
    struct wlr_addon_set addons;

    void *data;
    ...;
};

struct wlr_output_event_request_state {
    struct wlr_output *output;
    const struct wlr_output_state *state;
    ...;
};

void wlr_output_enable(struct wlr_output *output, bool enable);
void wlr_output_create_global(struct wlr_output *output);
void wlr_output_destroy_global(struct wlr_output *output);

bool wlr_output_init_render(struct wlr_output *output,
    struct wlr_allocator *allocator, struct wlr_renderer *renderer);

struct wlr_output_mode *wlr_output_preferred_mode(struct wlr_output *output);

void wlr_output_set_mode(struct wlr_output *output,
    struct wlr_output_mode *mode);
void wlr_output_set_custom_mode(struct wlr_output *output, int32_t width,
    int32_t height, int32_t refresh);
void wlr_output_set_transform(struct wlr_output *output,
    enum wl_output_transform transform);
void wlr_output_set_scale(struct wlr_output *output, float scale);

bool wlr_output_attach_render(struct wlr_output *output, int *buffer_age);
void wlr_output_transformed_resolution(struct wlr_output *output,
    int *width, int *height);
void wlr_output_effective_resolution(struct wlr_output *output,
    int *width, int *height);
void wlr_output_set_damage(struct wlr_output *output,
    struct pixman_region32 *damage);
bool wlr_output_test(struct wlr_output *output);
bool wlr_output_commit(struct wlr_output *output);
void wlr_output_rollback(struct wlr_output *output);
bool wlr_output_commit_state(struct wlr_output *output,
    const struct wlr_output_state *state);

void wlr_output_render_software_cursors(struct wlr_output *output,
    struct pixman_region32 *damage);

enum wl_output_transform wlr_output_transform_invert(
    enum wl_output_transform tr);

void wlr_output_state_init(struct wlr_output_state *state);
void wlr_output_state_finish(struct wlr_output_state *state);
void wlr_output_state_set_enabled(struct wlr_output_state *state,
    bool enabled);
void wlr_output_state_set_mode(struct wlr_output_state *state,
    struct wlr_output_mode *mode);
void wlr_output_state_set_custom_mode(struct wlr_output_state *state,
        int32_t width, int32_t height, int32_t refresh);
"""

# types/wlr_output_layout.h
CDEF += """
struct wlr_output_layout {
    struct wl_list outputs;

    struct {
        struct wl_signal add;
        struct wl_signal change;
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};
struct wlr_output_layout *wlr_output_layout_create(void);
void wlr_output_layout_destroy(struct wlr_output_layout *layout);

void wlr_output_layout_output_coords(struct wlr_output_layout *layout,
    struct wlr_output *reference, double *lx, double *ly);

void wlr_output_layout_closest_point(struct wlr_output_layout *layout,
    struct wlr_output *reference, double lx, double ly, double *dest_lx,
    double *dest_ly);

bool wlr_output_layout_add(struct wlr_output_layout *layout,
    struct wlr_output *output, int lx, int ly);

void wlr_output_layout_remove(struct wlr_output_layout *layout,
    struct wlr_output *output);

void wlr_output_layout_get_box(struct wlr_output_layout *layout,
    struct wlr_output *reference, struct wlr_box *dest_box);

bool wlr_output_layout_add_auto(struct wlr_output_layout *layout,
    struct wlr_output *output);

struct wlr_output *wlr_output_layout_output_at(struct wlr_output_layout *layout,
    double lx, double ly);
"""

# types/wlr_output_management_v1.h
CDEF += """
struct wlr_output_manager_v1 {
    struct wl_display *display;
    struct wl_global *global;
    struct wl_list resources; // wl_resource_get_link
    struct wl_list heads; // wlr_output_head_v1::link
    uint32_t serial;
    bool current_configuration_dirty;

    struct {
        struct wl_signal apply; // wlr_output_configuration_v1
        struct wl_signal test; // wlr_output_configuration_v1
        struct wl_signal destroy;
    } events;

    struct wl_listener display_destroy;
    void *data;
    ...;
};

struct wlr_output_configuration_v1 {
    struct wl_list heads; // wlr_output_configuration_head_v1::link

    // client state
    struct wlr_output_manager_v1 *manager;
    uint32_t serial;
    bool finalized; // client has requested to apply the config
    bool finished; // feedback has been sent by the compositor
    struct wl_resource *resource; // can be NULL if destroyed early
    ...;
};

struct wlr_output_configuration_head_v1 {
    struct wlr_output_head_v1_state state;
    struct wlr_output_configuration_v1 *config;
    struct wl_list link; // wlr_output_configuration_v1::heads
    // client state
    struct wl_resource *resource; // can be NULL if finalized or disabled
    struct wl_listener output_destroy;
    ...;
};

struct wlr_output_head_v1_state {
    struct wlr_output *output;

    bool enabled;
    struct wlr_output_mode *mode;
    struct {
        int32_t width, height;
        int32_t refresh;
    } custom_mode;
    int32_t x, y;
    enum wl_output_transform transform;
    float scale;
    bool adaptive_sync_enabled;
    ...;
};

struct wlr_output_manager_v1 *wlr_output_manager_v1_create(
    struct wl_display *display);

void wlr_output_manager_v1_set_configuration(
    struct wlr_output_manager_v1 *manager,
    struct wlr_output_configuration_v1 *config);
struct wlr_output_configuration_v1 *wlr_output_configuration_v1_create(void);
void wlr_output_configuration_v1_send_succeeded(
    struct wlr_output_configuration_v1 *config);
void wlr_output_configuration_v1_send_failed(
    struct wlr_output_configuration_v1 *config);
struct wlr_output_configuration_head_v1 *
    wlr_output_configuration_head_v1_create(
    struct wlr_output_configuration_v1 *config, struct wlr_output *output);
void wlr_output_configuration_v1_destroy(
    struct wlr_output_configuration_v1 *config);
"""

# types/wlr_output_powewr_management_v1.h
CDEF += """
struct wlr_output_power_manager_v1 {
    struct wl_global *global;
    struct wl_list output_powers; // wlr_output_power_v1::link

    struct wl_listener display_destroy;

    struct {
        struct wl_signal set_mode; // wlr_output_power_v1_set_mode_event
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_output_power_v1 {
    struct wl_resource *resource;
    struct wlr_output *output;
    struct wlr_output_power_manager_v1 *manager;
    struct wl_list link;

    struct wl_listener output_destroy_listener;
    struct wl_listener output_commit_listener;

    void *data;
    ...;
};

struct wlr_output_power_v1_set_mode_event {
    struct wlr_output *output;
    enum zwlr_output_power_v1_mode mode;
    ...;
};

struct wlr_output_power_manager_v1 *wlr_output_power_manager_v1_create(
    struct wl_display *display);
"""

# types/wlr_pointer.h
CDEF += """
struct wlr_pointer {
    struct wlr_input_device base;
    const struct wlr_pointer_impl *impl;
    char *output_name;

    struct {
        struct wl_signal motion;
        struct wl_signal motion_absolute;
        struct wl_signal button;
        struct wl_signal axis;
        struct wl_signal frame;
        struct wl_signal swipe_begin;
        struct wl_signal swipe_update;
        struct wl_signal swipe_end;
        struct wl_signal pinch_begin;
        struct wl_signal pinch_update;
        struct wl_signal pinch_end;
        struct wl_signal hold_begin;
        struct wl_signal hold_end;
    } events;

    void *data;

    ...;
};

struct wlr_pointer_motion_event {
    struct wlr_pointer *pointer;
    uint32_t time_msec;
    double delta_x, delta_y;
    double unaccel_dx, unaccel_dy;
    ...;
};

struct wlr_pointer_motion_absolute_event {
    struct wlr_pointer *pointer;
    uint32_t time_msec;
    double x, y;
    ...;
};

struct wlr_pointer_button_event {
    struct wlr_pointer *pointer;
    uint32_t time_msec;
    uint32_t button;
    enum wlr_button_state state;
    ...;
};

enum wlr_axis_source {
    WLR_AXIS_SOURCE_WHEEL,
    WLR_AXIS_SOURCE_FINGER,
    WLR_AXIS_SOURCE_CONTINUOUS,
    WLR_AXIS_SOURCE_WHEEL_TILT,
};

enum wlr_axis_orientation {
    WLR_AXIS_ORIENTATION_VERTICAL,
    WLR_AXIS_ORIENTATION_HORIZONTAL,
};

struct wlr_pointer_axis_event {
    struct wlr_pointer *pointer;
    uint32_t time_msec;
    enum wlr_axis_source source;
    enum wlr_axis_orientation orientation;
    double delta;
    int32_t delta_discrete;
    ...;
};

struct wlr_pointer_swipe_begin_event {
    struct wlr_pointer *pointer;
    uint32_t time_msec;
    uint32_t fingers;
    ...;
};

struct wlr_pointer_swipe_update_event {
    struct wlr_pointer *pointer;
    uint32_t time_msec;
    uint32_t fingers;
    double dx, dy;
    ...;
};

struct wlr_pointer_swipe_end_event {
    struct wlr_pointer *pointer;
    uint32_t time_msec;
    bool cancelled;
    ...;
};

struct wlr_pointer_pinch_begin_event {
    struct wlr_pointer *pointer;
    uint32_t time_msec;
    uint32_t fingers;
    ...;
};

struct wlr_pointer_pinch_update_event {
    struct wlr_pointer *pointer;
    uint32_t time_msec;
    uint32_t fingers;
    double dx, dy;
    double scale;
    double rotation;
    ...;
};

struct wlr_pointer_pinch_end_event {
    struct wlr_pointer *pointer;
    uint32_t time_msec;
    bool cancelled;
    ...;
};

struct wlr_pointer_hold_begin_event {
    struct wlr_pointer *pointer;
    uint32_t time_msec;
    uint32_t fingers;
    ...;
};

struct wlr_pointer_hold_end_event {
    struct wlr_pointer *pointer;
    uint32_t time_msec;
    bool cancelled;
    ...;
};

struct wlr_pointer *wlr_pointer_from_input_device(
    struct wlr_input_device *input_device);
"""

# types/wlr_pointer_constraints_v1.h
CDEF += """
enum wlr_pointer_constraint_v1_type {
    WLR_POINTER_CONSTRAINT_V1_LOCKED,
    WLR_POINTER_CONSTRAINT_V1_CONFINED,
    ...
};

enum wlr_pointer_constraint_v1_state_field {
    WLR_POINTER_CONSTRAINT_V1_STATE_REGION = 1 << 0,
    WLR_POINTER_CONSTRAINT_V1_STATE_CURSOR_HINT = 1 << 1,
    ...
};

struct wlr_pointer_constraint_v1_state {
    uint32_t committed; // enum wlr_pointer_constraint_v1_state_field
    struct pixman_region32 region;
    struct {
        double x, y;
    } cursor_hint;
    ...;
};

struct wlr_pointer_constraint_v1 {
    struct wlr_pointer_constraints_v1 *pointer_constraints;

    struct wl_resource *resource;
    struct wlr_surface *surface;
    struct wlr_seat *seat;
    enum zwp_pointer_constraints_v1_lifetime lifetime;
    enum wlr_pointer_constraint_v1_type type;
    struct pixman_region32 region;

    struct wlr_pointer_constraint_v1_state current, pending;

    struct wl_listener surface_commit;
    struct wl_listener surface_destroy;
    struct wl_listener seat_destroy;

    struct wl_list link; // wlr_pointer_constraints_v1::constraints

    struct {
        struct wl_signal set_region;
        struct wl_signal destroy;
    } events;

   void *data;
   ...;
};

struct wlr_pointer_constraints_v1 {
    struct wl_global *global;
    struct wl_list constraints; // wlr_pointer_constraint_v1::link

    struct {
        struct wl_signal new_constraint;
    } events;

    struct wl_listener display_destroy;

    void *data;
    ...;
};

struct wlr_pointer_constraints_v1 *wlr_pointer_constraints_v1_create(
    struct wl_display *display);
struct wlr_pointer_constraint_v1 *
wlr_pointer_constraints_v1_constraint_for_surface(
    struct wlr_pointer_constraints_v1 *pointer_constraints,
    struct wlr_surface *surface, struct wlr_seat *seat);
void wlr_pointer_constraint_v1_send_activated(
    struct wlr_pointer_constraint_v1 *constraint);
void wlr_pointer_constraint_v1_send_deactivated(
    struct wlr_pointer_constraint_v1 *constraint);
"""

# types/wlr_pointer_gestures_v1.h
CDEF += """
struct wlr_pointer_gestures_v1 {
    struct wl_global *global;
    struct wl_list swipes;
    struct wl_list pinches;
    struct wl_list holds;

    struct wl_listener display_destroy;

    struct {
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_pointer_gestures_v1 *wlr_pointer_gestures_v1_create(
    struct wl_display *display);

void wlr_pointer_gestures_v1_send_swipe_begin(
    struct wlr_pointer_gestures_v1 *gestures,
    struct wlr_seat *seat,
    uint32_t time_msec,
    uint32_t fingers);
void wlr_pointer_gestures_v1_send_swipe_update(
    struct wlr_pointer_gestures_v1 *gestures,
    struct wlr_seat *seat,
    uint32_t time_msec,
    double dx,
    double dy);
void wlr_pointer_gestures_v1_send_swipe_end(
    struct wlr_pointer_gestures_v1 *gestures,
    struct wlr_seat *seat,
    uint32_t time_msec,
    bool cancelled);

void wlr_pointer_gestures_v1_send_pinch_begin(
    struct wlr_pointer_gestures_v1 *gestures,
    struct wlr_seat *seat,
    uint32_t time_msec,
    uint32_t fingers);
void wlr_pointer_gestures_v1_send_pinch_update(
    struct wlr_pointer_gestures_v1 *gestures,
    struct wlr_seat *seat,
    uint32_t time_msec,
    double dx,
    double dy,
    double scale,
    double rotation);
void wlr_pointer_gestures_v1_send_pinch_end(
    struct wlr_pointer_gestures_v1 *gestures,
    struct wlr_seat *seat,
    uint32_t time_msec,
    bool cancelled);

void wlr_pointer_gestures_v1_send_hold_begin(
    struct wlr_pointer_gestures_v1 *gestures,
    struct wlr_seat *seat,
    uint32_t time_msec,
    uint32_t fingers);
void wlr_pointer_gestures_v1_send_hold_end(
    struct wlr_pointer_gestures_v1 *gestures,
    struct wlr_seat *seat,
    uint32_t time_msec,
    bool cancelled);
"""

# types/wlr_primary_selection_v1.h
CDEF += """
struct wlr_primary_selection_v1_device_manager {
    struct wl_global *global;
    struct wl_list devices;

    struct wl_listener display_destroy;

    struct {
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};
struct wlr_primary_selection_v1_device_manager *
    wlr_primary_selection_v1_device_manager_create(struct wl_display *display);
"""

# types/wlr_presentation_time.h
CDEF += """
struct wlr_presentation {
    ...;
};
struct wlr_presentation *wlr_presentation_create(struct wl_display *display,
    struct wlr_backend *backend);
"""

# types/wlr_primary_selection.h
CDEF += """
void wlr_seat_set_primary_selection(struct wlr_seat *seat,
    struct wlr_primary_selection_source *source, uint32_t serial);
"""

# types/wlr_relative_pointer_v1.h
CDEF += """
struct wlr_relative_pointer_manager_v1 {
    struct wl_global *global;
    struct wl_list relative_pointers; // wlr_relative_pointer_v1::link

    struct {
        struct wl_signal destroy;
        struct wl_signal new_relative_pointer; // wlr_relative_pointer_v1
    } events;
    ...;
};

struct wlr_relative_pointer_v1 {
    struct wl_resource *resource;
    struct wl_resource *pointer_resource;
    struct wlr_seat *seat;
    struct wl_list link; // wlr_relative_pointer_manager_v1::relative_pointers

    struct {
        struct wl_signal destroy;
    } events;
    ...;
};

struct wlr_relative_pointer_manager_v1 *wlr_relative_pointer_manager_v1_create(
    struct wl_display *display);

void wlr_relative_pointer_manager_v1_send_relative_motion(
    struct wlr_relative_pointer_manager_v1 *manager, struct wlr_seat *seat,
    uint64_t time_usec, double dx, double dy,
    double dx_unaccel, double dy_unaccel);
"""

# types/wlr_scene.h
CDEF += """
typedef bool (*wlr_scene_buffer_point_accepts_input_func_t)(
    struct wlr_scene_buffer *buffer, int sx, int sy);
typedef void (*wlr_scene_buffer_iterator_func_t)(
    struct wlr_scene_buffer *buffer, int sx, int sy, void *user_data);
extern "Python" void buffer_iterator_callback(
    struct wlr_scene_buffer *buffer, int sx, int sy, void *user_data);

enum wlr_scene_node_type {
    WLR_SCENE_NODE_TREE,
    WLR_SCENE_NODE_RECT,
    WLR_SCENE_NODE_BUFFER,
};

struct wlr_scene_node {
    enum wlr_scene_node_type type;
    struct wlr_scene_tree *parent;
    struct wl_list link;

    bool enabled;
    int x, y;

    struct {
        struct wl_signal destroy;
    } events;

    void *data;
    struct wlr_addon_set addons;
    struct pixman_region32 visible;
    ...;
};

struct wlr_scene_tree {
    struct wlr_scene_node node;
    struct wl_list children;
    ...;
};

struct wlr_scene {
    struct wlr_scene_tree tree;
    struct wl_list outputs;
    struct wlr_presentation *presentation;
    ...;
};

struct wlr_scene_surface {
    struct wlr_scene_buffer *buffer;
    struct wlr_surface *surface;
    ...;
};

struct wlr_scene_rect {
    struct wlr_scene_node node;
    int width, height;
    float color[4];
    ...;
};

struct wlr_scene_buffer {
    struct wlr_scene_node node;
    struct wlr_buffer *buffer;

    struct {
        struct wl_signal outputs_update;
        struct wl_signal output_enter; // struct wlr_scene_output
        struct wl_signal output_leave; // struct wlr_scene_output
        struct wl_signal output_present; // struct wlr_scene_output
        struct wl_signal frame_done; // struct timespec
    } events;

    wlr_scene_buffer_point_accepts_input_func_t point_accepts_input;
    struct wlr_scene_output *primary_output;
    ...;
};

struct wlr_scene_output {
    struct wlr_output *output;
    struct wl_list link;
    struct wlr_scene *scene;
    struct wlr_addon addon;
    struct wlr_damage_ring damage_ring;
    int x, y;

    struct {
        struct wl_signal destroy;
    } events;
    ...;
};

struct wlr_scene_layer_surface_v1 {
    struct wlr_scene_tree *tree;
    struct wlr_layer_surface_v1 *layer_surface;
    ...;
};

void wlr_scene_node_destroy(struct wlr_scene_node *node);

void wlr_scene_node_set_enabled(struct wlr_scene_node *node, bool enabled);

void wlr_scene_node_set_position(struct wlr_scene_node *node, int x, int y);

void wlr_scene_node_place_above(struct wlr_scene_node *node,
    struct wlr_scene_node *sibling);

void wlr_scene_node_place_below(struct wlr_scene_node *node,
    struct wlr_scene_node *sibling);

void wlr_scene_node_raise_to_top(struct wlr_scene_node *node);

void wlr_scene_node_lower_to_bottom(struct wlr_scene_node *node);

void wlr_scene_node_reparent(struct wlr_scene_node *node,
    struct wlr_scene_tree *new_parent);

bool wlr_scene_node_coords(struct wlr_scene_node *node, int *lx, int *ly);

void wlr_scene_node_for_each_buffer(struct wlr_scene_node *node,
    wlr_scene_buffer_iterator_func_t iterator, void *user_data);

struct wlr_scene_node *wlr_scene_node_at(struct wlr_scene_node *node,
    double lx, double ly, double *nx, double *ny);

struct wlr_scene *wlr_scene_create(void);

void wlr_scene_set_presentation(struct wlr_scene *scene,
    struct wlr_presentation *presentation);

struct wlr_scene_tree *wlr_scene_tree_create(struct wlr_scene_tree *parent);

struct wlr_scene_surface *wlr_scene_surface_create(struct wlr_scene_tree *parent,
    struct wlr_surface *surface);

struct wlr_scene_buffer *wlr_scene_buffer_from_node(struct wlr_scene_node *node);

struct wlr_scene_surface *wlr_scene_surface_try_from_buffer(
    struct wlr_scene_buffer *scene_buffer);

struct wlr_scene_rect *wlr_scene_rect_create(struct wlr_scene_tree *parent,
        int width, int height, const float color[static 4]);

void wlr_scene_rect_set_size(struct wlr_scene_rect *rect, int width, int height);

void wlr_scene_rect_set_color(struct wlr_scene_rect *rect, const float color[static 4]);

struct wlr_scene_buffer *wlr_scene_buffer_create(struct wlr_scene_tree *parent,
    struct wlr_buffer *buffer);

void wlr_scene_buffer_set_buffer(struct wlr_scene_buffer *scene_buffer,
    struct wlr_buffer *buffer);

void wlr_scene_buffer_set_buffer_with_damage(struct wlr_scene_buffer *scene_buffer,
    struct wlr_buffer *buffer, struct pixman_region32 *region);

void wlr_scene_buffer_set_opaque_region(struct wlr_scene_buffer *scene_buffer,
    struct pixman_region32 *region);

void wlr_scene_buffer_set_source_box(struct wlr_scene_buffer *scene_buffer,
    const struct wlr_fbox *box);

void wlr_scene_buffer_set_dest_size(struct wlr_scene_buffer *scene_buffer,
    int width, int height);

void wlr_scene_buffer_set_transform(struct wlr_scene_buffer *scene_buffer,
    enum wl_output_transform transform);

void wlr_scene_buffer_send_frame_done(struct wlr_scene_buffer *scene_buffer,
    struct timespec *now);

void wlr_scene_buffer_set_opacity(struct wlr_scene_buffer *scene_buffer,
    float opacity);

struct wlr_scene_output *wlr_scene_output_create(struct wlr_scene *scene,
    struct wlr_output *output);

void wlr_scene_output_destroy(struct wlr_scene_output *scene_output);

void wlr_scene_output_set_position(struct wlr_scene_output *scene_output,
    int lx, int ly);

bool wlr_scene_output_commit(struct wlr_scene_output *scene_output);

void wlr_scene_output_send_frame_done(struct wlr_scene_output *scene_output,
    struct timespec *now);

void wlr_scene_output_for_each_buffer(struct wlr_scene_output *scene_output,
    wlr_scene_buffer_iterator_func_t iterator, void *user_data);

struct wlr_scene_output *wlr_scene_get_scene_output(struct wlr_scene *scene,
    struct wlr_output *output);

bool wlr_scene_attach_output_layout(struct wlr_scene *scene,
    struct wlr_output_layout *output_layout);

struct wlr_scene_tree *wlr_scene_subsurface_tree_create(
    struct wlr_scene_tree *parent, struct wlr_surface *surface);

struct wlr_scene_tree *wlr_scene_xdg_surface_create(
    struct wlr_scene_tree *parent, struct wlr_xdg_surface *xdg_surface);

struct wlr_scene_layer_surface_v1 *wlr_scene_layer_surface_v1_create(
    struct wlr_scene_tree *parent, struct wlr_layer_surface_v1 *layer_surface);

void wlr_scene_layer_surface_v1_configure(
    struct wlr_scene_layer_surface_v1 *scene_layer_surface,
    const struct wlr_box *full_area, struct wlr_box *usable_area);

struct wlr_scene_tree *wlr_scene_drag_icon_create(
    struct wlr_scene_tree *parent, struct wlr_drag_icon *drag_icon);
"""

# types/wlr_screencopy_v1.h
CDEF += """
struct wlr_screencopy_manager_v1 {
    struct wl_global *global;
    struct wl_list frames; // wlr_screencopy_frame_v1::link

    struct wl_listener display_destroy;

    struct {
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_screencopy_manager_v1 *wlr_screencopy_manager_v1_create(
    struct wl_display *display);
"""

# types/wlr_seat.h
CDEF += """
struct timespec {
    int64_t tv_sec;
    int64_t tv_nsec;
    ...;
};
int clock_gettime(clockid_t clk_id, struct timespec *tp);

#define CLOCK_MONOTONIC ...

#define WLR_POINTER_BUTTONS_CAP 16

struct wlr_seat_touch_grab {
    const struct wlr_touch_grab_interface *interface;
    struct wlr_seat *seat;
    void *data;
    ...;
};
struct wlr_seat_keyboard_grab {
    const struct wlr_keyboard_grab_interface *interface;
    struct wlr_seat *seat;
    void *data;
    ...;
};
struct wlr_seat_pointer_grab {
    const struct wlr_pointer_grab_interface *interface;
    struct wlr_seat *seat;
    void *data;
    ...;
};

struct wlr_seat_pointer_state {
    struct wlr_seat *seat;
    struct wlr_seat_client *focused_client;
    struct wlr_surface *focused_surface;
    double sx, sy;

    struct wlr_seat_pointer_grab *grab;
    struct wlr_seat_pointer_grab *default_grab;

    uint32_t buttons[WLR_POINTER_BUTTONS_CAP];
    size_t button_count;
    uint32_t grab_button;
    uint32_t grab_serial;
    uint32_t grab_time;

    struct wl_listener surface_destroy;

    struct {
        struct wl_signal focus_change;
    } events;
    ...;
};
struct wlr_seat_keyboard_state {
    struct wlr_seat *seat;
    struct wlr_keyboard *keyboard;

    struct wlr_seat_client *focused_client;
    struct wlr_surface *focused_surface;

    struct wl_listener keyboard_destroy;
    struct wl_listener keyboard_keymap;
    struct wl_listener keyboard_repeat_info;

    struct wl_listener surface_destroy;

    struct wlr_seat_keyboard_grab *grab;
    struct wlr_seat_keyboard_grab *default_grab;

    struct {
        struct wl_signal focus_change;
    } events;
    ...;
};
struct wlr_seat_touch_state { ...; };

struct wlr_seat {
    struct wl_global *global;
    struct wl_display *display;
    struct wl_list clients;

    char *name;
    uint32_t capabilities;
    struct timespec last_event;

    struct wlr_data_source *selection_source;
    uint32_t selection_serial;
    struct wl_list selection_offers; // wlr_data_offer::link

    struct wlr_primary_selection_source *primary_selection_source;
    uint32_t primary_selection_serial;

    // `drag` goes away before `drag_source`, when the implicit grab ends
    struct wlr_drag *drag;
    struct wlr_data_source *drag_source;
    uint32_t drag_serial;
    struct wl_list drag_offers; // wlr_data_offer::link

    struct wlr_seat_pointer_state pointer_state;
    struct wlr_seat_keyboard_state keyboard_state;
    struct wlr_seat_touch_state touch_state;

    struct wl_listener display_destroy;
    struct wl_listener selection_source_destroy;
    struct wl_listener primary_selection_source_destroy;
    struct wl_listener drag_source_destroy;

    struct {
        struct wl_signal pointer_grab_begin;
        struct wl_signal pointer_grab_end;

        struct wl_signal keyboard_grab_begin;
        struct wl_signal keyboard_grab_end;

        struct wl_signal touch_grab_begin;
        struct wl_signal touch_grab_end;

        // wlr_seat_pointer_request_set_cursor_event
        struct wl_signal request_set_cursor;

        // wlr_seat_request_set_selection_event
        struct wl_signal request_set_selection;
        struct wl_signal set_selection;
        // wlr_seat_request_set_primary_selection_event
        struct wl_signal request_set_primary_selection;
        struct wl_signal set_primary_selection;

        // wlr_seat_request_start_drag_event
        struct wl_signal request_start_drag;
        struct wl_signal start_drag; // wlr_drag

        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_seat_pointer_request_set_cursor_event {
    struct wlr_seat_client *seat_client;
    struct wlr_surface *surface;
    uint32_t serial;
    int32_t hotspot_x, hotspot_y;
    ...;
};

struct wlr_seat_request_set_selection_event {
    struct wlr_data_source *source;
    uint32_t serial;
    ...;
};

struct wlr_seat_request_set_primary_selection_event {
    struct wlr_primary_selection_source *source;
    uint32_t serial;
    ...;
};

struct wlr_seat_request_start_drag_event {
    struct wlr_drag *drag;
    struct wlr_surface *origin;
    uint32_t serial;
    ...;
};

struct wlr_seat_pointer_focus_change_event {
    struct wlr_seat *seat;
    struct wlr_surface *old_surface, *new_surface;
    double sx, sy;
    ...;
};

struct wlr_seat_keyboard_focus_change_event {
    struct wlr_seat *seat;
    struct wlr_surface *old_surface, *new_surface;
    ...;
};

struct wlr_seat *wlr_seat_create(struct wl_display *display, const char *name);
void wlr_seat_destroy(struct wlr_seat *wlr_seat);

void wlr_seat_set_capabilities(struct wlr_seat *wlr_seat,
    uint32_t capabilities);

void wlr_seat_set_name(struct wlr_seat *wlr_seat, const char *name);

bool wlr_seat_pointer_surface_has_focus(struct wlr_seat *wlr_seat,
    struct wlr_surface *surface);
void wlr_seat_pointer_clear_focus(struct wlr_seat *wlr_seat);
void wlr_seat_pointer_start_grab(struct wlr_seat *wlr_seat,
    struct wlr_seat_pointer_grab *grab);
void wlr_seat_pointer_end_grab(struct wlr_seat *wlr_seat);
void wlr_seat_pointer_notify_enter(struct wlr_seat *wlr_seat,
    struct wlr_surface *surface, double sx, double sy);
void wlr_seat_pointer_notify_motion(struct wlr_seat *wlr_seat,
    uint32_t time_msec, double sx, double sy);
uint32_t wlr_seat_pointer_notify_button(struct wlr_seat *wlr_seat,
    uint32_t time_msec, uint32_t button, enum wlr_button_state state);
void wlr_seat_pointer_notify_axis(struct wlr_seat *wlr_seat, uint32_t time_msec,
    enum wlr_axis_orientation orientation, double value,
    int32_t value_discrete, enum wlr_axis_source source);
void wlr_seat_pointer_notify_frame(struct wlr_seat *wlr_seat);
bool wlr_seat_pointer_has_grab(struct wlr_seat *seat);

void wlr_seat_set_keyboard(struct wlr_seat *seat, struct wlr_keyboard *keyboard);
struct wlr_keyboard *wlr_seat_get_keyboard(struct wlr_seat *seat);

uint32_t wlr_seat_touch_notify_down(struct wlr_seat *seat,
    struct wlr_surface *surface, uint32_t time_msec,
    int32_t touch_id, double sx, double sy);
void wlr_seat_touch_notify_up(struct wlr_seat *seat, uint32_t time_msec,
    int32_t touch_id);
void wlr_seat_touch_notify_motion(struct wlr_seat *seat, uint32_t time_msec,
    int32_t touch_id, double sx, double sy);

void wlr_seat_keyboard_start_grab(struct wlr_seat *wlr_seat,
    struct wlr_seat_keyboard_grab *grab);
void wlr_seat_keyboard_end_grab(struct wlr_seat *wlr_seat);
void wlr_seat_keyboard_notify_key(struct wlr_seat *seat, uint32_t time_msec,
    uint32_t key, uint32_t state);
void wlr_seat_keyboard_notify_modifiers(struct wlr_seat *seat,
    struct wlr_keyboard_modifiers *modifiers);
void wlr_seat_keyboard_notify_enter(struct wlr_seat *seat,
    struct wlr_surface *surface, uint32_t keycodes[], size_t num_keycodes,
    struct wlr_keyboard_modifiers *modifiers);
void wlr_seat_keyboard_clear_focus(struct wlr_seat *wlr_seat);
void wlr_seat_pointer_notify_clear_focus(struct wlr_seat *wlr_seat);
bool wlr_seat_keyboard_has_grab(struct wlr_seat *seat);
bool wlr_seat_validate_pointer_grab_serial(struct wlr_seat *seat,
    struct wlr_surface *origin, uint32_t serial);
"""

# types/wlr_server_decoration.h
CDEF += """
enum wlr_server_decoration_manager_mode {
    WLR_SERVER_DECORATION_MANAGER_MODE_NONE = 0,
    WLR_SERVER_DECORATION_MANAGER_MODE_CLIENT = 1,
    WLR_SERVER_DECORATION_MANAGER_MODE_SERVER = 2,
};
struct wlr_server_decoration_manager {
    struct wl_global *global;
    struct wl_list resources; // wl_resource_get_link
    struct wl_list decorations; // wlr_server_decoration::link
    uint32_t default_mode; // enum wlr_server_decoration_manager_mode
    struct wl_listener display_destroy;
    struct {
        struct wl_signal new_decoration;
        struct wl_signal destroy;
    } events;
    void *data;
    ...;
};
struct wlr_server_decoration_manager *wlr_server_decoration_manager_create(
    struct wl_display *display);
void wlr_server_decoration_manager_set_default_mode(
    struct wlr_server_decoration_manager *manager, uint32_t default_mode);
"""

# types/wlr_virtual_keyboard_v1.h
CDEF += """
struct wlr_virtual_keyboard_manager_v1 {
    struct wl_global *global;
    struct wl_list virtual_keyboards; // struct wlr_virtual_keyboard_v1*

    struct wl_listener display_destroy;

    struct {
        struct wl_signal new_virtual_keyboard; // struct wlr_virtual_keyboard_v1*
        struct wl_signal destroy;
    } events;
    ...;
};

struct wlr_virtual_keyboard_v1 {
    struct wlr_keyboard keyboard;
    struct wl_resource *resource;
    struct wlr_seat *seat;
    bool has_keymap;

    struct wl_list link;
    ...;
};

struct wlr_virtual_keyboard_manager_v1* wlr_virtual_keyboard_manager_v1_create(
    struct wl_display *display);
struct wlr_virtual_keyboard_v1 *wlr_input_device_get_virtual_keyboard(
    struct wlr_input_device *wlr_dev);
"""

# types/wlr_virtual_pointer_v1.h
CDEF += """
struct wlr_virtual_pointer_manager_v1 {
    struct wl_global *global;
    struct wl_list virtual_pointers;
    struct wl_listener display_destroy;
    struct {
        struct wl_signal new_virtual_pointer;
        struct wl_signal destroy;
    } events;
    ...;
};

struct wlr_virtual_pointer_v1 {
    struct wlr_pointer pointer;
    struct wl_resource *resource;
    struct wlr_pointer_axis_event axis_event[2];
    enum wl_pointer_axis axis;
    bool axis_valid[2];
    struct wl_list link;
    ...;
};

struct wlr_virtual_pointer_v1_new_pointer_event {
    struct wlr_virtual_pointer_v1 *new_pointer;
    struct wlr_seat *suggested_seat;
    struct wlr_output *suggested_output;
    ...;
};

struct wlr_virtual_pointer_manager_v1* wlr_virtual_pointer_manager_v1_create(
    struct wl_display *display);
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
struct wlr_xcursor *wlr_xcursor_manager_get_xcursor(
    struct wlr_xcursor_manager *manager, const char *name, float scale);
"""

# xcursor.h
CDEF += """
struct wlr_xcursor_image {
    uint32_t width;
    uint32_t height;
    uint32_t hotspot_x;
    uint32_t hotspot_y;
    uint32_t delay;
    uint8_t *buffer;
};
struct wlr_xcursor {
    unsigned int image_count;
    struct wlr_xcursor_image **images;
    char *name;
    uint32_t total_delay;
};
"""

# types/wlr_xdg_activation_v1.h
CDEF += """
struct wlr_xdg_activation_v1 {
    uint32_t token_timeout_msec;
    struct wl_list tokens;

    struct {
        struct wl_signal destroy;
        struct wl_signal request_activate;
        struct wl_signal new_token;
    } events;
    ...;
};

struct wlr_xdg_activation_v1_request_activate_event {
    struct wlr_xdg_activation_v1 *activation;
    struct wlr_xdg_activation_token_v1 *token;
    struct wlr_surface *surface;
};

struct wlr_xdg_activation_v1 *wlr_xdg_activation_v1_create(
    struct wl_display *display);
"""

# types/wlr_xdg_decoration_v1.h
CDEF += """
enum wlr_xdg_toplevel_decoration_v1_mode {
    WLR_XDG_TOPLEVEL_DECORATION_V1_MODE_NONE = 0,
    WLR_XDG_TOPLEVEL_DECORATION_V1_MODE_CLIENT_SIDE = 1,
    WLR_XDG_TOPLEVEL_DECORATION_V1_MODE_SERVER_SIDE = 2,
};

struct wlr_xdg_decoration_manager_v1 {
    struct wl_global *global;
    struct wl_list decorations; // wlr_xdg_toplevel_decoration::link

    struct wl_listener display_destroy;

    struct {
        struct wl_signal new_toplevel_decoration; // struct wlr_xdg_toplevel_decoration *
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_xdg_toplevel_decoration_v1_configure {
    struct wl_list link; // wlr_xdg_toplevel_decoration::configure_list
    struct wlr_xdg_surface_configure *surface_configure;
    enum wlr_xdg_toplevel_decoration_v1_mode mode;
    ...;
};

struct wlr_xdg_toplevel_decoration_v1_state {
    enum wlr_xdg_toplevel_decoration_v1_mode mode;
    ...;
};

struct wlr_xdg_toplevel_decoration_v1 {
    struct wl_resource *resource;
    struct wlr_xdg_surface *surface;
    struct wlr_xdg_decoration_manager_v1 *manager;
    struct wl_list link; // wlr_xdg_decoration_manager_v1::link

    struct wlr_xdg_toplevel_decoration_v1_state current, pending;

    enum wlr_xdg_toplevel_decoration_v1_mode scheduled_mode;
    enum wlr_xdg_toplevel_decoration_v1_mode requested_mode;

    bool added;

    struct wl_list configure_list; // wlr_xdg_toplevel_decoration_v1_configure::link

    struct {
        struct wl_signal destroy;
        struct wl_signal request_mode;
    } events;

    struct wl_listener surface_destroy;
    struct wl_listener surface_configure;
    struct wl_listener surface_ack_configure;
    struct wl_listener surface_commit;

    void *data;
    ...;
};

struct wlr_xdg_decoration_manager_v1 *
    wlr_xdg_decoration_manager_v1_create(struct wl_display *display);

uint32_t wlr_xdg_toplevel_decoration_v1_set_mode(
    struct wlr_xdg_toplevel_decoration_v1 *decoration,
    enum wlr_xdg_toplevel_decoration_v1_mode mode);
"""

# types/wlr_xdg_output_v1.h
CDEF += """
struct wlr_xdg_output_manager_v1 {
    struct wl_global *global;
    struct wlr_output_layout *layout;

    struct wl_list outputs;

    struct {
        struct wl_signal destroy;
    } events;

    struct wl_listener display_destroy;
    struct wl_listener layout_add;
    struct wl_listener layout_change;
    struct wl_listener layout_destroy;
    ...;
};

struct wlr_xdg_output_manager_v1 *wlr_xdg_output_manager_v1_create(
    struct wl_display *display, struct wlr_output_layout *layout);
"""

# util/addon.h
CDEF += """
struct wlr_addon_set {
    struct wl_list addons;
    ...;
};
struct wlr_addon {
    const struct wlr_addon_interface *impl;
    ...;
};
"""

# types/wlr_xdg_shell.h
CDEF += """
struct wlr_xdg_shell {
    struct wl_global *global;
    struct wl_list clients;
    struct wl_list popup_grabs;
    uint32_t ping_timeout;

    struct wl_listener display_destroy;

    struct {
        struct wl_signal new_surface;
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_xdg_client {
    struct wlr_xdg_shell *shell;
    struct wl_resource *resource;
    struct wl_client *client;
    struct wl_list surfaces;

    struct wl_list link; // wlr_xdg_shell::clients

    uint32_t ping_serial;
    struct wl_event_source *ping_timer;
    ...;
};

struct wlr_xdg_positioner_rules {
    struct wlr_box anchor_rect;
    enum xdg_positioner_anchor anchor;
    enum xdg_positioner_gravity gravity;
    enum xdg_positioner_constraint_adjustment constraint_adjustment;

    bool reactive;

    bool has_parent_configure_serial;
    uint32_t parent_configure_serial;

    struct {
        int32_t width, height;
    } size, parent_size;

    struct {
        int32_t x, y;
    } offset;
    ...;
};

struct wlr_xdg_popup_state {
    struct wlr_box geometry;

    bool reactive;
    ...;
};

enum wlr_xdg_popup_configure_field {
    WLR_XDG_POPUP_CONFIGURE_REPOSITION_TOKEN = 1 << 0,
};

struct wlr_xdg_popup_configure {
    uint32_t fields; // enum wlr_xdg_popup_configure_field
    struct wlr_box geometry;
    struct wlr_xdg_positioner_rules rules;
    uint32_t reposition_token;
    ...;
};

struct wlr_xdg_popup {
    struct wlr_xdg_surface *base;
    struct wl_list link;

    struct wl_resource *resource;
    bool sent_initial_configure;
    struct wlr_surface *parent;
    struct wlr_seat *seat;

    struct wlr_xdg_popup_configure scheduled;

    struct wlr_xdg_popup_state current, pending;

    struct {
        struct wl_signal reposition;
    } events;

    struct wl_list grab_link; // wlr_xdg_popup_grab.popups
    ...;
};

struct wlr_xdg_shell *wlr_xdg_shell_create(struct wl_display *display,
    uint32_t version);

struct wlr_xdg_toplevel_state {
    bool maximized, fullscreen, resizing, activated;
    uint32_t tiled; // enum wlr_edges
    uint32_t width, height;
    uint32_t max_width, max_height;
    uint32_t min_width, min_height;
    ...;
};

struct wlr_xdg_toplevel_configure {
    bool maximized, fullscreen, resizing, activated;
    uint32_t tiled; // enum wlr_edges
    uint32_t width, height;
    ...;
};

struct wlr_xdg_toplevel_requested {
    bool maximized, minimized, fullscreen;
    struct wlr_output *fullscreen_output;
    struct wl_listener fullscreen_output_destroy;
    ...;
};

struct wlr_xdg_toplevel {
    struct wl_resource *resource;
    struct wlr_xdg_surface *base;
    bool sent_initial_configure;

    struct wlr_xdg_toplevel *parent;
    struct wl_listener parent_unmap;

    struct wlr_xdg_toplevel_state current, pending;

    struct wlr_xdg_toplevel_configure scheduled;

    struct wlr_xdg_toplevel_requested requested;

    char *title;
    char *app_id;

    struct {
        struct wl_signal request_maximize;
        struct wl_signal request_fullscreen;
        struct wl_signal request_minimize;
        struct wl_signal request_move;
        struct wl_signal request_resize;
        struct wl_signal request_show_window_menu;
        struct wl_signal set_parent;
        struct wl_signal set_title;
        struct wl_signal set_app_id;
    } events;
    ...;
};

enum wlr_xdg_surface_role {
    WLR_XDG_SURFACE_ROLE_NONE,
    WLR_XDG_SURFACE_ROLE_TOPLEVEL,
    WLR_XDG_SURFACE_ROLE_POPUP,
    ...
};

enum wlr_xdg_toplevel_wm_capabilities {
    WLR_XDG_TOPLEVEL_WM_CAPABILITIES_WINDOW_MENU = 1 << 0,
    WLR_XDG_TOPLEVEL_WM_CAPABILITIES_MAXIMIZE = 1 << 1,
    WLR_XDG_TOPLEVEL_WM_CAPABILITIES_FULLSCREEN = 1 << 2,
    WLR_XDG_TOPLEVEL_WM_CAPABILITIES_MINIMIZE = 1 << 3,
};

struct wlr_xdg_surface {
    struct wlr_xdg_client *client;
    struct wl_resource *resource;
    struct wlr_surface *surface;
    struct wl_list link; // wlr_xdg_client::surfaces
    enum wlr_xdg_surface_role role;

    union {
        struct wlr_xdg_toplevel *toplevel;
        struct wlr_xdg_popup *popup;
    };

    struct wl_list popups; // wlr_xdg_popup::link

    bool added, configured;
    struct wl_event_source *configure_idle;
    uint32_t scheduled_serial;
    struct wl_list configure_list;

    struct wlr_xdg_surface_state current, pending;

    struct wl_listener surface_commit;

    struct {
        struct wl_signal destroy;
        struct wl_signal ping_timeout;
        struct wl_signal new_popup;

        struct wl_signal configure; // wlr_xdg_surface_configure
        struct wl_signal ack_configure; // wlr_xdg_surface_configure
    } events;

    void *data;
    ...;
};

struct wlr_xdg_surface_configure {
    struct wlr_xdg_surface *surface;
    struct wl_list link; // wlr_xdg_surface::configure_list
    uint32_t serial;

    struct wlr_xdg_toplevel_configure *toplevel_configure;
    ...;
};

struct wlr_xdg_surface_state {
    uint32_t configure_serial;
    struct wlr_box geometry;
    ...;
};

struct wlr_xdg_toplevel_move_event {
    struct wlr_xdg_toplevel *toplevel;
    struct wlr_seat_client *seat;
    uint32_t serial;
    ...;
};

struct wlr_xdg_toplevel_resize_event {
    struct wlr_xdg_toplevel *toplevel;
    struct wlr_seat_client *seat;
    uint32_t serial;
    uint32_t edges;
    ...;
};

struct wlr_xdg_toplevel_show_window_menu_event {
    struct wlr_xdg_toplevel *toplevel;
    struct wlr_seat_client *seat;
    uint32_t serial;
    uint32_t x, y;
    ...;
};

void wlr_xdg_popup_unconstrain_from_box(struct wlr_xdg_popup *popup,
    const struct wlr_box *toplevel_sx_box);

void wlr_xdg_surface_ping(struct wlr_xdg_surface *surface);

uint32_t wlr_xdg_toplevel_set_size(struct wlr_xdg_toplevel *toplevel,
        int32_t width, int32_t height);
uint32_t wlr_xdg_toplevel_set_activated(struct wlr_xdg_toplevel *toplevel,
        bool activated);
uint32_t wlr_xdg_toplevel_set_maximized(struct wlr_xdg_toplevel *toplevel,
        bool maximized);
uint32_t wlr_xdg_toplevel_set_fullscreen(struct wlr_xdg_toplevel *toplevel,
        bool fullscreen);
uint32_t wlr_xdg_toplevel_set_resizing(struct wlr_xdg_toplevel *toplevel,
        bool resizing);
uint32_t wlr_xdg_toplevel_set_tiled(struct wlr_xdg_toplevel *toplevel,
        uint32_t tiled_edges);
uint32_t wlr_xdg_toplevel_set_bounds(struct wlr_xdg_toplevel *toplevel,
        int32_t width, int32_t height);
uint32_t wlr_xdg_toplevel_set_wm_capabilities(struct wlr_xdg_toplevel *toplevel,
        uint32_t caps);

void wlr_xdg_toplevel_send_close(struct wlr_xdg_toplevel *toplevel);
void wlr_xdg_popup_destroy(struct wlr_xdg_popup *popup);

struct wlr_surface *wlr_xdg_surface_surface_at(
    struct wlr_xdg_surface *surface, double sx, double sy,
    double *sub_x, double *sub_y);

struct wlr_xdg_surface *wlr_xdg_surface_try_from_wlr_surface(
    struct wlr_surface *surface);

void wlr_xdg_surface_get_geometry(struct wlr_xdg_surface *surface,
    struct wlr_box *box);

void wlr_xdg_surface_for_each_surface(struct wlr_xdg_surface *surface,
    wlr_surface_iterator_func_t iterator, void *user_data);

void wlr_xdg_surface_for_each_popup_surface(struct wlr_xdg_surface *surface,
    wlr_surface_iterator_func_t iterator, void *user_data);

uint32_t wlr_xdg_surface_schedule_configure(struct wlr_xdg_surface *surface);
"""

# util/edges.h
CDEF += """
enum wlr_edges {
    WLR_EDGE_NONE = ...,
    WLR_EDGE_TOP = ...,
    WLR_EDGE_BOTTOM = ...,
    WLR_EDGE_LEFT = ...,
    WLR_EDGE_RIGHT = ...,
    ...
};
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

# util/region.h
CDEF += """
void wlr_region_transform(struct pixman_region32 *dst, struct pixman_region32 *src,
    enum wl_output_transform transform, int width, int height);
"""

# backend/headless.h
CDEF += """
struct wlr_backend *wlr_headless_backend_create(struct wl_display *display);

struct wlr_output *wlr_headless_add_output(struct wlr_backend *backend,
    unsigned int width, unsigned int height);

bool wlr_backend_is_headless(struct wlr_backend *backend);
bool wlr_output_is_headless(struct wlr_output *output);
"""

# version.h
CDEF_VERSION = """
#define WLR_VERSION_MAJOR ...
#define WLR_VERSION_MINOR ...
#define WLR_VERSION_MICRO ...
"""
CDEF += CDEF_VERSION

SOURCE = """
#include <wlr/backend.h>
#include <wlr/backend/headless.h>
#include <wlr/backend/libinput.h>
#include <wlr/interfaces/wlr_keyboard.h>
#include <wlr/render/allocator.h>
#include <wlr/render/drm_format_set.h>
#include <wlr/render/wlr_renderer.h>
#include <wlr/types/wlr_buffer.h>
#include <wlr/types/wlr_compositor.h>
#include <wlr/types/wlr_cursor.h>
#include <wlr/types/wlr_damage_ring.h>
#include <wlr/types/wlr_data_control_v1.h>
#include <wlr/types/wlr_data_device.h>
#include <wlr/types/wlr_export_dmabuf_v1.h>
#include <wlr/types/wlr_viewporter.h>
#include <wlr/types/wlr_foreign_toplevel_management_v1.h>
#include <wlr/types/wlr_gamma_control_v1.h>
#include <wlr/types/wlr_idle.h>
#include <wlr/types/wlr_idle_inhibit_v1.h>
#include <wlr/types/wlr_idle_notify_v1.h>
#include <wlr/types/wlr_input_inhibitor.h>
#include <wlr/types/wlr_keyboard.h>
#include <wlr/types/wlr_layer_shell_v1.h>
#include <wlr/types/wlr_linux_dmabuf_v1.h>
#include <wlr/types/wlr_matrix.h>
#include <wlr/types/wlr_output.h>
#include <wlr/types/wlr_output_layout.h>
#include <wlr/types/wlr_output_management_v1.h>
#include <wlr/types/wlr_output_power_management_v1.h>
#include <wlr/types/wlr_pointer.h>
#include <wlr/types/wlr_pointer_constraints_v1.h>
#include <wlr/types/wlr_pointer_gestures_v1.h>
#include <wlr/types/wlr_presentation_time.h>
#include <wlr/types/wlr_primary_selection.h>
#include <wlr/types/wlr_primary_selection_v1.h>
#include <wlr/types/wlr_relative_pointer_v1.h>
#include <wlr/types/wlr_scene.h>
#include <wlr/types/wlr_screencopy_v1.h>
#include <wlr/types/wlr_seat.h>
#include <wlr/types/wlr_subcompositor.h>
#include <wlr/types/wlr_server_decoration.h>
#include <wlr/types/wlr_virtual_keyboard_v1.h>
#include <wlr/types/wlr_virtual_pointer_v1.h>
#include <wlr/types/wlr_xcursor_manager.h>
#include <wlr/types/wlr_xdg_activation_v1.h>
#include <wlr/types/wlr_xdg_decoration_v1.h>
#include <wlr/types/wlr_xdg_output_v1.h>
#include <wlr/types/wlr_xdg_shell.h>
#include <wlr/util/addon.h>
#include <wlr/util/box.h>
#include <wlr/util/log.h>
#include <wlr/util/region.h>
#include <wlr/version.h>

#include <xkbcommon/xkbcommon.h>
#include <xkbcommon/xkbcommon-keysyms.h>
#include <xkbcommon/xkbcommon-compose.h>

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

# types//wlr_layer_shell_v1.h
CDEF += """
struct wlr_layer_shell_v1 {
    struct wl_global *global;

    struct wl_listener display_destroy;

    struct {
        struct wl_signal new_surface;
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_layer_surface_v1_state {
    uint32_t anchor;
    int32_t exclusive_zone;
    struct {
        uint32_t top, right, bottom, left;
    } margin;
    enum zwlr_layer_surface_v1_keyboard_interactivity keyboard_interactive;
    uint32_t desired_width, desired_height;
    uint32_t actual_width, actual_height;
    enum zwlr_layer_shell_v1_layer layer;
    ...;
};

struct wlr_layer_surface_v1 {
    struct wlr_surface *surface;
    struct wlr_output *output;
    struct wl_resource *resource;
    struct wlr_layer_shell_v1 *shell;
    struct wl_list popups; // wlr_xdg_popup::link
    char *namespace;
    bool added, configured;
    struct wl_list configure_list;
    struct wlr_layer_surface_v1_state current, pending;
    struct {
        struct wl_signal destroy;
        struct wl_signal new_popup;
    } events;

    void *data;
    ...;
};

struct wlr_layer_shell_v1 *wlr_layer_shell_v1_create(struct wl_display *display,
    uint32_t version);

void wlr_layer_surface_v1_configure(struct wlr_layer_surface_v1 *surface,
    uint32_t width, uint32_t height);

void wlr_layer_surface_v1_destroy(struct wlr_layer_surface_v1 *surface);

struct wlr_layer_surface_v1 *wlr_layer_surface_v1_try_from_wlr_surface(
    struct wlr_surface *surface);

void wlr_layer_surface_v1_for_each_surface(struct wlr_layer_surface_v1 *surface,
    wlr_surface_iterator_func_t iterator, void *user_data);

struct wlr_surface *wlr_layer_surface_v1_surface_at(
    struct wlr_layer_surface_v1 *surface, double sx, double sy,
    double *sub_x, double *sub_y);
"""

check_version()

if has_xwayland():
    # xwayland.h
    print("Built with support for XWayland helpers.")

    SOURCE += """
    #include <wlr/xwayland.h>
    """

    CDEF += """
    typedef int... time_t;
    typedef struct {
        ...;
    } xcb_generic_event_t;
    typedef struct {
        ...;
    } xcb_ewmh_wm_strut_partial_t;
    typedef uint32_t xcb_pixmap_t;
    typedef uint32_t xcb_window_t;
    typedef uint32_t xcb_atom_t;
    typedef struct {
        ...;
    } xcb_icccm_wm_hints_t;
    typedef struct {
    uint32_t flags;
    int32_t x, y;
    int32_t width, height;
    int32_t min_width, min_height;
    int32_t max_width, max_height;
    int32_t width_inc, height_inc;
    int32_t min_aspect_num, min_aspect_den;
    int32_t max_aspect_num, max_aspect_den;
    int32_t base_width, base_height;
    uint32_t win_gravity;
    } xcb_size_hints_t;

    struct wlr_xwm;
    struct wlr_xwayland_cursor;
    struct wlr_xwayland_server_options {
        bool lazy;
        bool enable_wm;
        bool no_touch_pointer_emulation;
        ...;
    };
    struct wlr_xwayland_server {
        pid_t pid;
        struct wl_client *client;
        struct wl_event_source *pipe_source;
        int wm_fd[2], wl_fd[2];
        time_t server_start;
        int display;
        char display_name[16];
        int x_fd[2];
        struct wl_event_source *x_fd_read_event[2];
        struct wlr_xwayland_server_options options;
        struct wl_display *wl_display;
        struct {
            struct wl_signal ready;
            struct wl_signal destroy;
        } events;
        struct wl_listener client_destroy;
        struct wl_listener display_destroy;
        void *data;
        ...;
    };
    struct wlr_xwayland {
        struct wlr_xwayland_server *server;
        struct wlr_xwm *xwm;
        struct wlr_xwayland_cursor *cursor;
        const char *display_name;
        struct wl_display *wl_display;
        struct wlr_compositor *compositor;
        struct wlr_seat *seat;
        struct {
            struct wl_signal ready;
            struct wl_signal new_surface;
            struct wl_signal remove_startup_info;
        } events;
        int (*user_event_handler)(struct wlr_xwm *xwm, xcb_generic_event_t *event);
        struct wl_listener server_ready;
        struct wl_listener server_destroy;
        struct wl_listener seat_destroy;
        void *data;
        ...;
    };
    enum wlr_xwayland_surface_decorations {
        WLR_XWAYLAND_SURFACE_DECORATIONS_ALL = 0,
        WLR_XWAYLAND_SURFACE_DECORATIONS_NO_BORDER = 1,
        WLR_XWAYLAND_SURFACE_DECORATIONS_NO_TITLE = 2,
    };
    enum wlr_xwayland_icccm_input_model {
        WLR_ICCCM_INPUT_MODEL_NONE = 0,
        WLR_ICCCM_INPUT_MODEL_PASSIVE = 1,
        WLR_ICCCM_INPUT_MODEL_LOCAL = 2,
        WLR_ICCCM_INPUT_MODEL_GLOBAL = 3,
    };
    struct wlr_xwayland_surface {
        xcb_window_t window_id;
        struct wlr_xwm *xwm;
        uint32_t surface_id;
        uint64_t serial;
        struct wl_list link;
        struct wl_list stack_link;
        struct wl_list unpaired_link;
        struct wlr_surface *surface;
        struct wlr_addon surface_addon;
        struct wl_listener surface_commit;
        struct wl_listener surface_map;
        struct wl_listener surface_unmap;
        int16_t x, y;
        uint16_t width, height;
        uint16_t saved_width, saved_height;
        bool override_redirect;
        char *title;
        char *class;
        char *instance;
        char *role;
        char *startup_id;
        pid_t pid;
        bool has_utf8_title;
        struct wl_list children; // wlr_xwayland_surface::parent_link
        struct wlr_xwayland_surface *parent;
        struct wl_list parent_link; // wlr_xwayland_surface::children
        xcb_atom_t *window_type;
        size_t window_type_len;
        xcb_atom_t *protocols;
        size_t protocols_len;
        uint32_t decorations;
        xcb_icccm_wm_hints_t *hints;
        xcb_size_hints_t *size_hints;
        xcb_ewmh_wm_strut_partial_t *strut_partial;
        bool pinging;
        struct wl_event_source *ping_timer;
        bool modal;
        bool fullscreen;
        bool maximized_vert, maximized_horz;
        bool minimized;
        bool withdrawn;
        bool has_alpha;
        struct {
            struct wl_signal destroy;
            struct wl_signal request_configure;
            struct wl_signal request_move;
            struct wl_signal request_resize;
            struct wl_signal request_minimize;
            struct wl_signal request_maximize;
            struct wl_signal request_fullscreen;
            struct wl_signal request_activate;
            struct wl_signal associate;
            struct wl_signal dissociate;
            struct wl_signal set_title;
            struct wl_signal set_class;
            struct wl_signal set_role;
            struct wl_signal set_parent;
            struct wl_signal set_pid;
            struct wl_signal set_startup_id;
            struct wl_signal set_window_type;
            struct wl_signal set_hints;
            struct wl_signal set_decorations;
            struct wl_signal set_strut_partial;
            struct wl_signal set_override_redirect;
            struct wl_signal set_geometry;
            struct wl_signal ping_timeout;
        } events;
        void *data;
        ...;
    };
    struct wlr_xwayland_surface_configure_event {
        struct wlr_xwayland_surface *surface;
        int16_t x, y;
        uint16_t width, height;
        uint16_t mask; // xcb_config_window_t
        ...;
    };
    struct wlr_xwayland_move_event {
        struct wlr_xwayland_surface *surface;
        ...;
    };
    struct wlr_xwayland_remove_startup_info_event  {
        const char *id;
        xcb_window_t window;
        ...;
    };
    struct wlr_xwayland_resize_event {
        struct wlr_xwayland_surface *surface;
        uint32_t edges;
        ...;
    };
    struct wlr_xwayland_minimize_event {
        struct wlr_xwayland_surface *surface;
        bool minimize;
        ...;
    };
    struct wlr_xwayland_server *wlr_xwayland_server_create(
        struct wl_display *display, struct wlr_xwayland_server_options *options);
    void wlr_xwayland_server_destroy(struct wlr_xwayland_server *server);
    struct wlr_xwayland *wlr_xwayland_create(struct wl_display *wl_display,
        struct wlr_compositor *compositor, bool lazy);
    void wlr_xwayland_destroy(struct wlr_xwayland *wlr_xwayland);
    void wlr_xwayland_set_cursor(struct wlr_xwayland *wlr_xwayland,
        uint8_t *pixels, uint32_t stride, uint32_t width, uint32_t height,
        int32_t hotspot_x, int32_t hotspot_y);
    void wlr_xwayland_surface_activate(struct wlr_xwayland_surface *surface,
        bool activated);
    void wlr_xwayland_surface_restack(struct wlr_xwayland_surface *surface,
        struct wlr_xwayland_surface *sibling, enum xcb_stack_mode_t mode);
    void wlr_xwayland_surface_configure(struct wlr_xwayland_surface *surface,
        int16_t x, int16_t y, uint16_t width, uint16_t height);
    void wlr_xwayland_surface_close(struct wlr_xwayland_surface *surface);
    void wlr_xwayland_surface_set_minimized(struct wlr_xwayland_surface *surface,
        bool minimized);
    void wlr_xwayland_surface_set_maximized(struct wlr_xwayland_surface *surface,
        bool maximized);
    void wlr_xwayland_surface_set_fullscreen(struct wlr_xwayland_surface *surface,
        bool fullscreen);
    void wlr_xwayland_set_seat(struct wlr_xwayland *xwayland,
        struct wlr_seat *seat);
    struct wlr_xwayland_surface *wlr_xwayland_surface_try_from_wlr_surface(
        struct wlr_surface *surface);
    void wlr_xwayland_surface_ping(struct wlr_xwayland_surface *surface);
    bool wlr_xwayland_or_surface_wants_focus(
        const struct wlr_xwayland_surface *xsurface);
    enum wlr_xwayland_icccm_input_model wlr_xwayland_icccm_input_model(
        const struct wlr_xwayland_surface *xsurface);

    typedef struct xcb_intern_atom_cookie_t {
        ...;
    } xcb_intern_atom_cookie_t;
    typedef ... xcb_connection_t;
    typedef struct xcb_intern_atom_reply_t {
        uint8_t    response_type;
        uint8_t    pad0;
        uint16_t   sequence;
        uint32_t   length;
        xcb_atom_t atom;
        ...;
    } xcb_intern_atom_reply_t;
    typedef ... xcb_generic_error_t;

    int xcb_connection_has_error(xcb_connection_t *c);
    xcb_connection_t *xcb_connect(const char *displayname, int *screenp);
    void xcb_disconnect(xcb_connection_t *c);
    xcb_intern_atom_cookie_t xcb_intern_atom(xcb_connection_t *conn, uint8_t only_if_exists,
        uint16_t name_len, const char *name);
    xcb_intern_atom_reply_t *xcb_intern_atom_reply(xcb_connection_t *conn,
        xcb_intern_atom_cookie_t cookie, xcb_generic_error_t **e);
    """

ffi_builder = FFI()
ffi_builder.set_source(
    "wlroots._ffi",
    SOURCE,
    libraries=["wlroots"],
    define_macros=[("WLR_USE_UNSTABLE", None)],
    include_dirs=["/usr/include/pixman-1", include_dir],
)
ffi_builder.include(pywayland_ffi)
ffi_builder.include(xkb_ffi)
ffi_builder.cdef(CDEF)

if __name__ == "__main__":
    ffi_builder.compile()
