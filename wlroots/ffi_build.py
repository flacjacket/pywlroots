# Copyright (c) 2018 Sean Vig

from pathlib import Path

from cffi import FFI
from pywayland.ffi_build import ffi_builder as pywayland_ffi
from xkbcommon.ffi_build import ffibuilder as xkb_ffi


# backend.h
CDEF = """
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

struct wlr_backend *wlr_backend_autocreate(struct wl_display *display);

bool wlr_backend_start(struct wlr_backend *backend);
void wlr_backend_destroy(struct wlr_backend *backend);
struct wlr_renderer *wlr_backend_get_renderer(struct wlr_backend *backend);
struct wlr_session *wlr_backend_get_session(struct wlr_backend *backend);
"""

# backend/session.h
CDEF += """
bool wlr_session_change_vt(struct wlr_session *session, unsigned vt);
"""

# render/wlr_renderer.h
CDEF += """
void wlr_renderer_begin(struct wlr_renderer *r, int width, int height);
void wlr_renderer_end(struct wlr_renderer *r);
void wlr_renderer_clear(struct wlr_renderer *r, const float color[static 4]);

bool wlr_render_texture(struct wlr_renderer *r, struct wlr_texture *texture,
    const float projection[static 9], int x, int y, float alpha);
bool wlr_render_texture_with_matrix(struct wlr_renderer *r,
    struct wlr_texture *texture, const float matrix[static 9], float alpha);

const enum wl_shm_format *wlr_renderer_get_shm_texture_formats(
    struct wlr_renderer *r, size_t *len);

void wlr_renderer_init_wl_display(struct wlr_renderer *r, struct wl_display *wl_display);
void wlr_renderer_destroy(struct wlr_renderer *renderer);
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

void wlr_box_rotated_bounds(struct wlr_box *dest, const struct wlr_box *box, float rotation);
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

        struct wl_signal touch_up;
        struct wl_signal touch_down;
        struct wl_signal touch_motion;
        struct wl_signal touch_cancel;

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
struct wlr_compositor *wlr_compositor_create(struct wl_display *display,
    struct wlr_renderer *renderer);
"""

# types/wlr_data_device.h
CDEF += """
struct wlr_data_device_manager *wlr_data_device_manager_create(
    struct wl_display *display);

void wlr_seat_set_selection(struct wlr_seat *seat,
    struct wlr_data_source *source, uint32_t serial);
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
    const struct wlr_input_device_impl *impl;

    enum wlr_input_device_type type;
    unsigned int vendor, product;
    char *name;
    double width_mm, height_mm;
    char *output_name;

    /* wlr_input_device.type determines which of these is valid */
    union {
        void *_device;
        struct wlr_keyboard *keyboard;
        struct wlr_pointer *pointer;
        struct wlr_switch *switch_device;
        struct wlr_touch *touch;
        struct wlr_tablet *tablet;
        struct wlr_tablet_pad *tablet_pad;
    };

    struct {
        struct wl_signal destroy;
    } events;

    void *data;

    struct wl_list link;
    ...;
};
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
    const struct wlr_keyboard_impl *impl;
    struct wlr_keyboard_group *group;

    char *keymap_string;
    size_t keymap_size;
    struct xkb_keymap *keymap;
    struct xkb_state *xkb_state;
    xkb_led_index_t led_indexes[WLR_LED_COUNT];
    xkb_mod_index_t mod_indexes[WLR_MODIFIER_COUNT];

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
        struct wl_signal destroy;
    } events;

    void *data;
    ...;
};

struct wlr_event_keyboard_key {
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
"""

# types/wlr_linux_dmabuf_v1.h
CDEF += """
struct wlr_linux_dmabuf_v1 *wlr_linux_dmabuf_v1_create(struct wl_display *display,
    struct wlr_renderer *renderer);
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

void wlr_matrix_projection(float mat[static 9], int width, int height,
    enum wl_output_transform transform);

void wlr_matrix_project_box(float mat[static 9], const struct wlr_box *box,
    enum wl_output_transform transform, float rotation,
    const float projection[static 9]);
"""

# types/wlr_output.h
CDEF += """
struct pixman_region32 {
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

    char name[24];
    char make[56];
    char model[16];
    char serial[16];
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

    bool needs_frame;
    bool frame_pending;
    float transform_matrix[9];

    struct wlr_output_state pending;

    struct {
        struct wl_signal frame;
        struct wl_signal damage;
        struct wl_signal needs_frame;
        struct wl_signal precommit;
        struct wl_signal commit;
        struct wl_signal present;
        struct wl_signal bind;
        struct wl_signal enable;
        struct wl_signal mode;
        struct wl_signal description;
        struct wl_signal destroy;
    } events;

    struct wl_event_source *idle_frame;
    struct wl_event_source *idle_done;

    int attach_render_locks; // number of locks forcing rendering

    struct wl_list cursors; // wlr_output_cursor::link
    struct wlr_output_cursor *hardware_cursor;
    int software_cursor_locks;

    struct wl_listener display_destroy;

    void *data;
    ...;
};

void wlr_output_enable(struct wlr_output *output, bool enable);
void wlr_output_create_global(struct wlr_output *output);
void wlr_output_destroy_global(struct wlr_output *output);

struct wlr_output_mode *wlr_output_preferred_mode(struct wlr_output *output);

void wlr_output_set_mode(struct wlr_output *output,
    struct wlr_output_mode *mode);

bool wlr_output_attach_render(struct wlr_output *output, int *buffer_age);
void wlr_output_effective_resolution(struct wlr_output *output,
    int *width, int *height);
bool wlr_output_commit(struct wlr_output *output);

void wlr_output_render_software_cursors(struct wlr_output *output,
    struct pixman_region32 *damage);

enum wl_output_transform wlr_output_transform_invert(
    enum wl_output_transform tr);
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

# types/wlr_pointer.h
CDEF += """
struct wlr_pointer {
    const struct wlr_pointer_impl *impl;

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
    } events;

    void *data;

    ...;
};

struct wlr_event_pointer_motion {
    struct wlr_input_device *device;
    uint32_t time_msec;
    double delta_x, delta_y;
    double unaccel_dx, unaccel_dy;
    ...;
};

struct wlr_event_pointer_motion_absolute {
    struct wlr_input_device *device;
    uint32_t time_msec;
    double x, y;
    ...;
};

struct wlr_event_pointer_button {
    struct wlr_input_device *device;
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
    ...
};

enum wlr_axis_orientation {
    WLR_AXIS_ORIENTATION_VERTICAL,
    WLR_AXIS_ORIENTATION_HORIZONTAL,
    ...
};

struct wlr_event_pointer_axis {
    struct wlr_input_device *device;
    uint32_t time_msec;
    enum wlr_axis_source source;
    enum wlr_axis_orientation orientation;
    double delta;
    int32_t delta_discrete;
    ...;
};

struct wlr_event_pointer_swipe_begin {
    struct wlr_input_device *device;
    uint32_t time_msec;
    uint32_t fingers;
    ...;
};

struct wlr_event_pointer_swipe_update {
    struct wlr_input_device *device;
    uint32_t time_msec;
    uint32_t fingers;
    double dx, dy;
    ...;
};

struct wlr_event_pointer_swipe_end {
    struct wlr_input_device *device;
    uint32_t time_msec;
    bool cancelled;
    ...;
};

struct wlr_event_pointer_pinch_begin {
    struct wlr_input_device *device;
    uint32_t time_msec;
    uint32_t fingers;
    ...;
};

struct wlr_event_pointer_pinch_update {
    struct wlr_input_device *device;
    uint32_t time_msec;
    uint32_t fingers;
    double dx, dy;
    double scale;
    double rotation;
    ...;
};

struct wlr_event_pointer_pinch_end {
    struct wlr_input_device *device;
    uint32_t time_msec;
    bool cancelled;
    ...;
};
"""

# types/wlr_seat.h
CDEF += """
struct timespec {
    int64_t tv_sec;
    int64_t tv_nsec;
    ...;
};
typedef int32_t clockid_t;
int clock_gettime(clockid_t clk_id, struct timespec *tp);

#define CLOCK_MONOTONIC ...

#define WLR_POINTER_BUTTONS_CAP 16

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
};

struct wlr_seat_request_set_selection_event {
    struct wlr_data_source *source;
    uint32_t serial;
};

struct wlr_seat_request_start_drag_event {
    struct wlr_drag *drag;
    struct wlr_surface *origin;
    uint32_t serial;
};

struct wlr_seat_pointer_focus_change_event {
    struct wlr_seat *seat;
    struct wlr_surface *old_surface, *new_surface;
    double sx, sy;
};

struct wlr_seat_keyboard_focus_change_event {
    struct wlr_seat *seat;
    struct wlr_surface *old_surface, *new_surface;
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

void wlr_seat_set_keyboard(struct wlr_seat *seat, struct wlr_input_device *dev);
struct wlr_keyboard *wlr_seat_get_keyboard(struct wlr_seat *seat);

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
bool wlr_seat_keyboard_has_grab(struct wlr_seat *seat);
"""

# types/wlr_surface.h
CDEF += """
struct wlr_surface_state {
    uint32_t committed;

    struct wl_resource *buffer_resource;
    int32_t dx, dy;
    struct pixman_region32 surface_damage, buffer_damage;
    struct pixman_region32 opaque, input;
    enum wl_output_transform transform;
    int32_t scale;
    struct wl_list frame_callback_list;

    int width, height;
    int buffer_width, buffer_height;

    struct wl_listener buffer_destroy;
    ...;
};

struct wlr_surface_role {
    const char *name;
    void (*commit)(struct wlr_surface *surface);
    void (*precommit)(struct wlr_surface *surface);
};

struct wlr_surface {
    struct wl_resource *resource;
    struct wlr_renderer *renderer;
    struct wlr_client_buffer *buffer;
    int sx, sy;
    struct pixman_region32 buffer_damage;
    struct pixman_region32 opaque_region;
    struct pixman_region32 input_region;
    struct wlr_surface_state current, pending, previous;

    const struct wlr_surface_role *role;
    void *role_data;

    struct {
        struct wl_signal commit;
        struct wl_signal new_subsurface;
        struct wl_signal destroy;
    } events;

    struct wl_list subsurfaces;
    struct wl_list subsurface_pending_list;
    struct wl_listener renderer_destroy;

    void *data;
    ...;
};

struct wlr_texture *wlr_surface_get_texture(struct wlr_surface *surface);

void wlr_surface_send_frame_done(struct wlr_surface *surface,
    const struct timespec *when);

typedef void (*wlr_surface_iterator_func_t)(struct wlr_surface *surface,
    int sx, int sy, void *data);

extern "Python" void surface_iterator_callback(struct wlr_surface *surface, int sx, int sy, void *data);
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

struct wlr_xdg_shell *wlr_xdg_shell_create(struct wl_display *display);

struct wlr_xdg_toplevel_state {
    bool maximized, fullscreen, resizing, activated;
    uint32_t tiled;
    uint32_t width, height;
    uint32_t max_width, max_height;
    uint32_t min_width, min_height;

    struct wlr_output *fullscreen_output;
    struct wl_listener fullscreen_output_destroy;
    ...;
};

struct wlr_xdg_toplevel {
    struct wl_resource *resource;
    struct wlr_xdg_surface *base;
    bool added;

    struct wlr_xdg_surface *parent;
    struct wl_listener parent_unmap;

    struct wlr_xdg_toplevel_state client_pending;
    struct wlr_xdg_toplevel_state server_pending;
    struct wlr_xdg_toplevel_state current;

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

    bool added, configured, mapped;
    uint32_t configure_serial;
    struct wl_event_source *configure_idle;
    uint32_t configure_next_serial;
    struct wl_list configure_list;

    bool has_next_geometry;
    struct wlr_box next_geometry;
    struct wlr_box geometry;

    struct wl_listener surface_destroy;
    struct wl_listener surface_commit;

    struct {
        struct wl_signal destroy;
        struct wl_signal ping_timeout;
        struct wl_signal new_popup;
        struct wl_signal map;
        struct wl_signal unmap;

        struct wl_signal configure; // wlr_xdg_surface_configure
        struct wl_signal ack_configure; // wlr_xdg_surface_configure
    } events;

    void *data;
    ...;
};

struct wlr_xdg_toplevel_move_event {
    struct wlr_xdg_surface *surface;
    struct wlr_seat_client *seat;
    uint32_t serial;
    ...;
};

struct wlr_xdg_toplevel_resize_event {
    struct wlr_xdg_surface *surface;
    struct wlr_seat_client *seat;
    uint32_t serial;
    uint32_t edges;
    ...;
};

struct wlr_xdg_toplevel_set_fullscreen_event {
    struct wlr_xdg_surface *surface;
    bool fullscreen;
    struct wlr_output *output;
    ...;
};

struct wlr_xdg_toplevel_show_window_menu_event {
    struct wlr_xdg_surface *surface;
    struct wlr_seat_client *seat;
    uint32_t serial;
    uint32_t x, y;
    ...;
};

void wlr_xdg_surface_ping(struct wlr_xdg_surface *surface);

uint32_t wlr_xdg_toplevel_set_size(struct wlr_xdg_surface *surface,
    uint32_t width, uint32_t height);
uint32_t wlr_xdg_toplevel_set_activated(struct wlr_xdg_surface *surface,
    bool activated);
uint32_t wlr_xdg_toplevel_set_maximized(struct wlr_xdg_surface *surface,
    bool maximized);
uint32_t wlr_xdg_toplevel_set_fullscreen(struct wlr_xdg_surface *surface,
    bool fullscreen);
uint32_t wlr_xdg_toplevel_set_resizing(struct wlr_xdg_surface *surface,
    bool resizing);
uint32_t wlr_xdg_toplevel_set_tiled(struct wlr_xdg_surface *surface,
    uint32_t tiled_edges);

void wlr_xdg_toplevel_send_close(struct wlr_xdg_surface *surface);
void wlr_xdg_popup_destroy(struct wlr_xdg_surface *surface);

struct wlr_surface *wlr_xdg_surface_surface_at(
    struct wlr_xdg_surface *surface, double sx, double sy,
    double *sub_x, double *sub_y);
bool wlr_surface_is_xdg_surface(struct wlr_surface *surface);

struct wlr_xdg_surface *wlr_xdg_surface_from_wlr_surface(
    struct wlr_surface *surface);

void wlr_xdg_surface_get_geometry(struct wlr_xdg_surface *surface,
    struct wlr_box *box);

void wlr_xdg_surface_for_each_surface(struct wlr_xdg_surface *surface,
    wlr_surface_iterator_func_t iterator, void *user_data);

void wlr_xdg_surface_for_each_popup_surface(struct wlr_xdg_surface *surface,
    wlr_surface_iterator_func_t iterator, void *user_data);
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

include_dir = (Path(__file__).parent.parent / "include").resolve()
assert include_dir.is_dir(), f"missing {include_dir}"

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
