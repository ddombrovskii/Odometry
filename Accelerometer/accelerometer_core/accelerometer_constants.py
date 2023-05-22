GRAVITY_CONSTANT = 9.80665  # [m / sec^2]

FILTER_GX = 0
FILTER_GY = 1
FILTER_GZ = 2

FILTER_AX = 3
FILTER_AY = 4
FILTER_AZ = 5

# MPU-6050 Registers
MPU6050_PWR_MGMT_1 = 0x6B
MPU6050_SAMPLE_RATE_DIV = 0x19
MPU6050_MPU_CONFIG = 0x1A
MPU6050_ACCEL_CONFIG = 0x1C
MPU6050_GYRO_CONFIG = 0x1B
MPU6050_INT_ENABLE = 0x38

MPU6050_YGRO_X_OUT_H = 0x43
MPU6050_GYRO_X_OUT_L = 0x44
MPU6050_GYRO_Y_OUT_H = 0x45
MPU6050_GYRO_Y_OUT_L = 0x46
MPU6050_GYRO_Z_OUT_H = 0x47
MPU6050_GYRO_Z_OUT_L = 0x48
MPU6050_ACCEL_X_OUT_H = 0x3B
MPU6050_ACCEL_X_OUT_L = 0x3C
MPU6050_ACCEL_Y_OUT_H = 0x3D
MPU6050_ACCEL_Y_OUT_L = 0x3E
MPU6050_ACCEL_Z_OUT_H = 0x3F
MPU6050_ACCEL_Z_OUT_L = 0x40
MPU6050_TEMP_OUT_H = 0x41
# Scale Modifiers
MPU6050_ACCEL_SCALE_MODIFIER_2G = 16384.0
MPU6050_ACCEL_SCALE_MODIFIER_4G = 8192.0
MPU6050_ACCEL_SCALE_MODIFIER_8G = 4096.0
MPU6050_ACCEL_SCALE_MODIFIER_16G = 2048.0
MPU6050_GYRO_SCALE_MODIFIER_250DEG = 131.0
MPU6050_GYRO_SCALE_MODIFIER_500DEG = 65.5
MPU6050_GYRO_SCALE_MODIFIER_1000DEG = 32.8
MPU6050_GYRO_SCALE_MODIFIER_2000DEG = 16.4

# Pre-defined ranges
MPU6050_ACCEL_RANGE_2G = 0x00
MPU6050_ACCEL_RANGE_4G = 0x08
MPU6050_ACCEL_RANGE_8G = 0x10
MPU6050_ACCEL_RANGE_16G = 0x18
MPU6050_GYRO_RANGE_250DEG = 0x00
MPU6050_GYRO_RANGE_500DEG = 0x08
MPU6050_GYRO_RANGE_1000DEG = 0x10
MPU6050_GYRO_RANGE_2000DEG = 0x18

# Filter settings
MPU6050_FILTER_BW_256 = 0x00
MPU6050_FILTER_BW_188 = 0x01
MPU6050_FILTER_BW_98 = 0x02
MPU6050_FILTER_BW_42 = 0x03
MPU6050_FILTER_BW_20 = 0x04
MPU6050_FILTER_BW_10 = 0x05
MPU6050_FILTER_BW_5 = 0x06


# BNO055 Registers
START_BYTE     = 0xAA
RESPONSE_BYTE  = 0xBB
ERROR_BYTE     = 0xEE

BNO055_I2C_ADDR_HI       = 0x29
BNO055_I2C_ADDR_LO       = 0x28
BNO055_READ_TIMEOUT      = 100
BNO055_WRITE_TIMEOUT     = 10

ERROR_WRITE_SUCCESS      = 0x01  # Everything working as expected
ERROR_WRITE_FAIL         = 0x03  # Check connection, protocol settings and operation more of BNO055
ERROR_REGMAP_INV_ADDR    = 0x04  # Invalid register address
ERROR_REGMAP_WRITE_DIS   = 0x05  # Register is read-only
ERROR_WRONG_START_BYTE   = 0x06  # Check if the first byte
ERROR_BUS_OVERRUN_ERR    = 0x07  # Resend the command, BNO055 was not able to clear the receive buffer
ERROR_MAX_LEN_ERR        = 0x08  # Split the command, max fire size can be up to 128 bytes
ERROR_MIN_LEN_ERR        = 0x09  # Min length of data is less than 1
ERROR_RECV_CHAR_TIMEOUT  = 0x0A

REG_WRITE = 0x00
REG_READ  = 0x01

BNO055_ID = 0xA0
BNO055_CHIP_ID         = 0x00  # value: 0xA0
BNO055_ACC_ID          = 0x01  # value: 0xFB
BNO055_MAG_ID          = 0x02  # value: 0x32
BNO055_GYR_ID          = 0x03  # value: 0x0F
BNO055_SW_REV_ID_LSB   = 0x04  # value: 0x08
BNO055_SW_REV_ID_MSB   = 0x05  # value: 0x03
BNO055_BL_REV_ID       = 0x06  # N/A
BNO055_PAGE_ID         = 0x07
BNO055_ACC_DATA_X_LSB  = 0x08
BNO055_ACC_DATA_X_MSB  = 0x09
BNO055_ACC_DATA_Y_LSB  = 0x0A
BNO055_ACC_DATA_Y_MSB  = 0x0B
BNO055_ACC_DATA_Z_LSB  = 0x0C
BNO055_ACC_DATA_Z_MSB  = 0x0D
BNO055_MAG_DATA_X_LSB  = 0x0E
BNO055_MAG_DATA_X_MSB  = 0x0F
BNO055_MAG_DATA_Y_LSB  = 0x10
BNO055_MAG_DATA_Y_MSB  = 0x11
BNO055_MAG_DATA_Z_LSB  = 0x12
BNO055_MAG_DATA_Z_MSB  = 0x13
BNO055_GYR_DATA_X_LSB  = 0x14
BNO055_GYR_DATA_X_MSB  = 0x15
BNO055_GYR_DATA_Y_LSB  = 0x16
BNO055_GYR_DATA_Y_MSB  = 0x17
BNO055_GYR_DATA_Z_LSB  = 0x18
BNO055_GYR_DATA_Z_MSB  = 0x19
BNO055_EUL_HEADING_LSB = 0x1A
BNO055_EUL_HEADING_MSB = 0x1B
BNO055_EUL_ROLL_LSB    = 0x1C
BNO055_EUL_ROLL_MSB    = 0x1D
BNO055_EUL_PITCH_LSB   = 0x1E
BNO055_EUL_PITCH_MSB   = 0x1F
BNO055_QUA_DATA_W_LSB  = 0x20
BNO055_QUA_DATA_W_MSB  = 0x21
BNO055_QUA_DATA_X_LSB  = 0x22
BNO055_QUA_DATA_X_MSB  = 0x23
BNO055_QUA_DATA_Y_LSB  = 0x24
BNO055_QUA_DATA_Y_MSB  = 0x25
BNO055_QUA_DATA_Z_LSB  = 0x26
BNO055_QUA_DATA_Z_MSB  = 0x27
BNO055_LIA_DATA_X_LSB  = 0x28
BNO055_LIA_DATA_X_MSB  = 0x29
BNO055_LIA_DATA_Y_LSB  = 0x2A
BNO055_LIA_DATA_Y_MSB  = 0x2B
BNO055_LIA_DATA_Z_LSB  = 0x2C
BNO055_LIA_DATA_Z_MSB  = 0x2D
BNO055_GRV_DATA_X_LSB  = 0x2E
BNO055_GRV_DATA_X_MSB  = 0x2F
BNO055_GRV_DATA_Y_LSB  = 0x30
BNO055_GRV_DATA_Y_MSB  = 0x31
BNO055_GRV_DATA_Z_LSB  = 0x32
BNO055_GRV_DATA_Z_MSB  = 0x33
BNO055_TEMP             = 0x34
BNO055_CALIB_STAT       = 0x35
BNO055_ST_RESULT        = 0x36
BNO055_INT_STATUS       = 0x37
BNO055_SYS_CLK_STATUS   = 0x38
BNO055_SYS_STATUS       = 0x39
BNO055_SYS_ERR          = 0x3A
BNO055_UNIT_SEL         = 0x3B
BNO055_OPR_MODE         = 0x3D
BNO055_PWR_MODE         = 0x3E
BNO055_SYS_TRIGGER      = 0x3F
BNO055_TEMP_SOURCE      = 0x40
BNO055_AXIS_MAP_CONFIG  = 0x41
BNO055_AXIS_MAP_SIGN 	= 0x42
BNO055_ACC_OFFSET_X_LSB = 0x55
BNO055_ACC_OFFSET_X_MSB = 0x56
BNO055_ACC_OFFSET_Y_LSB = 0x57
BNO055_ACC_OFFSET_Y_MSB = 0x58
BNO055_ACC_OFFSET_Z_LSB = 0x59
BNO055_ACC_OFFSET_Z_MSB = 0x5A
BNO055_MAG_OFFSET_X_LSB = 0x5B
BNO055_MAG_OFFSET_X_MSB = 0x5C
BNO055_MAG_OFFSET_Y_LSB = 0x5D
BNO055_MAG_OFFSET_Y_MSB = 0x5E
BNO055_MAG_OFFSET_Z_LSB = 0x5F
BNO055_MAG_OFFSET_Z_MSB = 0x60
BNO055_GYR_OFFSET_X_LSB = 0x61
BNO055_GYR_OFFSET_X_MSB = 0x62
BNO055_GYR_OFFSET_Y_LSB = 0x63
BNO055_GYR_OFFSET_Y_MSB = 0x64
BNO055_GYR_OFFSET_Z_LSB = 0x65
BNO055_GYR_OFFSET_Z_MSB = 0x66
BNO055_ACC_RADIUS_LSB   = 0x67
BNO055_ACC_RADIUS_MSB   = 0x68
BNO055_MAG_RADIUS_LSB   = 0x69
BNO055_MAG_RADIUS_MSB   = 0x6A
# Page 1
BNO055_ACC_CONFIG 		= 0x08
BNO055_MAG_CONFIG 		= 0x09
BNO055_GYRO_CONFIG_0 	= 0x0A
BNO055_GYRO_CONFIG_1 	= 0x0B
BNO055_ACC_SLEEP_CONFIG = 0x0C
BNO055_GYR_SLEEP_CONFIG = 0x0D
BNO055_INT_MSK 			= 0x0F
BNO055_INT_EN 			= 0x10
BNO055_ACC_AM_THRES 	= 0x11
BNO055_ACC_INT_SETTINGS = 0x12
BNO055_ACC_HG_DURATION  = 0x13
BNO055_ACC_HG_THRESH    = 0x14
BNO055_ACC_NM_THRESH    = 0x15
BNO055_ACC_NM_SET 		= 0x16
BNO055_GYR_INT_SETTINGS = 0x17
BNO055_GYR_HR_X_SET 	= 0x18
BNO055_GYR_DUR_X 		= 0x19
BNO055_GYR_HR_Y_SET 	= 0x1A
BNO055_GYR_DUR_Y 		= 0x1B
BNO055_GYR_HR_Z_SET 	= 0x1C
BNO055_GYR_DUR_Z 		= 0x1D
BNO055_GYR_AM_THRESH 	= 0x1E
BNO055_GYR_AM_SET 		= 0x1F
# bno055_system_status_t
BNO055_SYSTEM_STATUS_IDLE                     = 0x00
BNO055_SYSTEM_STATUS_SYSTEM_ERROR             = 0x01
BNO055_SYSTEM_STATUS_INITIALIZING_PERIPHERALS = 0x02
BNO055_SYSTEM_STATUS_SYSTEM_INITIALIZATION    = 0x03
BNO055_SYSTEM_STATUS_EXECUTING_SELF_TEST      = 0x04
BNO055_SYSTEM_STATUS_FUSION_ALGO_RUNNING      = 0x05
BNO055_SYSTEM_STATUS_FUSION_ALOG_NOT_RUNNING  = 0x06
# bno055_vector_type_t
BNO055_VECTOR_ACCELEROMETER = 0x08  # Default: m / s²
BNO055_VECTOR_MAGNETOMETER  = 0x0E  # Default: uT
BNO055_VECTOR_GYROSCOPE     = 0x14  # Default: rad / s
BNO055_VECTOR_EULER         = 0x1A  # Default: degrees
BNO055_VECTOR_LINEARACCEL   = 0x28  # Default: m / s²
BNO055_VECTOR_GRAVITY       = 0x2E  # Default: m / s²
# bno055_system_error_t
BNO055_SYSTEM_ERROR_NO_ERROR                                         = 0x00
BNO055_SYSTEM_ERROR_PERIPHERAL_INITIALIZATION_ERROR                  = 0x01
BNO055_SYSTEM_ERROR_SYSTEM_INITIALIZATION_ERROR                      = 0x02
BNO055_SYSTEM_ERROR_SELF_TEST_FAILED                                 = 0x03
BNO055_SYSTEM_ERROR_REG_MAP_VAL_OUT_OF_RANGE                         = 0x04
BNO055_SYSTEM_ERROR_REG_MAP_ADDR_OUT_OF_RANGE                        = 0x05
BNO055_SYSTEM_ERROR_REG_MAP_WRITE_ERROR                              = 0x06
BNO055_SYSTEM_ERROR_LOW_PWR_MODE_NOT_AVAILABLE_FOR_SELECTED_OPR_MODE = 0x07
BNO055_SYSTEM_ERROR_ACCEL_PWR_MODE_NOT_AVAILABLE                     = 0x08
BNO055_SYSTEM_ERROR_FUSION_ALGO_CONF_ERROR                           = 0x09
BNO055_SYSTEM_ERROR_SENSOR_CONF_ERROR                                = 0x0A
bno055_vector_t = '>ddd'
bno055_sensor_t = '>cccccccccccciiifffi'
bno055_self_test_result_t = '>cccc'
bno055_calibration_state_t = '>cccc'
bno055_vector_xyz_int16_t = '>hhh'
bno055_calibration_offset_t = '>hhhhhhhhh'
bno055_calibration_radius_t = '>hh'


BNO055_FILTER_BW_256 = 0x00
BNO055_FILTER_BW_188 = 0x00
BNO055_FILTER_BW_98 = 0x00
BNO055_FILTER_BW_42 = 0x00
BNO055_FILTER_BW_20 = 0x00
BNO055_FILTER_BW_10 = 0x00
BNO055_FILTER_BW_5 = 0x00

BNO055_ACCEL_RANGE_2G = 0x00
BNO055_ACCEL_RANGE_4G = 0x00
BNO055_ACCEL_RANGE_8G = 0x00
BNO055_ACCEL_RANGE_16G = 0x00

BNO055_GYRO_RANGE_250DEG = 0x00
BNO055_GYRO_RANGE_500DEG = 0x00
BNO055_GYRO_RANGE_1000DEG = 0x00
BNO055_GYRO_RANGE_2000DEG = 0x00


BNO055_ACCEL_SCALE_MODIFIER_2G = 16384.0
BNO055_ACCEL_SCALE_MODIFIER_4G = 8192.0
BNO055_ACCEL_SCALE_MODIFIER_8G = 4096.0
BNO055_ACCEL_SCALE_MODIFIER_16G = 2048.0
BNO055_GYRO_SCALE_MODIFIER_250DEG = 131.0
BNO055_GYRO_SCALE_MODIFIER_500DEG = 65.5
BNO055_GYRO_SCALE_MODIFIER_1000DEG = 32.8
BNO055_GYRO_SCALE_MODIFIER_2000DEG = 16.4