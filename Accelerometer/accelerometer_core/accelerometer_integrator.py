from accelerometer_core.utilities import Matrix4, Vector3, Quaternion
from accelerometer_core import read_accel_log, AccelMeasurement
from matplotlib import pyplot as plt
from typing import List


CALIBRATION_MODE = 0
BASIS_COMPUTE_MODE = 1
INTEGRATE_MODE = 2
STOP_MODE = 3
WARM_UP_MODE = 4


class AccelIntegrator:
    def __init__(self, log_src: str):
        self._log_file = read_accel_log(log_src)
        self._time_values:  List[float] = []
        self._omegas:       List[Vector3] = [Vector3(0.0, 0.0, 0.0)]
        self._angles:       List[Vector3] = []
        self._velocities:   List[Vector3] = []  # [Vector3(0.0, 0.0, 0.0)]
        self._positions:    List[Vector3] = []  # [Vector3(0.0, 0.0, 0.0)]
        self._accel_basis:  List[Matrix4] = []  # [Matrix4.build_basis(point.acceleration)]
        self._curr_accel:   Vector3 = Vector3(0.0, 0.0, 0.0)
        self._prev_accel:   Vector3 = Vector3(0.0, 0.0, 0.0)
        self._calib_accel:  Vector3 = Vector3(0.0, 0.0, 0.0)
        self._calib_omega:  Vector3 = Vector3(0.0, 0.0, 0.0)
        self._accel_bias:   float = 0.01
        self._trust_t:      float = 0.1
        self._time:         float = 0.0
        self._warm_up_time: float = 1.0
        self._calib_time:   float = 5.0
        self._calib_cntr:   int = 0
        self._mode:         int = WARM_UP_MODE
        self._accel_k:      float = 0.98  # значение параметра комплиментарного фильтра для ускорения
        self._velocity_k:   float = 0.9995  # значение параметра комплиментарного фильтра для ускорения

    @property
    def accel_k(self) -> float:
        """
        Параметр комплиметарного фильтра для направления ускорения
        """
        return self._accel_k

    @accel_k.setter
    def accel_k(self, value: float) -> None:
        """
        Параметр комплиметарного фильтра для направления ускорения
        """
        self._accel_k = min(max(0.0, value), 1.0)
        
    @property
    def calib_time(self) -> float:
        """
        Время калибровки
        """
        return self._calib_time

    @calib_time.setter
    def calib_time(self, value: float) -> None:
        """
        Время калибровки
        """
        self._calib_time = min(max(0.5, value), 60.0)
    
    @property
    def warm_up_time(self) -> float:
        """
        Время старта
        """
        return self._warm_up_time

    @warm_up_time.setter
    def warm_up_time(self, value: float) -> None:
        """
        Время старта
        """
        self._warm_up_time = min(max(0.5, value), 60.0)
        
    @property
    def accel_trust_time(self) -> float:
        """
        Время анализа изменения модуля ускорения. Если модуль значения ускорения остаётся меньше некоторой величины, то
        обнуляем скорость движения
        """
        return self._trust_t

    @accel_trust_time.setter
    def accel_trust_time(self, value: float) -> None:
        """
        Время анализа изменения модуля ускорения. Если модуль значения ускорения остаётся меньше некоторой величины, то
        обнуляем скорость движения
        """
        self._trust_t = min(max(0.01, value), 10.0)
        
    @property
    def accel_trust_bias(self) -> float:
        """
        Если модуль значения ускорения остаётся меньше accel_trust_bias в течении времени accel_trust_time, то
        обнуляем скорость движения
        """
        return self._accel_bias

    @accel_trust_bias.setter
    def accel_trust_bias(self, value: float) -> None:
        """
        Если модуль значения ускорения остаётся меньше accel_trust_bias в течении времени accel_trust_time, то
        обнуляем скорость движения
        """
        self._accel_bias = min(max(0.001, value), 1.0)
    
    @property
    def time_values(self) -> List[float]:
        """
        Список измерений времени
        """
        return self._time_values

    @property
    def angles(self) -> List[Vector3]:
        """
        Список углов
        """
        return self._angles

    @property
    def omegas(self) -> List[Vector3]:
        """
        Список углов
        """
        return self._omegas

    @property
    def velocities(self) -> List[Vector3]:
        """
        Список скоростей в мировой системе
        """
        return self._velocities

    @property
    def positions(self) -> List[Vector3]:
        """
        Список положений в мировой системе
        """
        return self._positions

    @property
    def accel_basis(self) -> List[Vector3]:
        """
        Список локальных базисов и ускорений в собственной системе
        """
        return self._accel_basis

    @property
    def curr_accel(self) -> Vector3:
        """
        Текущее ускорение
        """
        return self._curr_accel

    @property
    def prev_accel(self) -> Vector3:
        """
        Предыдущее ускорение
        """
        return self._prev_accel

    @property
    def calib_accel(self) -> Vector3:
        """
        Калибровочное значение ускорения
        """
        return self._calib_accel

    @property
    def calib_omega(self) -> Vector3:
        """
        Калибровочное значение угловой скорости
        """
        return self._calib_omega
    
    def _warm_up(self, point: AccelMeasurement) -> bool:
        """
        Пропускает часть измерений в течении какого-то времени. По завершении включается калибровка
        """
        if self._mode != WARM_UP_MODE:
            return False
        if self._time > self._warm_up_time:
            self._mode = CALIBRATION_MODE
            self._time = 0.0
            return False
        self._time += point.dtime
        return True

    def _calibrate(self, point: AccelMeasurement) -> bool:
        """
        Калибрует значения угловой скорости и ускорения. Если акселерометр тряхнёт, то калибровка прерывается на
        последнем измерении и происходит расчёт калибровочных значений
        """
        if self._mode != CALIBRATION_MODE:
            return False

        if self._time < self._calib_time:
            self._calib_accel += point.acceleration
            self._calib_omega += point.angles_velocity
            self._time        += point.dtime
            self._calib_cntr  += 1
            return True

        self._mode = INTEGRATE_MODE
        self._calib_accel /= self._calib_cntr
        self._calib_omega /= self._calib_cntr
        basis: Matrix4 = Matrix4.build_basis(self._calib_accel)
        self._accel_basis.append(Matrix4.build_transform(basis.right, basis.up, basis.front, self._calib_accel))
        """
        Калибровочное ускорение записывается в мировой системе координат
        """
        self._calib_accel = Vector3(basis.m00 * self._calib_accel.x +
                                    basis.m10 * self._calib_accel.y +
                                    basis.m20 * self._calib_accel.z,
                                    basis.m01 * self._calib_accel.x +
                                    basis.m11 * self._calib_accel.y +
                                    basis.m21 * self._calib_accel.z,
                                    basis.m02 * self._calib_accel.x +
                                    basis.m12 * self._calib_accel.y +
                                    basis.m22 * self._calib_accel.z)
        print(f"c_accel ls: {self._accel_basis[-1].origin}")
        print(f"c_accel   : {self._calib_accel}")
        print(f"c_omega   : {self._calib_omega}")
        print(f"c_count   : {self._calib_cntr}")
        self._angles.append(Quaternion.from_rotation_matrix(self._accel_basis[-1]).to_euler_angles())
        self._velocities.append(Vector3(0.0, 0.0, 0.0))
        self._positions.append(Vector3(0.0, 0.0, 0.0))
        self._time_values.append(self._time + self.warm_up_time)
        self._time = 0.0
        self._calib_cntr = 0
        return False

    def _build_basis(self, point: AccelMeasurement) -> bool:
        """
        Не используется
        """
        if self._mode != BASIS_COMPUTE_MODE:
            return False
        return False

    def _integrate(self, point: AccelMeasurement) -> bool:
        """
        Интегрирование скорости, угла, и положения
        """
        if self._mode != INTEGRATE_MODE:
            return False
        dt    = point.dtime
        omega = point.angles_velocity
        basis = self._accel_basis[-1]
        self._omegas.append(omega)
        #  комплиментарная фильтрация и привязка u к направлению g
        u: Vector3 = ((basis.up * Vector3.dot(basis.up, self._curr_accel) + Vector3.cross(omega, basis.up) * dt) *
                      self._accel_k + (1.0 - self._accel_k) * self._curr_accel)
        f: Vector3 = (basis.front + Vector3.cross(omega, basis.front) * dt)  # .normalized()
        r = Vector3.cross(f, u)  # .normalized()
        f = Vector3.cross(u, r)  # .normalized()
        f = f.normalized()
        u = u.normalized()
        r = r.normalized()
        # получим ускорение в мировой системе координат за вычетом ускорения свободного падения
        a: Vector3 = Vector3(self._curr_accel.x - (r.x * self._calib_accel.x + u.x * self._calib_accel.y + f.x * self._calib_accel.z),
                             self._curr_accel.y - (r.y * self._calib_accel.x + u.y * self._calib_accel.y + f.y * self._calib_accel.z),
                             self._curr_accel.z - (r.z * self._calib_accel.x + u.z * self._calib_accel.y + f.z * self._calib_accel.z))
        """
        Проверка наличия весомых изменений в векторе ускорения в течении времени
        """
        if (self._curr_accel - self._prev_accel).magnitude() < self._accel_bias:
            self._time += dt
        else:
            self._time = 0

        self._accel_basis.append(Matrix4.build_transform(r, u, f, a))

        self._angles.append(self._accel_basis[-1].to_euler_angles())

        v = (self._velocities[-1] + (r * a.x + u * a.y + f * a.z) * dt) \
            if self._time <= self._trust_t else Vector3(0.0, 0.0, 0.0)
        # v = Vector3(0.1, 0.1, 0.1)  if self._time <= self._trust_t else Vector3(0.0, 0.0, 0.0)
        # self._angles.append(self._angles[-1] + (point.angles_velocity - self._calib_omega) * dt)
        self._velocities.append(v)
        self._positions.append(self._positions[-1] + (r * v.x + u * v.y + f * v.y) * dt)
        self._time_values.append(self._time_values[-1] + dt)
        return True

    def show_results(self):
        fig, axes = plt.subplots(5)
        angles = [m.to_euler_angles() for m in self._accel_basis]
        axes[0].plot(self.time_values, [a.x for a in self.angles], 'r')
        axes[0].plot(self.time_values, [a.y for a in self.angles], 'g')
        axes[0].plot(self.time_values, [a.z for a in self.angles], 'b')
        axes[0].plot(self.time_values, [a.x for a in angles], ':r')
        axes[0].plot(self.time_values, [a.y for a in angles], ':g')
        axes[0].plot(self.time_values, [a.z for a in angles], ':b')
        axes[0].set_xlabel("t, [sec]")
        axes[0].set_ylabel("$angle(t), [rad]$")
        axes[0].set_title("angles")

        axes[1].plot(self.time_values, [a.origin.x for a in self.accel_basis], 'r')
        axes[1].plot(self.time_values, [a.origin.y for a in self.accel_basis], 'g')
        axes[1].plot(self.time_values, [a.origin.z for a in self.accel_basis], 'b')
        axes[1].set_xlabel("t, [sec]")
        axes[1].set_ylabel("$a(t), [m/sec^2]$")
        axes[1].set_title("accelerations - world space")

        axes[2].plot(self.time_values, [v.x for v in self.velocities], 'r')
        axes[2].plot(self.time_values, [v.y for v in self.velocities], 'g')
        axes[2].plot(self.time_values, [v.z for v in self.velocities], 'b')
        axes[2].set_xlabel("t, [sec]")
        axes[2].set_ylabel("$v(t), [m/sec]$")
        axes[2].set_title("velocities - world space")

        axes[3].plot(self.time_values, [p.x for p in self.positions], 'r')
        axes[3].plot(self.time_values, [p.y for p in self.positions], 'g')
        axes[3].plot(self.time_values, [p.z for p in self.positions], 'b')
        axes[3].set_xlabel("t, [sec]")
        axes[3].set_ylabel("$S(t), [m]$")
        axes[3].set_title("positions - world space")

        axes[4].plot([p.x for p in self.positions], [p.z for p in self.positions], 'r')
        axes[4].set_aspect('equal', 'box')
        axes[4].set_xlabel("Sx, [m]")
        axes[4].set_ylabel("Sz, [m]")
        axes[4].set_title("positions - world space")
        plt.show()

    def show_results_xz(self):
        fig, axes = plt.subplots(6)
        axes[0].plot(self.time_values, [a.x for a in self.omegas], 'r')
        axes[0].plot(self.time_values, [a.y for a in self.omegas], 'g')
        axes[0].plot(self.time_values, [a.z for a in self.omegas], 'b')
        axes[0].set_xlabel("t, [sec]")
        axes[0].set_ylabel("$omega(t), [rad/sec]$")
        axes[0].set_title("angles")

        axes[1].plot(self.time_values, [a.x for a in self.angles], 'r')
        axes[1].plot(self.time_values, [a.y for a in self.angles], 'g')
        axes[1].plot(self.time_values, [a.z for a in self.angles], 'b')
        axes[1].set_xlabel("t, [sec]")
        axes[1].set_ylabel("$angle(t), [rad]$")
        axes[1].set_title("angles")

        axes[2].plot(self.time_values, [a.origin.x for a in self.accel_basis], 'r')
        axes[2].plot(self.time_values, [a.origin.z for a in self.accel_basis], 'b')
        axes[2].set_xlabel("t, [sec]")
        axes[2].set_ylabel("$a(t), [m/sec^2]$")
        axes[2].set_title("accelerations - world space")

        axes[3].plot(self.time_values, [v.x for v in self.velocities], 'r')
        axes[3].plot(self.time_values, [v.z for v in self.velocities], 'b')
        axes[3].set_xlabel("t, [sec]")
        axes[3].set_ylabel("$v(t), [m/sec]$")
        axes[3].set_title("velocities - world space")

        axes[4].plot(self.time_values, [p.x for p in self.positions], 'r')
        axes[4].plot(self.time_values, [p.z for p in self.positions], 'b')
        axes[4].set_xlabel("t, [sec]")
        axes[4].set_ylabel("$S(t), [m]$")
        axes[4].set_title("positions - world space")

        axes[5].plot([p.x for p in self.positions], [p.z for p in self.positions], 'r')
        axes[5].set_aspect('equal', 'box')
        axes[5].set_xlabel("Sx, [m]")
        axes[5].set_ylabel("Sz, [m]")
        axes[5].set_title("positions - world space")
        plt.show()

    def show_path(self):
        fig, axes = plt.subplots(1)
        axes[0].plot([p.x for p in self.positions], [p.z for p in self.positions], 'r')
        axes[0].set_aspect('equal', 'box')
        axes[0].set_xlabel("Sx, [m]")
        axes[0].set_ylabel("Sz, [m]")
        axes[0].set_title("positions - world space")
        plt.show()
  
    def integrate(self):
        for point in self._log_file.way_points:
            self._prev_accel = self._curr_accel
            self._curr_accel = point.acceleration
            if self._warm_up(point):
                continue
            if self._calibrate(point):
                continue
            if self._build_basis(point):
                continue
            if self._integrate(point):
                continue


if __name__ == "__main__":
    integrator = AccelIntegrator("accelerometer_records/the newest/building_way_2.json")
    integrator.integrate()
    integrator.show_results_xz()
