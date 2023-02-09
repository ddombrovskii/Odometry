from accelerometer import Accelerometer
from accelerometer_settings import load_accelerometer_settings, save_accelerometer_settings
from cgeo import LoopTimer, Vec3
import math


class IMU:
    def __init__(self):
        self._accelerometer: Accelerometer
        try:
            self._accelerometer = Accelerometer()
        except RuntimeError as err:
            print(err.args)
            exit(-13)
        self._k = 0.99
        # TODO connection to accelerometer check...
        self._timer: LoopTimer = LoopTimer(0.001)

        self._v_ang: Vec3 = Vec3(0.0)
        self._accel: Vec3 = Vec3(0.0)

        self._ang: Vec3 = Vec3(0.0)
        self._vel: Vec3 = Vec3(0.0)
        self._pos: Vec3 = Vec3(0.0)
        if not load_accelerometer_settings(self._accelerometer, "accel_settings.json"):
            self.calibrate(30)
            save_accelerometer_settings(self._accelerometer, "accel_settings.json")

    @property
    def angles_velocity(self) -> Vec3:
        return self._accelerometer.ang_velocity

    @property
    def angles(self) -> Vec3:
        return self._ang

    @property
    def acceleration(self) -> Vec3:
        return self._accelerometer.acceleration

    @property
    def velocity(self) -> Vec3:
        return self._vel

    @property
    def position(self) -> Vec3:
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

    def read(self) -> bool:
        with self._timer:
            if not self._accelerometer.read_accel_measurements():
                return False
                #raise RuntimeError("accelerometer reading error")

            curr_accel = self._accelerometer.acceleration
            prev_accel = self._accelerometer.prev_acceleration

            dt = self._accelerometer.delta_t
            # Считается, что общий вклад вектора G неизменен, поэтому разница между предыдущим и следующим
            # значением позволит исключить его влияние на измеренное ускорение
            self._accel.x += curr_accel.x - prev_accel.x
            self._accel.y += curr_accel.y - prev_accel.y
            self._accel.z += curr_accel.z - prev_accel.z
            # углы из значения ускорения (верно лишь при относительно небольших значениях)
            accel_a_x = math.pi + math.atan2(curr_accel.z, curr_accel.z)
            accel_a_y = math.pi + math.atan2(curr_accel.y, curr_accel.z)
            accel_a_z = math.pi + math.atan2(curr_accel.y, curr_accel.x)
            # Наивное интегрирование угла
            self._ang.x += self._accelerometer.ang_velocity.x * dt
            self._ang.z += self._accelerometer.ang_velocity.z * dt
            self._ang.y += self._accelerometer.ang_velocity.y * dt
            # Корректировка дрейфа угла гироскопа комплиментарным фильтром
            self._ang.x = self._k * self._ang.x + (1.0 - self._k) * accel_a_x
            self._ang.z = self._k * self._ang.z + (1.0 - self._k) * accel_a_y
            self._ang.y = self._k * self._ang.y + (1.0 - self._k) * accel_a_z
            # Построение локального базиса гироскопа на основе вычисленных углов
            sin_a, sin_b, sin_g = math.sin(self._ang.x), math.sin(self._ang.y), math.sin(self._ang.z)
            cos_a, cos_b, cos_g = math.cos(self._ang.x), math.cos(self._ang.y), math.cos(self._ang.z)

            ex = (cos_a * cos_g - sin_a * cos_b * sin_g,
                  sin_a * cos_g - cos_a * cos_b * sin_g,
                  sin_b * sin_g)

            ey = (-cos_a * sin_g - sin_a * cos_b * cos_g,
                  -sin_a * sin_g + cos_a * cos_b * cos_g,
                  sin_b * cos_g)

            ez = (sin_a * sin_b, -cos_a * sin_b, cos_b)
            # Расчёт значения скорости в мировых координатах
            accel_c = self._accelerometer.acceleration_calibration
            self._vel.x += ((ex[0] * self._accel.x + ex[1] * self._accel.y + ex[2] * self._accel.z) - accel_c.x) * dt
            self._vel.y += ((ey[0] * self._accel.x + ey[1] * self._accel.y + ey[2] * self._accel.z) - accel_c.y) * dt
            self._vel.z += ((ez[0] * self._accel.x + ez[1] * self._accel.y + ez[2] * self._accel.z) - accel_c.z) * dt
            # Расчёт значения положения в мировых координатах
            self._pos.x += self._vel.x * dt
            self._pos.y += self._vel.y * dt
            self._pos.z += self._vel.z * dt
            return True

    def calibrate(self, timeout: float, forward: Vec3) -> None:
        self._accelerometer.calibrate(timeout, forward)
        self._ang = self._accelerometer.start_ang_values
