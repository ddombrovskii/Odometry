# from Accelerometer import Accelerometer
#from Accelerometer.accelerometer_recording import read_record, integrate_velocities, integrate_accelerations, accelerations, \
#    integrate_angles, ang_velocities
import time

from accelerometer_core import Accelerometer

if __name__ == "__main__":
    accelerometer = Accelerometer()
    accelerometer.calibrate(5)
    time.sleep(10)
    ##accel_log = read_record("still.json")
    #ax, ay, az = accelerations(accel_log)
    #vx, vy, vz = integrate_accelerations(accel_log)
    #sx, sy, sz = integrate_velocities(accel_log)
    #v_ang_x, v_ang_y, v_ang_z = ang_velocities(accel_log)
    #ang_x, ang_y, ang_z = integrate_angles(accel_log)
