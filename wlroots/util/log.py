# Copyright (c) Sean Vig 2019

import logging

from wlroots import ffi, lib


logger = logging.getLogger("wlroots")


@ffi.def_extern()
def log_func_callback(importance: int, formatted_str) -> None:
    """Callback that logs the string at the given level"""
    log_str = ffi.string(formatted_str).decode()
    if importance == lib.WLR_ERROR:
        logger.error(log_str)
    elif importance == lib.WLR_INFO:
        logger.info(log_str)
    elif importance == lib.WLR_DEBUG:
        logger.debug(log_str)


def log_init(log_level: int) -> None:
    """Setup the wlroots logger to the specified level

    :param log_level:
        The log level to set the Python logger to for the wlroots library and
        the pywlroots bindings.
    """
    logger.setLevel(log_level)

    if log_level <= logging.DEBUG:
        wlr_log_level = lib.WLR_DEBUG
    elif log_level <= logging.INFO:
        wlr_log_level = lib.WLR_INFO
    elif log_level <= logging.ERROR:
        wlr_log_level = lib.WLR_ERROR
    else:
        wlr_log_level = lib.WLR_SILENT

    lib.wrapped_log_init(wlr_log_level, lib.log_func_callback)
