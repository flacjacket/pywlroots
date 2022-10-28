Included Headers
----------------

Generated Wayland protocol headers that are included with the pywlroots ffi
build, and are shipped with the library for downstream libraries to be able to
include these headers.

Updating Headers
----------------

When protocol versions are updated or the wayland scanner generation changes,
the included headers should be updated as well.  The match between the latest
protocol and the included files is run in the CI.  When that starts to fail,
run:

```
wayland-scanner server-header /usr/share/wayland-protocols/path/to/file.xml wlroots/include/file.h
```
