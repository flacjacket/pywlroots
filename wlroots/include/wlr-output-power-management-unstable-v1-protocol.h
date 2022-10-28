/* Generated by wayland-scanner 1.21.0 */

#ifndef WLR_OUTPUT_POWER_MANAGEMENT_UNSTABLE_V1_SERVER_PROTOCOL_H
#define WLR_OUTPUT_POWER_MANAGEMENT_UNSTABLE_V1_SERVER_PROTOCOL_H

#include <stdint.h>
#include <stddef.h>
#include "wayland-server.h"

#ifdef  __cplusplus
extern "C" {
#endif

struct wl_client;
struct wl_resource;

/**
 * @page page_wlr_output_power_management_unstable_v1 The wlr_output_power_management_unstable_v1 protocol
 * Control power management modes of outputs
 *
 * @section page_desc_wlr_output_power_management_unstable_v1 Description
 *
 * This protocol allows clients to control power management modes
 * of outputs that are currently part of the compositor space. The
 * intent is to allow special clients like desktop shells to power
 * down outputs when the system is idle.
 *
 * To modify outputs not currently part of the compositor space see
 * wlr-output-management.
 *
 * Warning! The protocol described in this file is experimental and
 * backward incompatible changes may be made. Backward compatible changes
 * may be added together with the corresponding interface version bump.
 * Backward incompatible changes are done by bumping the version number in
 * the protocol and interface names and resetting the interface version.
 * Once the protocol is to be declared stable, the 'z' prefix and the
 * version number in the protocol and interface names are removed and the
 * interface version number is reset.
 *
 * @section page_ifaces_wlr_output_power_management_unstable_v1 Interfaces
 * - @subpage page_iface_zwlr_output_power_manager_v1 - manager to create per-output power management
 * - @subpage page_iface_zwlr_output_power_v1 - adjust power management mode for an output
 * @section page_copyright_wlr_output_power_management_unstable_v1 Copyright
 * <pre>
 *
 * Copyright © 2019 Purism SPC
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice (including the next
 * paragraph) shall be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 * </pre>
 */
struct wl_output;
struct zwlr_output_power_manager_v1;
struct zwlr_output_power_v1;

#ifndef ZWLR_OUTPUT_POWER_MANAGER_V1_INTERFACE
#define ZWLR_OUTPUT_POWER_MANAGER_V1_INTERFACE
/**
 * @page page_iface_zwlr_output_power_manager_v1 zwlr_output_power_manager_v1
 * @section page_iface_zwlr_output_power_manager_v1_desc Description
 *
 * This interface is a manager that allows creating per-output power
 * management mode controls.
 * @section page_iface_zwlr_output_power_manager_v1_api API
 * See @ref iface_zwlr_output_power_manager_v1.
 */
/**
 * @defgroup iface_zwlr_output_power_manager_v1 The zwlr_output_power_manager_v1 interface
 *
 * This interface is a manager that allows creating per-output power
 * management mode controls.
 */
extern const struct wl_interface zwlr_output_power_manager_v1_interface;
#endif
#ifndef ZWLR_OUTPUT_POWER_V1_INTERFACE
#define ZWLR_OUTPUT_POWER_V1_INTERFACE
/**
 * @page page_iface_zwlr_output_power_v1 zwlr_output_power_v1
 * @section page_iface_zwlr_output_power_v1_desc Description
 *
 * This object offers requests to set the power management mode of
 * an output.
 * @section page_iface_zwlr_output_power_v1_api API
 * See @ref iface_zwlr_output_power_v1.
 */
/**
 * @defgroup iface_zwlr_output_power_v1 The zwlr_output_power_v1 interface
 *
 * This object offers requests to set the power management mode of
 * an output.
 */
extern const struct wl_interface zwlr_output_power_v1_interface;
#endif

/**
 * @ingroup iface_zwlr_output_power_manager_v1
 * @struct zwlr_output_power_manager_v1_interface
 */
struct zwlr_output_power_manager_v1_interface {
	/**
	 * get a power management for an output
	 *
	 * Create a output power management mode control that can be used
	 * to adjust the power management mode for a given output.
	 */
	void (*get_output_power)(struct wl_client *client,
				 struct wl_resource *resource,
				 uint32_t id,
				 struct wl_resource *output);
	/**
	 * destroy the manager
	 *
	 * All objects created by the manager will still remain valid,
	 * until their appropriate destroy request has been called.
	 */
	void (*destroy)(struct wl_client *client,
			struct wl_resource *resource);
};


/**
 * @ingroup iface_zwlr_output_power_manager_v1
 */
#define ZWLR_OUTPUT_POWER_MANAGER_V1_GET_OUTPUT_POWER_SINCE_VERSION 1
/**
 * @ingroup iface_zwlr_output_power_manager_v1
 */
#define ZWLR_OUTPUT_POWER_MANAGER_V1_DESTROY_SINCE_VERSION 1

#ifndef ZWLR_OUTPUT_POWER_V1_MODE_ENUM
#define ZWLR_OUTPUT_POWER_V1_MODE_ENUM
enum zwlr_output_power_v1_mode {
	/**
	 * Output is turned off.
	 */
	ZWLR_OUTPUT_POWER_V1_MODE_OFF = 0,
	/**
	 * Output is turned on, no power saving
	 */
	ZWLR_OUTPUT_POWER_V1_MODE_ON = 1,
};
#endif /* ZWLR_OUTPUT_POWER_V1_MODE_ENUM */

#ifndef ZWLR_OUTPUT_POWER_V1_ERROR_ENUM
#define ZWLR_OUTPUT_POWER_V1_ERROR_ENUM
enum zwlr_output_power_v1_error {
	/**
	 * inexistent power save mode
	 */
	ZWLR_OUTPUT_POWER_V1_ERROR_INVALID_MODE = 1,
};
#endif /* ZWLR_OUTPUT_POWER_V1_ERROR_ENUM */

/**
 * @ingroup iface_zwlr_output_power_v1
 * @struct zwlr_output_power_v1_interface
 */
struct zwlr_output_power_v1_interface {
	/**
	 * Set an outputs power save mode
	 *
	 * Set an output's power save mode to the given mode. The mode
	 * change is effective immediately. If the output does not support
	 * the given mode a failed event is sent.
	 * @param mode the power save mode to set
	 */
	void (*set_mode)(struct wl_client *client,
			 struct wl_resource *resource,
			 uint32_t mode);
	/**
	 * destroy this power management
	 *
	 * Destroys the output power management mode control object.
	 */
	void (*destroy)(struct wl_client *client,
			struct wl_resource *resource);
};

#define ZWLR_OUTPUT_POWER_V1_MODE 0
#define ZWLR_OUTPUT_POWER_V1_FAILED 1

/**
 * @ingroup iface_zwlr_output_power_v1
 */
#define ZWLR_OUTPUT_POWER_V1_MODE_SINCE_VERSION 1
/**
 * @ingroup iface_zwlr_output_power_v1
 */
#define ZWLR_OUTPUT_POWER_V1_FAILED_SINCE_VERSION 1

/**
 * @ingroup iface_zwlr_output_power_v1
 */
#define ZWLR_OUTPUT_POWER_V1_SET_MODE_SINCE_VERSION 1
/**
 * @ingroup iface_zwlr_output_power_v1
 */
#define ZWLR_OUTPUT_POWER_V1_DESTROY_SINCE_VERSION 1

/**
 * @ingroup iface_zwlr_output_power_v1
 * Sends an mode event to the client owning the resource.
 * @param resource_ The client's resource
 * @param mode the output's new power management mode
 */
static inline void
zwlr_output_power_v1_send_mode(struct wl_resource *resource_, uint32_t mode)
{
	wl_resource_post_event(resource_, ZWLR_OUTPUT_POWER_V1_MODE, mode);
}

/**
 * @ingroup iface_zwlr_output_power_v1
 * Sends an failed event to the client owning the resource.
 * @param resource_ The client's resource
 */
static inline void
zwlr_output_power_v1_send_failed(struct wl_resource *resource_)
{
	wl_resource_post_event(resource_, ZWLR_OUTPUT_POWER_V1_FAILED);
}

#ifdef  __cplusplus
}
#endif

#endif
