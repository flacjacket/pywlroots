Protocol Headers
----------------

Dynamically generated Wayland and wlroots protocol headers that are included
with the pywlroots ffi build, and are automatically generated when running
``python wlroots/ffi_build.py``. You can generate them manually by running:

.. code-block::

    python check_headers.py --generate

Updating Protocols
------------------

When protocol versions are updated, the included protocols XML files should
be updated as well. The match between the latest protocol and the generated
headers is run in the CI.  When that starts to fail, update the corresponding
XML file in ``wlroots/protocol`` with the one in the `wlroots repository
<https://gitlab.freedesktop.org/wlroots/wlroots>`_.
