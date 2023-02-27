from accelerometer_settings import load_accelerometer_settings, save_accelerometer_settings
from accelerometer_core.accelerometer import Accelerometer
from accelerometer_core.utilities import Vector3, Matrix4
from accelerometer_core.utilities import LoopTimer
from accelerometer_core import GRAVITY_CONSTANT
import math


class IMU:
    def __init__(self, forward: Vector3 = None):
        self._accelerometer: Accelerometer
        try:
            self._accelerometer = Accelerometer()
        except RuntimeError as err:
            print(err.args)
            exit(0)
        self.calibrate(20, forward)

        if not load_accelerometer_settings(self._accelerometer, "accel_settings.json"):
            self.calibrate(10)
            save_accelerometer_settings(self._accelerometer, "accel_settings.json")
        else:
            self._accelerometer.start_up()

        self._k_gravity = 0.9995
        self._k_angle   = 0.9995
        # TODO connection to accelerometer check...
        self._timer: LoopTimer = LoopTimer(0.001)

        self._v_ang: Vector3 = self._accelerometer.ang_velocity  # Vector3(0.0, 0.0, 0.0)
        self._accel: Vector3 = self._accelerometer.acceleration  # Vector3(0.0, 0.0, 0.0)

        self._ang: Vector3 = self._accelerometer.start_ang_values  # Vector3(0.0, 0.0, 0.0)
        self._vel: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._pos: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._basis: Matrix4 = Matrix4.build_basis(self._accel, forward)

    @property
    def k_gravity(self) -> float:
        return self._k_gravity

    @property
    def k_angle(self) -> float:
        return self._k_angle
        
    @k_gravity.setter
    def k_gravity(self, val: float) -> None:
        self._k_gravity = min(max(0.0, val), 1.0)

    @k_angle.setter
    def k_angle(self, val: float) -> None:
        self._k_angle = min(max(0.0, val), 1.0)
     
    @property
    def angles_velocity(self) -> Vector3:
        return self._accelerometer.ang_velocity

    @property
    def angles(self) -> Vector3:
        return self._ang

    @property
    def acceleration(self) -> Vector3:
        return self._accel

    @property
    def velocity(self) -> Vector3:
        return self._vel

    @property
    def position(self) -> Vector3:
        return self._pos

    @property
    def delta_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self.curr_t - self.prev_t

    @property
    def curr_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self._accelerometer.curr_t

    @property
    def prev_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self._accelerometer.prev_t

    def calibrate(self, timeout: float, forward: Vector3 = None) -> None:
        self._accelerometer.calibrate(timeout, forward)
        self._ang = self._accelerometer.start_ang_values

    def read(self) -> bool:
        with self._timer:
            if not self._accelerometer.read_accel_measurements():
                return False
            accel = self._accelerometer.acceleration
            omega = self._accelerometer.ang_velocity
            dt    = self._accelerometer.delta_t
            # r: Vector3 = (basis.right + Vector3.cross(omega, basis.right) * dt).normalized()
            # комплиментарная фильтрация и привязка u к направлению g
            u: Vector3 = (self._basis.up + Vector3.cross(omega, self._basis.up) * dt).normalized() * \
                         self.k_gravity + (1.0 - self.k_gravity) * accel
            f: Vector3 = (self._basis.front + Vector3.cross(omega, self._basis.front) * dt).normalized()
            r = Vector3.cross(f, u).normalized()
            f = Vector3.cross(u, r).normalized()
            # получим ускорение в мировой системе координат за вычетом ускорения свободного падения
            a: Vector3 = Vector3(r.x * accel.x + r.y * accel.y + r.z * accel.z,
                                 u.x * accel.x + u.y * accel.y + u.z * accel.z - GRAVITY_CONSTANT,
                                 f.x * accel.x + f.y * accel.y + f.z * accel.z)
            # комплиментарная фильтрация угла с направлением g
            self._ang += self._ang + omega * dt
            g_angles = Vector3(math.pi + math.atan2(accel.z, accel.z),
                               math.pi + math.atan2(accel.y, accel.z),
                               math.pi + math.atan2(accel.y, accel.x))
            self._ang = self.k_angle * self._ang + (1.0 - self.k_angle) * g_angles
            # интегрирование скорости
            self._vel += self._vel + a * dt
            # интегрирование пути
            self._pos += self._pos + self._vel * dt

        return True
