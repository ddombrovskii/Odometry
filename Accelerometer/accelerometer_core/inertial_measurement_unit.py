from settings_io import load_accelerometer_settings, save_accelerometer_settings
from accelerometer_core.accelerometer import Accelerometer
from accelerometer_core.utilities import Vector3, Matrix4, Quaternion
from accelerometer_core.utilities import LoopTimer
import sys

CALIBRATION_MODE   = 0
BASIS_COMPUTE_MODE = 1
INTEGRATE_MODE     = 2
STOP_MODE          = 3
WARM_UP_MODE       = 4


class IMU:
    def __init__(self, forward: Vector3 = None):
        self._accelerometer: Accelerometer
        try:
            self._accelerometer = Accelerometer()
        except RuntimeError as err:
            print(err.args)
            exit(0)
        # self.calibrate(20, forward)
        # if not load_accelerometer_settings(self._accelerometer, "accel_settings.json"):
        #    self.calibrate(10)
        #    save_accelerometer_settings(self._accelerometer, "accel_settings.json")
        # else:
        #    self._accelerometer.start_up()
        self._accel_bias: float = 0.01
        self._k_gravity:  float = 0.9995
        self._k_angle:    float = 0.9995
        self._time = 0.0
        # время простоя перед запуском
        self._warm_up_time:   float = 1.0
        # время калибровки
        self._calib_time:     float = 10.0
        self._calib_read_n:   int = 0
        # время ...
        self._trust_acc_time: float = 0.1
        # TODO connection to accelerometer check...
        self._timer: LoopTimer = LoopTimer(0.001)
        self._mode: int = STOP_MODE
        self._ang: Vector3   = Vector3(0.0, 0.0, 0.0)
        self._vel: Vector3   = Vector3(0.0, 0.0, 0.0)
        self._pos: Vector3   = Vector3(0.0, 0.0, 0.0)
        self._basis: Matrix4 = Matrix4.identity()

        self._omega_c: Vector3   = Vector3(0.0, 0.0, 0.0)
        self._accel_c: Vector3   = Vector3(0.0, 0.0, 0.0)
        print(f'|----------------Accelerometer start up...--------------|\n'
              f'|-------------Please stand by and hold still...---------|')

    @property
    def warm_up_time(self) -> float:
        return self._warm_up_time

    @warm_up_time.setter
    def warm_up_time(self, value: float) -> None:
        self._warm_up_time = min(max(0.125, value), 60)

    @property
    def calib_time(self) -> float:
        return self._calib_time

    @calib_time.setter
    def calib_time(self, value: float) -> None:
        self._calib_time = min(max(0.125, value), 60)

    @property
    def trust_acc_time(self) -> float:
        """
        Интервал времени для проверки наличия изменения в измерении вектора ускорения
        Если по истечению времени изменений не произошло, то считаем, что акселерометр неподвижен
        """
        return self._trust_acc_time

    @trust_acc_time.setter
    def trust_acc_time(self, value: float) -> None:
        """
        Интервал времени для проверки наличия изменения в измерении вектора ускорения
        Если по истечению времени изменений не произошло, то считаем, что акселерометр неподвижен
        """
        self._trust_acc_time = min(max(0.05, value), 1.0)

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
    def omega(self) -> Vector3:
        return self._accelerometer.omega

    @property
    def angles(self) -> Vector3:
        return self._ang

    @property
    def acceleration_calib(self) -> Vector3:
        return self._accelerometer.acceleration

    @property
    def omega_calib(self) -> Vector3:
        return self._accelerometer.acceleration

    @acceleration_calib.setter
    def acceleration_calib(self, value: Vector3) -> None:
        self._accel_c = value

    @omega_calib.setter
    def omega_calib(self, value: Vector3) -> None:
        self._omega_c = value

    @property
    def acceleration(self) -> Vector3:
        return self._accelerometer.acceleration

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

    def calibrate(self, timeout: float = None, forward: Vector3 = None) -> bool:
        print(f"|----------------Accelerometer start up...--------------|\n"
              f"|-------------Please stand by and hold still...---------|")
        if self._mode != INTEGRATE_MODE:
            return False
        self._calib_time = self._calib_time if timeout is None else timeout
        self._mode = CALIBRATION_MODE
        if forward is None:
            return True
        self._basis = Matrix4.build_basis(self.acceleration, forward)
        return True

    def update_basis(self) -> bool:
        if self._mode == CALIBRATION_MODE:
            return False
        self._mode = BASIS_COMPUTE_MODE
        return True

    def read(self) -> bool:
        if self._mode == CALIBRATION_MODE:
            return False
        self._mode = INTEGRATE_MODE
        return True

    def _integrate(self) -> bool:

        if self._mode != INTEGRATE_MODE:
            return False

        if not self._accelerometer.read_accel_measurements():
            return False

        dt    = self.delta_t

        if (self._accelerometer.acceleration - self._accelerometer.acceleration_prev).magnitude() > self._accel_bias:
            self._time = 0.0
        else:
            self._time += self.delta_t
            if self._time >= self._trust_acc_time:
                self._mode = BASIS_COMPUTE_MODE

        accel = self.acceleration
        omega = self.omega

        # r: Vector3 = (basis.right + Vector3.cross(omega, basis.right) * dt).normalized()
        # комплиментарная фильтрация и привязка u к направлению g
        # r: Vector3 = (basis.right + Vector3.cross(omega, basis.right) * dt).normalized()
        # комплиментарная фильтрация и и привязка u к направлению g
        u: Vector3 = ((self._basis.up    + Vector3.cross(omega, self._basis.up   ) * dt) *
                      self.k_gravity + (1.0 - self.k_gravity) * accel).normalized()
        f: Vector3 = (self._basis.front + Vector3.cross(omega, self._basis.front) * dt).normalized()
        r = Vector3.cross(f, u).normalized()
        f = Vector3.cross(u, r).normalized()
        # получим ускорение в мировой системе координат за вычетом ускорения свободного падения
        a: Vector3 = Vector3(accel.x - (r.x * self._accel_c.x + u.x * self._accel_c.y + f.x * self._accel_c.z),
                             accel.y - (r.y * self._accel_c.x + u.y * self._accel_c.y + f.y * self._accel_c.z),
                             accel.z - (r.z * self._accel_c.x + u.z * self._accel_c.y + f.z * self._accel_c.z))
        # комплиментарная фильтрация угла с направлением g
        self._basis = Matrix4.build_transform(r, u, f, a)
        self._ang += self._ang + omega * dt
        # g_angles = Vector3(math.pi + math.atan2(accel.z, accel.z),
        #                    math.pi + math.atan2(accel.y, accel.z),
        #                    math.pi + math.atan2(accel.y, accel.x))
        # self._ang = self.k_angle * self._ang + (1.0 - self.k_angle) * g_angles

        self._vel += (r * a.x + u * a.y + f * a.z) * dt if self._time >= self._trust_acc_time else Vector3(0.0, 0.0, 0.0)

        # интегрирование пути
        self._pos += (r * self._vel.x + u * self._vel.y + f * self._vel.z) * dt

    def _compute_basis(self) -> bool:
        if self._mode != BASIS_COMPUTE_MODE:
            return False
        self._mode = INTEGRATE_MODE
        self._basis = Matrix4.build_basis(self.acceleration, self._basis.front)
        self._ang   = Quaternion.from_rotation_matrix(self._basis).to_euler_angles()
        return True

    def _calibrate(self) -> bool:
        if self._mode != CALIBRATION_MODE:
            return False
        # докалибровались
        if self._time >= self._calib_time:
            self._time = 0.0
            self._omega_c /= self._calib_read_n
            self._accel_c /= self._calib_read_n
            self._calib_read_n = 0
            self._basis = Matrix4.build_basis(self._accel_c, self._basis.front)
            self._accel_c = Vector3(self._basis.m00 * self._accel_c.x + self._basis.m10 * self._accel_c.y + self._basis.m20 * self._accel_c.z,
                                    self._basis.m01 * self._accel_c.x + self._basis.m11 * self._accel_c.y + self._basis.m21 * self._accel_c.z,
                                    self._basis.m02 * self._accel_c.x + self._basis.m12 * self._accel_c.y + self._basis.m22 * self._accel_c.z)
            self._mode = BASIS_COMPUTE_MODE  # self._basis = Matrix4.build_basis(self.acceleration, self._basis.front)
            print(f"|-----------------Calibration is done-----------------|\n")
            return False

        # тряхнулись в процессе калибровки
        if (self._accelerometer.acceleration - self._accelerometer.acceleration_prev).magnitude() > self._accel_bias:
            self._time = 0.0
            self._omega_c /= self._calib_read_n
            self._accel_c /= self._calib_read_n
            self._calib_read_n = 0
            self._basis = Matrix4.build_basis(self._accel_c, self._basis.front)
            self._accel_c = Vector3(self._basis.m00 * self._accel_c.x + self._basis.m10 * self._accel_c.y + self._basis.m20 * self._accel_c.z,
                                    self._basis.m01 * self._accel_c.x + self._basis.m11 * self._accel_c.y + self._basis.m21 * self._accel_c.z,
                                    self._basis.m02 * self._accel_c.x + self._basis.m12 * self._accel_c.y + self._basis.m22 * self._accel_c.z)
            self._mode = BASIS_COMPUTE_MODE  # Matrix4.build_basis(self.acceleration, self._basis.front)
            print(f"|--------------Calibration is interrupted-------------|\n")
            return False

        filler_l = int(self._time / self._calib_time * 56)  # 56 - title chars count
        filler_r = 55 - filler_l
        sys.stdout.write(f'\r|{"":#>{str(filler_l)}}{"":.<{str(filler_r)}}|')
        sys.stdout.flush()
        if filler_r == 0:
            sys.stdout.write('\n\n')
        self._time += self.delta_t
        self._calib_read_n += 1
        self._omega_c += self.omega
        self._accel_c += self.acceleration
        return True

    def _warm_up(self) -> bool:
        if self._mode != WARM_UP_MODE:
            return False

        self._time += self.delta_t

        filler_l = int(self._time / self._warm_up_time * 56)  # 56 - title chars count

        filler_r = 55 - filler_l

        sys.stdout.write(f'\r|{"":#>{str(filler_l)}}{"":.<{str(filler_r)}}|')

        sys.stdout.flush()

        if filler_r == 0:
            sys.stdout.write('\n\n')

        if self._time >= self._warm_up_time:
            self._mode = CALIBRATION_MODE
            self._time = 0.0
        return True

    def run(self):
        if self._mode == STOP_MODE:
            return
        with self._timer:
            if not self._accelerometer.read_accel_measurements():
                raise RuntimeError("Read accelerometer measurements error...")
            if self._warm_up():
                return
            if self._calibrate():
                return
            if self._compute_basis():
                return
            self._integrate()
