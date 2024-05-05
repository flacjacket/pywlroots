0.16.8 -- 2024-05-04
--------------------
* Fixed: ``XdgTopLevel.parent`` always returnd a parent even if the parent is NULL.
* Fixed return type of ``Seat.touch_notify_down``: Returns an integer now (the
  serial identifier)
* Added support for ``wlr_switch``
* Added ``Seat.touch_send_*`` methods
* Added ``TouchPoint`` class
* Real support for ``wlr_touch``. The previous implementations were not usable. 


0.16.7 -- 2024-04-16
--------------------
* Added support for the 
  `Single-pixel buffer <https://wayland.app/protocols/single-pixel-buffer-v1>`_ 
  protocol.
* Added (experimental) support for the 
  `Session lock V1 <https://wayland.app/protocols/ext-session-lock-v1>`_
  protocol
* Added ``Output.enable_adaptive_sync(bool)``
* Added ``Cursor.detach_input_device()``
* Added ``Backend.is_multi`` property which indicates if the backend represents
  a multi-backend
* Added ``Pointer.data`` property
* Added support for ``wlr_touch``
* Added support for ``OutputState`` which simplifies the configuration of 
  ``Output``
* Removed ``Seat.has_grab()``: Use the explicit methods like
  ``Seat.keyboard_has_grab()``, ``Seat.pointer_has_grab()`` or 
  ``Seat.touch_has_grab()``
* Renamed the touch events to maintain a consistent naming scheme:
  ``TouchEventUp`` -> ``TouchUpEvent``, ``TouchEventDown`` -> ``TouchDownEvent``,
  ``TouchEventMotion`` -> ``TouchMotionEvent``, 
  ``TouchEventCancel`` -> ``TouchCancelEvent``
* The following methods don't throw a ``RuntimeError`` anymore, but return a 
  boolean value like the wlroots API: ``Backend.start()``, ``Output.commit()``,
  and ``SceneOutput.commit()``
* Deprecated ``Seat.set_keyboard()``: Use the ``Seat.keyboard`` property
* ``Seat.keyboard`` (and ``Seat.set_keyboard()``) accepts ``None`` as valid value.


0.16.6 -- 2023-10-08
--------------------
* Add missing include
  implemented by `VladislavGrudinin <https://github.com/VladislavGrudinin>`_
  (PR `#127 <https://github.com/flacjacket/pywlroots/pull/127>`_)
* Update to include CPython 3.12 and PyPy in CI and release
  implemented by `Sean Vig <https://github.com/flacjacket>`_ 
  (PR `#128 <https://github.com/flacjacket/pywlroots/pull/128>`_)


0.16.5 -- 2023-09-11
--------------------
* Update wlroots url in ``README.rst``
  implemented by `cooki35 <https://github.com/cooki35>`_
  (PR `#124 <https://github.com/flacjacket/pywlroots/pull/124>`_)
* Expose ``wlr_keyboard_notify_modifiers`` function
  implemented by `Charbel Assaad <https://github.com/Sydiepus>`_
  (PR `#123 <https://github.com/flacjacket/pywlroots/pull/123>`_)
* Migrated to use PEP 517 compatible release process


0.16.4 -- 2023-04-08
--------------------
* Added idle_notify_v1 protocol
  implemented by `Charbel Assaad <https://github.com/Sydiepus>`_
  (PR `#118 <https://github.com/flacjacket/pywlroots/pull/118>`_)


0.16.3 -- 2023-03-23
--------------------
* Add helpers for XDG activation V1 and presentation time protocols
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#117 <https://github.com/flacjacket/pywlroots/pull/117>`_)


0.16.2 -- 2023-03-18
--------------------
* Add helpers for mapping input devices to outputs
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#116 <https://github.com/flacjacket/pywlroots/pull/116>`_)


0.16.1 -- 2023-02-21
--------------------
* Minor keyboard handling improvements
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#114 <https://github.com/flacjacket/pywlroots/pull/114>`_)
* Ensure xwayland is built in released wheels
  implemented by `Sean Vig <https://github.com/flacjacket>`_ 
  (PR `#115 <https://github.com/flacjacket/pywlroots/pull/115>`_)


0.16.0 -- 2023-02-20
--------------------
* Support for wlroots 0.16.x
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#109 <https://github.com/flacjacket/pywlroots/pull/109>`_)


0.15.24 -- 2022-10-29
---------------------
* Drag.icon can also return ``None`` if clients don't provide icons to render
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#107 <https://github.com/flacjacket/pywlroots/pull/107>`_)


0.15.23 -- 2022-10-28
---------------------
* Add handlers for ``wlr_pointer_gestures_v1``
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#106 <https://github.com/flacjacket/pywlroots/pull/106>`_)


0.15.22 -- 2022-09-20
---------------------
* Add method to ``XCursorManager`` for ``wlr_xcursor_manager_load``
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#104 <https://github.com/flacjacket/pywlroots/pull/104>`_)
* Bump libdrm version to 2.4.113 in CI to fix build agaist wlroots master
  implemented by `Sean Vig <https://github.com/flacjacket>`_ 
  (PR `#105 <https://github.com/flacjacket/pywlroots/pull/105>`_)


0.15.21 -- 2022-09-08
---------------------
* Add signals for ``wlr_input_device`` events
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#101 <https://github.com/flacjacket/pywlroots/pull/101>`_)
* Fix up some output code
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#102 <https://github.com/flacjacket/pywlroots/pull/102>`_)
* Add wlr_xdg_surface_schedule_configure as XdgSurface method
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#103 <https://github.com/flacjacket/pywlroots/pull/103>`_)


0.15.20 -- 2022-08-20
---------------------
* Bump libdrm and wayland protocols in CI
  implemented by `Sean Vig <https://github.com/flacjacket>`_ 
  (PR `#100 <https://github.com/flacjacket/pywlroots/pull/100>`_)
* Correct 2 enums to be IntFlags, supporting 0s
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#99 <https://github.com/flacjacket/pywlroots/pull/99>`_)


0.15.19 -- 2022-07-24
---------------------
* Added support for ``wlr_viewporter``
  implemented by `Aakash Sen Sharma <https://github.com/Shinyzenith>`_
  (PR `#94 <https://github.com/flacjacket/pywlroots/pull/94>`_)
* Wrap input inhibitor active client in pywayland Client
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#98 <https://github.com/flacjacket/pywlroots/pull/98>`_)


0.15.18 -- 2022-06-27
---------------------
* Build wlroots wheels for new releases 
  implemented by `Sean Vig <https://github.com/flacjacket>`_ 
  (PR `#90 <https://github.com/flacjacket/pywlroots/pull/89>`_)
* improve SIGINT handler
  implemented by `Aakash Sen Sharma <https://github.com/Shinyzenith>`_
  (PR `#91 <https://github.com/flacjacket/pywlroots/pull/90>`_)
* Expose input inhibitor activate/deactivate events
  implemented by `Matt Colligan <https://github.com/m-col>`_
  (PR `#92 <https://github.com/flacjacket/pywlroots/pull/92>`_)


0.15.17 -- 2022-06-06
---------------------
* Merged pull request `#89 <https://github.com/flacjacket/pywlroots/pull/89>`_:
  [import] export_dmabuf and virtual_pointer support
  implemented by `Aakash Sen Sharma <https://github.com/Shinyzenith>`_


0.15.16 -- 2022-06-05
---------------------
* Merged pull request `#88 <https://github.com/flacjacket/pywlroots/pull/88>`_:
  [protocol] wlr_export_dmabuf_v1 bindings added
  implemented by `Aakash Sen Sharma <https://github.com/Shinyzenith>`_


0.15.15 -- 2022-05-28
---------------------
* Merged pull request `#86 <https://github.com/flacjacket/pywlroots/pull/86>`_:
  Add wlr_virtual_pointer_v1 interface 
  implemented by `Matt Colligan <https://github.com/m-col>`_


0.15.14 -- 2022-05-16
---------------------
* Merged pull request `#85 <https://github.com/flacjacket/pywlroots/pull/85>`_:
  Added proper support for primary selection
  implemented by `Antonín Říha <https://github.com/anriha>`_


0.15.13 -- 2022-04-18
---------------------
* Merged pull request `#84 <https://github.com/flacjacket/pywlroots/pull/84>`_:
  Expose xcursors to enable setting xwayland cursor images
  implemented by `Matt Colligan <https://github.com/m-col>`_

0.15.12 -- 2022-04-15
---------------------
* Merged pull request `#83 <https://github.com/flacjacket/pywlroots/pull/83>`_:
  XWayland surface restack sibling is optional
  implemented by `Matt Colligan <https://github.com/m-col>`_


0.15.11 -- 2022-03-16
---------------------
* Merged pull request `#81 <https://github.com/flacjacket/pywlroots/pull/81>`_:
  Catch OSErrors triggered by ffi_build.py version check
  implemented by `Matt Colligan <https://github.com/m-col>`_


0.15.10 -- 2022-02-23
---------------------
* Merged pull request `#79 <https://github.com/flacjacket/pywlroots/pull/79>`_:
  Don't wrap IdleInhibitorV1's destroy event data
  implemented by `Matt Colligan <https://github.com/m-col>`_


0.15.9 -- 2022-02-19
--------------------
* Get build-time information from local files


0.15.8 -- 2022-02-13
--------------------
* Skip version check in ffi_build if unable to create file (which is a sign of
  using a system installed version of the library)


0.15.7 -- 2022-02-03
--------------------
* Added support for idle_inhibitor


0.15.6 -- 2022-02-02
--------------------
* Added idle protocol


0.15.5 -- 2022-02-02
--------------------
* Added support for output power management protocol


0.15.4 -- 2022-01-31
--------------------
* Add header files to be included in package for use in downstream CFFI packages.


0.15.3 -- 2022-01-22
--------------------
* Add destroy method to XWayland


0.15.2 -- 2022-01-21
--------------------
* Add XWayland support functionality.


0.15.1 -- 2022-01-17
--------------------
* Fixes problem with annotations


0.15.0 -- 2022-01-11
--------------------
* Support wlroots 0.15
  The latest release of wlroots brings with it a new scene graph API as well 
  as changes to the backend and renderer interfaces, all of which should make
  it much easier to do proper handling of rendering and damage tracking, as
  well as simplify some of the handling that was needed for showing windows
  in the outputs. There are also minor changes to the handling of boxes,
  surfaces, and other wlroots primitives. The basic tiny compositor is updated 
  with some of this functionality, but expect further pywlroots releases to
  make use of all the wlroots 0.15 features
* Additional breaking changes: Python 3.6 has hit EOL, so this version is no 
  longer supported.


0.14.12 -- 2022-01-10
---------------------
* Handle invalid UTF-8 string members


0.14.11 -- 2021-11-20
---------------------
* Fix packaging and installation issue.


0.14.10 -- 2021-11-14
---------------------
* Add some handlers for wlr_foreign_toplevel_management_v1


0.14.9 -- 2021-10-20
--------------------
* Add some touch event handling to the seat


0.14.8 -- 2021-10-17
--------------------
* Add interface for wlr_drag and related objects


0.14.7 -- 2021-10-07
--------------------
* Add wlr_input_inhibit_manager for screen locking, implemented
  by `Graeme Holliday <https://github.com/Graeme22>`_


0.14.6 -- 2021-09-24
--------------------
* Fix typo


0.14.5 -- 2021-09-21
--------------------
* Redirect internal Box import to avoid deprecation warning on correctly used
  imports
* Add ``wlr_relative_pointer_v1``


0.14.4 -- 2021-09-17
--------------------
* Update Box type to be more in line with 0.15 and add deprecation.
* Add ``closest_point`` and ``__repr__`` for Box
* Add wlr_xdg_surface_configure and corresponding events
* Add wlr_pointer_constraints_v1


0.14.3 -- 2021-07-18
--------------------
* Update source package to include tests and example tiny compositor.


0.14.2 -- 2021-07-09
--------------------
* Let ``wlr_output_layout_get_box`` return extents of whole layout.
* Add is_headless properties to Output and Backend.
* Reduce severity of wlroots version mismatch, just print error at build time 
  rather than failing.


0.14.1 -- 2021-07-07
--------------------
* Add check for compatible wlroots version, should be run on install.


0.13.6 -- 2021-07-07
--------------------
* Add check for compatible wlroots version, should be run on install.


0.14.0 -- 2021-06-26
--------------------
* Fix compatibility with wlroots 0.14.


0.13.5 -- 2021-06-13
--------------------
* Expose input device properties


0.13.4 -- 2021-06-11
--------------------
* Add parent method to xdg-shell toplevels
* Add ``wlr_data_control_v1`` interface


0.13.3 -- 2021-06-02
--------------------
* Add ``wlr_primary_selection_v1``
* Add str_or_none helper to better decode ffi char strings
* Expose libinput handles
* Fixes: Fix wlroots version and remove ``wl_shm_format`` enum


0.13.2 -- 2021-05-28
--------------------
* Add subsurfaces


0.13.1 -- 2021-05-23
--------------------
* Add keyboard destroyed property
* Add texture handling functionality
* Add server decoration manager


0.13.0 -- 2021-05-15
--------------------
* Changed versioning scheme: Releases will be versioned where the major and 
  minor version of pywlroots will match the version of wlroots that is supported. 
  The patch version of pywlroots will be incremented for various additions, 
  changes, and bug fix versions to support the designated wlroots version.
* Bug fix for ``set_custom_mode``


0.2.9 -- 2021-05-15
-------------------
* Add wlr output managment


0.2.8 -- 2021-05-08
-------------------
* Add output damage tracking functionality.


0.2.7 -- 2021-05-01
-------------------
* Add some more wlroots interfaces and modify the API for creating Compositors 
  and associated Backend and Renderer objects.


0.2.6 -- 2021-04-25
-------------------
* Add check to see if a surface is an XDG surface, and check it before returning 
  the surface.


0.2.5 -- 2021-04-24
-------------------
* Lots of new wlroots functionality and interfaces bound.


0.2.4 -- 2021-04-23
-------------------
* More bug fixes still.


0.2.3 -- 2021-04-23
-------------------
* Bug fix release with typo fix.


0.2.2 -- 2021-04-22
-------------------
* Bug fix release with even more fixes for wlroots 0.13.


0.2.1 -- 2021-04-22
-------------------
* Bugfix release with additional fixes for wlroots 0.13.


0.2.0 -- 2021-04-17
-------------------
* Updates to run on wlroots v0.13.
* Add an example compositor that shows some basic functionality of pywlroots.
* Add many additional functions and bindings to support basic compositor 
  functionality.


0.1.3 -- 2020-07-20
-------------------
* Updates to work with wlroots 0.11.0


0.1.2 -- 2020-06-28
-------------------
* Fixes to the 0.1.0 release to improve packaging and installation.


0.1.0 -- 2020-06-28
-------------------
Initial release
