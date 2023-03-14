from Accelerometer.accelerometer_core.accelerometer_integrator import AccelIntegrator

#if __name__ == "__main__":
#    integrator = AccelIntegrator("accelerometer_core/accelerometer_records/the newest/building_way_2.json")
#    integrator.integrate()
#    integrator.show_results_xz()

from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU

if __name__ == "__main__":
    imu = IMU()
    imu.run()
