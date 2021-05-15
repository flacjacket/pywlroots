pywlroots
=========

|ci|

A Python binding to the `wlroots`_ library using cffi.  The library uses
`pywayland`_ to provide the Wayland bindings and `python-xkbcommon`_ to provide
wlroots keyboard functionality.

.. _python-xkbcommon: https://github.com/sde1000/python-xkbcommon
.. _pywayland: https://pywayland.readthedocs.io/en/latest/
.. _wlroots: https://github.com/swaywm/wlroots

Installation
------------

The library can be installed from the packaged PyPI releases, which will pull
in all of the necessary Python dependencies.  In addition to the Python
dependencies, pywlroots requires the wlroots and xkbcommon libraries and
headers to be installed.  At installation time, the cffi binding is compiled
against these libraries.

To build pywlroots from source, the Python requirements will need to be
installed manually.  These are available in ``requirements.txt``.  The cffi
bindings are built by running ``python wlroots/ffi_build.py``.

Versioning and Releases
-----------------------

Released versions of pywlroots are published to `PyPI`_.

The major and minor versions of pywlroots denote the version of wlroots that it
is compatibile with.  The pywlroots patch version will denote changes and fixes
on the given wlroots version.

 .. _PyPI: https://pypi.org/project/pywlroots/

.. |ci| image:: https://github.com/flacjacket/pywlroots/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/flacjacket/pywlroots/actions/workflows/ci.yml
    :alt: Build Status
