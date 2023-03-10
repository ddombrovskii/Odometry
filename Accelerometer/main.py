# from Accelerometer import Accelerometer
#from Accelerometer.accelerometer_recording import read_record, integrate_velocities, integrate_accelerations, accelerations, \
#    integrate_angles, ang_velocities
import math
import time

import matplotlib.pyplot as plt

from accelerometer_core import Accelerometer, read_accel_log
from accelerometer_core.utilities import Matrix3, Vector3, Quaternion

def rotationMatrixToEulerAngles(R: Matrix3):
    sy = math.sqrt(R.m00 * R.m00 + R.m10 * R.m10)
    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R.m21, R.m22)
        y = math.atan2(-R.m20, sy)
        z = math.atan2(R.m10, R.m00)
    else:
        x = math.atan2(-R.m12, R.m11)
        y = math.atan2(-R.m20, sy)
        z = 0
    return Vector3(x, y, z)


if __name__ == "__main__":
    _log_file = read_accel_log("accelerometer_core/accelerometer_records/the newest/building_walk_straight.json")
    _basis = Matrix3.build_basis(_log_file.way_points[0].acceleration)
    angles = [_basis.to_euler_angles()]
    angles_from_basis = [angles[-1]]
    n_iters = 1000
    dt = math.pi / (n_iters - 1)

    omega: Vector3 = Vector3(0.02,  0.02,  0.02)
    time_values = [0]


    for p in _log_file.way_points:

        f = (_basis.front + Vector3.cross(p.angles_velocity, _basis.front) * p.dtime).normalized()
        u = (_basis.up    + Vector3.cross(p.angles_velocity, _basis.up   ) * p.dtime).normalized()
        r = (_basis.right + Vector3.cross(p.angles_velocity, _basis.right) * p.dtime).normalized()
        _basis = Matrix3(r.x, u.x, f.x,
                         r.y, u.y, f.y,
                         r.z, u.z, f.z)
        #angles_from_basis.append(Quaternion.from_rotation_matrix(_basis).to_euler_angles())
        angles_from_basis.append(_basis.to_euler_angles())
        angle = (angles[-1] + p.angles_velocity * p.dtime) * 0.98 + 0.02 * angles_from_basis[-1]
        angles.append(Vector3(angle.x, angle.y, angle.z))
        time_values.append(time_values[-1] + p.dtime)

    plt.plot([time_values[0], time_values[-1]], [math.pi, math.pi], ':k')
    plt.plot([time_values[0], time_values[-1]], [-math.pi, -math.pi], ':k')

    plt.plot(time_values, [v.x for v in angles], 'r')
    plt.plot(time_values, [v.y for v in angles], 'g')
    plt.plot(time_values, [v.z for v in angles], 'b')

    #plt.plot(time_values, [v.x for v in angles_from_basis], ':r')
    #plt.plot(time_values, [v.y for v in angles_from_basis], ':g')
    #plt.plot(time_values, [v.z for v in angles_from_basis], ':b')
    plt.show()
    # accelerometer = Accelerometer()
    # accelerometer.calibrate(5)
    # time.sleep(10)
    ##accel_log = read_record("still.json")
    #ax, ay, az = accelerations(accel_log)
    #vx, vy, vz = integrate_accelerations(accel_log)
    #sx, sy, sz = integrate_velocities(accel_log)
    #v_ang_x, v_ang_y, v_ang_z = ang_velocities(accel_log)
    #ang_x, ang_y, ang_z = integrate_angles(accel_log)
