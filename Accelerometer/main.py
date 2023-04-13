import math

import numpy as np

from Accelerometer.accelerometer_core.accelerometer_integrator import AccelIntegrator

if __name__ == "__main__":
    # integrator = AccelIntegrator("accelerometer_core/accelerometer_records/the newest/building_way_2.json")
    integrator = AccelIntegrator("accelerometer_core/accelerometer_records/record_bno_test.json")
    integrator.integrate()
    integrator.show_results_xz()
    integrator.show_path()
# from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU
#
#if __name__ == "__main__":
#    import cv2 as cv
#    cv.namedWindow("accelerometer", cv.WINDOW_NORMAL)
#    imu = IMU()
#    imu.run()


# from matplotlib import pyplot as plt
#
# t = np.linspace(0, np.pi, 2000)
# x = np.cos(t * 10)
# y = np.sin(t * 5)
# _x = [x[0]]
# _y = [y[0]]
# s = 0.01
# for xi, yi in zip(x.flat, y.flat):
#     alpha = (xi - yi) * s
#     _x.append(_x[-1] - alpha)
#     _y.append(_y[-1] + alpha)
#
#
# plt.plot(_x, 'r')
# plt.plot(_y, 'g')
# plt.show()