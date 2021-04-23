# Copyright Sean Vig (c) 2020

from pywayland.protocol.wayland import WlOutput

from wlroots import ffi, lib, Ptr
from .box import Box


class Matrix(Ptr):
    def __init__(self, ptr) -> None:
        """A matrix which encodes transformations used for rendering"""
        self._ptr = ptr

    @classmethod
    def identity(cls) -> "Matrix":
        """An identity matrix"""
        mat_ptr = cls._build_matrix_ptr()
        lib.wlr_matrix_identity(mat_ptr)
        return Matrix(mat_ptr)

    @classmethod
    def projection(
        cls, width: int, height: int, transform: WlOutput.transform
    ) -> "Matrix":
        """A 2d orthographic projection matrix of (width, height) with specified transform"""
        mat_ptr = cls._build_matrix_ptr()
        lib.wlr_matrix_projection(mat_ptr, width, height, transform)
        return Matrix(mat_ptr)

    @classmethod
    def project_box(
        cls,
        box: Box,
        transform: WlOutput.transform,
        rotation: float,
        projection: "Matrix",
    ) -> "Matrix":
        """Project the specified box onto a orthographic projection with a rotation"""
        mat_ptr = cls._build_matrix_ptr()
        lib.wlr_matrix_project_box(
            mat_ptr, box._ptr, transform, rotation, projection._ptr
        )
        return Matrix(mat_ptr)

    def transpose(self) -> "Matrix":
        """Transpose the matrix"""
        mat_ptr = self._build_matrix_ptr()
        lib.wlr_matrix_transpose(mat_ptr, self._ptr)
        return Matrix(mat_ptr)

    def translate(self, x: float, y: float) -> None:
        """A 2d translation matrix of magnitude (x,y)"""
        lib.wlr_matrix_translate(self._ptr, x, y)

    def scale(self, x: float, y: float) -> None:
        """A 2d scale matrix of magnitude (x,y)"""
        lib.wlr_matrix_scale(self._ptr, x, y)

    def rotate(self, rad: float) -> None:
        """A 2d rotation of angle rad"""
        lib.wlr_matrix_rotate(self._ptr, rad)

    def transform(self, transform: WlOutput.transform) -> None:
        """Apply the given transformation to the matrix"""
        lib.wlr_matrix_transform(self._ptr, transform)

    def __matmul__(self, other: "Matrix") -> "Matrix":
        """Perform matrix multiplication with given matrix"""
        mat_ptr = self._build_matrix_ptr()
        lib.wlr_matrix_multiply(mat_ptr, self._ptr, other._ptr)
        return Matrix(mat_ptr)

    def __str__(self) -> str:
        """String representation showing the matrix"""
        matrix_values = list(self._ptr)
        return (
            f"Matrix([{matrix_values[:3]}, {matrix_values[3:6]}, {matrix_values[6:]}])"
        )

    @staticmethod
    def _build_matrix_ptr():
        return ffi.new("float [9]")
