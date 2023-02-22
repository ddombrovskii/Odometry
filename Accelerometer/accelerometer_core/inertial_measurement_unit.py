from accelerometer_core.accelerometer import Accelerometer
from accelerometer_core.utilities import Vector3, Matrix4
from accelerometer_core.utilities import LoopTimer
# from accelerometer_settings import load_accelerometer_settings, save_accelerometer_settings
import math


class IMU:
    def __init__(self):
        self._accelerometer: Accelerometer
        try:
            self._accelerometer = Accelerometer()
        except RuntimeError as err:
            print(err.args)
            exit(-13)
        self.calibrate(20)
            
        #if not load_accelerometer_settings(self._accelerometer, "accel_settings.json"):
         #   self.calibrate(10)
         #   save_accelerometer_settings(self._accelerometer, "accel_settings.json")
        #else:
            #self._accelerometer.compute_static_orientation()
        self._k = 0.98
        # TODO connection to accelerometer check...
        self._timer: LoopTimer = LoopTimer(0.001)

        self._v_ang: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._accel: Vector3 = Vector3(0.0, 0.0, 0.0)

        self._ang: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._vel: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._pos: Vector3 = Vector3(0.0, 0.0, 0.0)
        # self.calibrate(5.0)

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

    def read(self) -> bool:
        with self._timer:
            if not self._accelerometer.read_accel_measurements():
                return False
                #raise RuntimeError("accelerometer reading error")

            _accel = self._accelerometer.acceleration
            
            dt = self._accelerometer.delta_t
            # Считается, что общий вклад вектора G неизменен, поэтому разница между предыдущим и следующим
            # значением позволит исключить его влияние на измеренное ускорение
            self._accel.x = _accel.x
            self._accel.y = _accel.y
            self._accel.z = _accel.z
            # углы из значения ускорения (верно лишь при относительно небольших значениях)
            accel_a_x = math.pi + math.atan2(_accel.z, _accel.z)
            accel_a_y = math.pi + math.atan2(_accel.y, _accel.z)
            accel_a_z = math.pi + math.atan2(_accel.y, _accel.x)
            # Наивное интегрирование угла
            # Корректировка дрейфа угла гироскопа комплиментарным фильтром
            self._ang.x = (self._ang.x + self._accelerometer.ang_velocity.x * dt) * self._k + (1.0 - self._k) * accel_a_x
            self._ang.z = (self._ang.y + self._accelerometer.ang_velocity.z * dt) * self._k + (1.0 - self._k) * accel_a_y
            self._ang.y = (self._ang.z + self._accelerometer.ang_velocity.y * dt) * self._k + (1.0 - self._k) * accel_a_z
       
            # Построение локального базиса гироскопа на основе вычисленных углов
            """
            sin_a, sin_b, sin_g = utilities.sin(self._ang.x), utilities.sin(self._ang.y), utilities.sin(self._ang.z)
            cos_a, cos_b, cos_g = utilities.cos(self._ang.x), utilities.cos(self._ang.y), utilities.cos(self._ang.z)

            ex = (cos_a * cos_g - sin_a * cos_b * sin_g,
                  sin_a * cos_g - cos_a * cos_b * sin_g,
                  sin_b * sin_g)

            ey = (-cos_a * sin_g - sin_a * cos_b * cos_g,
                  -sin_a * sin_g + cos_a * cos_b * cos_g,
                  sin_b * cos_g)

            ez = (sin_a * sin_b, -cos_a * sin_b, cos_b)
            """
            rm =  Matrix4.rotate_z(-self._ang.z) * Matrix4.rotate_y(-self._ang.y) * Matrix4.rotate_x(-self._ang.x)
            # Расчёт значения скорости в мировых координатах
            # accel_c = self._accelerometer.acceleration_calibration
            #self._accel.x = curr_accel.x# - prev_accel.x
            #self._accel.y = curr_accel.y# - prev_accel.y
            #self._accel.z = curr_accel.z# - prev_accel.z
            # print(self._ang)
            # print(ex)
            # print(ey)
            # print(ez)
            # print(accel_c)
            # print(curr_accel)
            # print((rm.m00 * curr_accel.x + rm.m01 * curr_accel.y + rm.m02 * curr_accel.z))
            # print((rm.m10 * curr_accel.x + rm.m11 * curr_accel.y + rm.m12 * curr_accel.z))
            # print((rm.m20 * curr_accel.x + rm.m21 * curr_accel.y + rm.m22 * curr_accel.z))
            # print("________________________________________________________")
            
            # ax = ((rm.m00 * curr_accel.x + rm.m01 * curr_accel.y + rm.m02 * curr_accel.z) + (rm.m00 * accel_c.x + rm.m01 * accel_c.y + rm.m02 * accel_c.z))
            # ay = ((rm.m10 * curr_accel.x + rm.m11 * curr_accel.y + rm.m12 * curr_accel.z) + (rm.m10 * accel_c.x + rm.m11 * accel_c.y + rm.m12 * accel_c.z))
            # az = ((rm.m20 * curr_accel.x + rm.m21 * curr_accel.y + rm.m22 * curr_accel.z) + (rm.m20 * accel_c.x + rm.m21 * accel_c.y + rm.m22 * accel_c.z))
          
            # self._accel.x = (rm.m00 * curr_accel.x + rm.m01 * curr_accel.y + rm.m02 * curr_accel.z) + (rm.m00 * accel_c.x + rm.m01 * accel_c.x + rm.m02 * accel_c.x)
            # self._accel.y = (rm.m10 * curr_accel.x + rm.m11 * curr_accel.y + rm.m12 * curr_accel.z) + (rm.m10 * accel_c.y + rm.m11 * accel_c.y + rm.m12 * accel_c.y)
            # self._accel.z = (rm.m20 * curr_accel.x + rm.m21 * curr_accel.y + rm.m22 * curr_accel.z) + (rm.m20 * accel_c.z + rm.m21 * accel_c.z + rm.m22 * accel_c.z)
            
            self._vel.x += (rm.m00 * self._accel.x + rm.m01 * self._accel.y + rm.m02 * self._accel.z) * dt
            self._vel.y += (rm.m10 * self._accel.x + rm.m11 * self._accel.y + rm.m12 * self._accel.z) * dt
            self._vel.z += (rm.m20 * self._accel.x + rm.m21 * self._accel.y + rm.m22 * self._accel.z) * dt
            # Расчёт значения положения в мировых координатах
            self._pos.x += self._vel.x * dt
            self._pos.y += self._vel.y * dt
            self._pos.z += self._vel.z * dt
            return True

    def calibrate(self, timeout: float, forward: Vector3 = None) -> None:
        self._accelerometer.calibrate(timeout, forward)
        self._ang = self._accelerometer.start_ang_values
