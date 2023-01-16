C_REG_A = 0x09  # Address of Configuration register A
C_REG_B = 0x0a  # Address of configuration register B
SR_period_REG = 0x0b  # Address of SER/RESET register

MODE_STBY = 0x00  # standby mode
MODE_CONT = 0x01  # continous mode

ODR_10Hz = 0x00  # output data rate 10Hz
ODR_50Hz = 0x01  # output data rate 50Hz
ODR_100Hz = 0x10  # output data rate 100Hz
ODR_200Hz = 0x11  # output data rate 200Hz

SENS_2G = 0x00  # magnetic field sensitivity 2G
SENS_8G = 0x01  # magnetic field sensitivity 8G

OSR_512 = 0x00  # oversampling rate 512
OSR_256 = 0x01  # oversampling rate 256
OSR_128 = 0x10  # oversampling rate 128
OSR_64 = 0x11  # oversampling rate 64

X_axis_H = 0x00  # Address of X-axis MSB data register
Z_axis_H = 0x02  # Address of Z-axis MSB data register
Y_axis_H = 0x04  # Address of Y-axis MSB data register
TEMP_REG = 0x07  # Address of Temperature MSB data register

# declination angle of location where measurement going to be done
CURR_DECL = -0.00669  # determine by yourself