from .vector3 import Vector3
import numpy as np


class PinholeCameraModel:
    def __init__(self, p, t):
        self._projection: np.ndarray = np.eye(3, dtype=np.float32) if p is None else p
        assert(self._projection.shape == (3, 3))
        self._transform:  np.ndarray = np.ones((3, 4,), dtype=np.float32) if t is None else t
        assert(self._transform.shape == (3, 4))
        self._i_projection: np.ndarray = np.linalg.inv(self._projection)

    @property
    def position(self) -> Vector3:
        return Vector3(self._transform[0, 3], self._transform[1, 3], self._transform[2, 3])

    @property
    def front(self) -> Vector3:
        return Vector3(self._transform[0, 2], self._transform[1, 2], self._transform[2, 2])

    @property
    def up(self) -> Vector3:
        return Vector3(self._transform[0, 1], self._transform[1, 1], self._transform[2, 1])

    @property
    def right(self) -> Vector3:
        return Vector3(self._transform[0, 0], self._transform[1, 0], self._transform[2, 0])

    @position.setter
    def position(self, pos: Vector3) -> None:
        self._transform[0, 3], self._transform[1, 3], self._transform[2, 3] = pos[0], pos[1], pos[2]

    @property
    def transform(self) -> np.ndarray:
        return self._transform

    @property
    def projection(self) -> np.ndarray:
        return self._transform

    @property
    def inv_proj(self) -> np.ndarray:
        return self._i_projection

    @property
    def cx(self) -> float:
        return self._transform[0, 2]

    @property
    def cy(self) -> float:
        return self._transform[1, 2]

    @property
    def fx(self) -> float:
        return self._transform[0, 0]

    @property
    def fy(self) -> float:
        return self._transform[1, 1]

    @cx.setter
    def cx(self, val: float) -> None:
        self._transform[0, 2] = val

    @cy.setter
    def cy(self, val: float) -> None:
        self._transform[1, 2] = val

    @fx.setter
    def fx(self, val: float) -> None:
        self._transform[0, 0] = val

    @fy.setter
    def fy(self, val: float) -> None:
        self._transform[1, 1] = val

    def project(self, pos: Vector3) -> Vector3:
        x, y, z = pos.x, pos.y, pos.z
        tx = self.transform[0, 0] * x + self.transform[0, 1] * y + self.transform[0, 2] * z + self.transform[0, 3]
        ty = self.transform[1, 0] * x + self.transform[1, 1] * y + self.transform[1, 2] * z + self.transform[1, 3]
        tz = self.transform[2, 0] * x + self.transform[2, 1] * y + self.transform[2, 2] * z + self.transform[2, 3]
        return Vector3(self.projection[0, 0] * tx + self.projection[0, 1] * ty + self.projection[0, 2] * tz,
                       self.projection[1, 0] * tx + self.projection[1, 1] * ty + self.projection[1, 2] * tz,
                       self.projection[2, 0] * tx + self.projection[2, 1] * ty + self.projection[2, 2] * tz)

    def unproject(self, pos: Vector3) -> Vector3:
        x, y, z = pos.x, pos.y, pos.z
        tx = self.inv_proj[0, 0] * x + self.inv_proj[0, 1] * y + self.inv_proj[0, 2] * z + self.inv_proj[0, 3] - \
             self.transform[0, 3]
        ty = self.inv_proj[1, 0] * x + self.inv_proj[1, 1] * y + self.inv_proj[1, 2] * z + self.inv_proj[1, 3] - \
             self.transform[1, 3]
        tz = self.inv_proj[2, 0] * x + self.inv_proj[2, 1] * y + self.inv_proj[2, 2] * z + self.inv_proj[2, 3] - \
             self.transform[2, 3]

        return Vector3(self.transform[0, 0] * tx + self.transform[1, 0] * ty + self.transform[2, 0] * tz,
                       self.transform[0, 1] * tx + self.transform[1, 1] * ty + self.transform[2, 1] * tz,
                       self.transform[0, 2] * tx + self.transform[1, 2] * ty + self.transform[2, 2] * tz)

    def look_at(self, target: Vector3, eye: Vector3, up: Vector3) -> None:
        z_axis = (target - eye).normalized()  # The "forward" vector.
        x_axis = Vector3.cross(up, z_axis).normalized()  # The "right" vector.
        y_axis = Vector3.cross(x_axis, z_axis)  # The "up" vector.

        self.transform[0, 0] = x_axis.x
        self.transform[1, 0] = x_axis.y
        self.transform[2, 0] = x_axis.z

        self.transform[0, 1] = y_axis.x
        self.transform[1, 1] = y_axis.y
        self.transform[2, 1] = y_axis.z

        self.transform[0, 2] = z_axis.x
        self.transform[1, 2] = z_axis.y
        self.transform[2, 2] = z_axis.z

        self.transform[0, 3] = eye.x
        self.transform[1, 3] = eye.y
        self.transform[2, 3] = eye.z
