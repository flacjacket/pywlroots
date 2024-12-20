# Copyright Sean Vig (c) 2020

from __future__ import annotations

from wlroots import Ptr, ffi, lib


class Timespec(Ptr):
    def __init__(self, ptr) -> None:
        """A wrapper aronud a timespec struct"""
        self._ptr = ptr

    @staticmethod
    def get_monotonic_time() -> Timespec:
        """Get the current monotonic time"""
        timespec = ffi.new("struct timespec *")
        ret = lib.clock_gettime(lib.CLOCK_MONOTONIC, timespec)
        if ret != 0:
            raise RuntimeError("Failed to get clock")
        return Timespec(timespec)

    @property
    def sec(self) -> int:
        """Whole seconds of designated time"""
        return self._ptr.tv_sec

    @property
    def nsec(self) -> int:
        """Nanoseconds in designated time"""
        return self._ptr.tv_nsec

    @property
    def time(self) -> float:
        """The designated time in seconds"""
        return self.sec + self.nsec * 1e-9

    def __str__(self) -> str:
        """String representation of timespec"""
        return f"Timespec({self.sec}, {self.nsec})"
