# Copyright (c) 2022 Aakash Sen Sharma

from pywayland.server import Display, Signal
from wlroots import PtrHasData, ffi, lib
from wlroots.backend import Backend
from wlroots.wlr_types import Output, Surface


class PresentationEvent(PtrHasData):
    def __init__(self, ptr) -> None:
        self._ptr = ptr

    def from_output(self, output_event: OutputEventPresent) -> None:
        lib.wlr_presentation_event_from_output(self._ptr, output_event._ptr)

    @property
    def output(self) -> Output | None:
        if self._ptr.output == ffi.NULL:
            return None
        return Output(self._ptr.output)

    @property
    def tv_sec(self) -> int:
        return self._ptr.tv_sec

    @property
    def tv_nsec(self) -> int:
        return self._ptr.tv_nsec

    @property
    def refresh(self) -> int:
        return self._ptr.refresh

    @property
    def seq(self) -> int:
        return self._ptr.seq

    @property
    def flags(self) -> int:
        return self._ptr.flags


class PresentationFeedback(PtrHasData):
    def __init__(self, ptr) -> None:
        self._ptr = ptr

    def destroy(self) -> None:
        lib.wlr_presentation_feedback_destroy(self._ptr)

    def send_presented(self, event: PresentationEvent) -> None:
        lib.wlr_presentation_feedback_send_presented(self._ptr, event._ptr)

    @property
    def output(self) -> Output:
        return Output(self._ptr.output)

    @property
    def output_comitted(self) -> bool:
        return self._ptr.output_comitted

    @property
    def output_commit_seq(self) -> int:
        return self._ptr.output_commit_seq


class Presentation(PtrHasData):
    def __init__(self, display: Display, backend: Backend) -> None:
        """A `struct wlr_presentation`

        :param display:
            The wayland display
        """

        self._ptr = lib.wlr_presentation_create(display._ptr, backend._ptr)
        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))

    def surface_sampled(self, surface: Surface) -> PresentationFeedback:
        return PresentationFeedback(
            lib.wlr_presentation_surface_sampled(self._ptr, surface._ptr)
        )

    def surface_sampled_on_output(self, surface: Surface, output: Output) -> None:
        lib.wlr_presentation_surface_sampled_on_output(
            self._ptr, surface._ptr, output._ptr
        )

    def destroy(self) -> None:
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    @property
    def clock(self) -> int:
        return self._ptr.clock
