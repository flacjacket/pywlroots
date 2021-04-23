from wlroots import ffi, lib, Ptr


class PtrT(Ptr):
    def __init__(self, ptr):
        self._ptr = ptr


def test_binding():
    assert ffi is not None
    assert lib is not None


def test_ptr():
    ptr1 = ffi.new("struct wlr_box *")
    ptr2 = ffi.new("struct wlr_box *")

    box1 = PtrT(ptr1)
    box2 = PtrT(ptr1)

    assert box1 == box2
    assert hash(box1) != hash(box2)

    box1 = PtrT(ptr1)
    box2 = PtrT(ptr2)

    assert box1 != box2
    assert hash(box1) != hash(box2)
