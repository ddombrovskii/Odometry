from constants import *
from time import sleep
from math import pi
import math


class BusDummy:
    def __init__(self):
        pass

    def SMBus(self, a: int):
        return self

    def write_byte_data(self, a: int, b: int, c: int):
        pass

    def read_byte_data(self, a: int, b: int):
        return 0


try:
    import smbus
# TODO add board version check
except ImportError as ex:
    smbus = BusDummy()
    print(f"SM Bus import error!!!\n{ex.args}")


class Compass:

    """
    Диапазоны измеряемых ускорений
    """
    __compass_modes = {0: MODE_CONT,
                       1: MODE_STBY}
    """
    Диапазоны измеряемых ускорений
    """
    __compass_read_rate_hz = {10:  ODR_10Hz,
                              50:  ODR_50Hz,
                              100: ODR_100Hz,
                              200: ODR_200Hz }
    """
    Модификаторы масштаба для ускорений
    """
    __compass_sensitivity = {2: SENS_2G,
                             8: SENS_8G}
    """
    Диапазоны измеряемых угловых скоростей
    """
    __compas_oversampling_rate  = {512: OSR_512,
                                   256: OSR_256,
                                   128: OSR_128,
                                   64: OSR_64}

    # Control register 2 - Addr 0x0A
    # 7		6		5	4	3	2	1	0
    # SOFT_RST	ROL_PNT		-	-	-	-	-	INT_ENB
    # INT_EN
    # https://github.com/texperiri/GY-271-QMC5883/blob/master/qmc5883.py

    def __init__(self, address=0x0d, mode=MODE_CONT, odr=ODR_10Hz, sens=SENS_2G, osr=OSR_512, d=CURR_DECL):
        self.bus = smbus.SMBus(1)
        self.device_address = address  # magnetometer device i2c address
        self._declination = d
        self.magnetometer_init(mode, odr, sens, osr)
        sleep(2)

    def soft_reset(self):
        self.bus.write_byte_data(self.device_address, C_REG_B, 0x80)

    def __set_mode(self, mode, odr, sens, osr):
        value = mode | odr | sens | osr
        return value

    def magnetometer_init(self, mode, odr, sens, osr):
        self.soft_reset()

        self._mode = self.__set_mode(mode, odr, sens, osr)

        # Write to Configuration Register B: normal 0x00, soft_reset: 0x80
        self.bus.write_byte_data(self.device_address, C_REG_B, 0x00)

        # SET/RESET period set to 0x01 (recommendation from datasheet)
        self.bus.write_byte_data(self.device_address, SR_period_REG, 0x01)

        # write to Configuration Register A: mode
        self.bus.write_byte_data(self.device_address, C_REG_A, self._mode)

    def __read_raw_data(self, reg_address):
        # Read raw 16-bit value
        low_byte = self.bus.read_byte_data(self.device_address, reg_address)
        high_byte = self.bus.read_byte_data(self.device_address, reg_address + 1)

        # concatenate high_byte and low_byte into two_byte data
        value = (high_byte << 8) | low_byte

        if value > 32767:
            value = value - 65536

        return value

    def get_bearing(self):
        # Read Accelerometer raw value
        x = self.__read_raw_data(X_axis_H)
        z = self.__read_raw_data(Z_axis_H)
        y = self.__read_raw_data(Y_axis_H)

        heading = math.atan2(y, x) + self._declination

        # due to declination check for >360 degree
        if heading > 2.0 * math.pi:
            heading = heading - 2.0 * pi

        # check for sign
        if heading < 0.0:
            heading = heading + 2.0 * pi

        # convert into angle
        heading_angle = int(heading * 180.0 / pi)
        return heading_angle

    def read_temp(self):
        low_byte = self.bus.read_byte_data(self.device_address, TEMP_REG)
        high_byte = self.bus.read_byte_data(self.device_address, TEMP_REG + 1)

        # concatenate higher and lower value
        value = (high_byte << 8) | low_byte  # signed int (-32766 : 32767)
        value = value & 0x3fff  # to get only positive numbers (first bit, sign bit)
        value = value / 520.0  # around: 125 (temp range) times 100 LSB/*C ~ 520
        return value

    def set_declination(self, value):
        self._declination = value