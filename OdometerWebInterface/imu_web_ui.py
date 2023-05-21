from application import*
from threading import Lock


imu = IMU()
imu.enable_logging = False
record_imu_file_path = None
imu_clib_file_path = None
imu_lock = Lock()


#################################
#            BINGINGS           #
#################################
IMU_READ = "/imu_read"
IMU_PAUSE = "/imu_pause"
IMU_EXIT = "/imu_exit"
IMU_RESET = "/imu_reset"
IMU_CALIBRATE = "/imu_calibrate"
IMU_RECORD = "/imu_record"
IMU_SET_UPDATE_TIME = "/imu_set_update_time"
IMU_SET_RECORD_FILE_PATH = "/imu_set_record_file_path"
IMU_SET_CALIB_FILE_PATH = "/imu_set_calib_file_path"
IMU_SET_GRAVITY_SCALE = "/imu_set_gravity_scale"
IMU_SET_ANGLES_RATE = "/imu_set_angles_rate"
IMU_SET_TRUSTABLE_TIME = "/imu_set_trustable_time"
IMU_SET_ACCEL_THRESHOLD = "/imu_set_accel_threshold"
IMU_K_ARG = "/imu_set_k_arg"
