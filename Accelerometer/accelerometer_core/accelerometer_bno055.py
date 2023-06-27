from .accelerometer_base import AccelerometerBase
from .accelerometer_constants import *
from serial.tools import list_ports
from typing import Tuple, Any, List
from time import sleep
import struct
import serial
# import smbus

UART_START_MESSAGE = b'$#'
UART_END_MESSAGE = b'#$'
UART_EMPTY_MESSAGE = b'$##$'


def read_package(serial_port: serial.Serial) -> bytes:
    """
    Читает пакет данных по UART с признаками начала и конца b'$#', b'#$' соответственно
    :param serial_port: UART порт
    :return: b'$#...Данные...#$' или пустой пакет b'$##$'
    """
    if serial_port.in_waiting == 0:
        return b''
    while serial_port.read(2) != UART_START_MESSAGE:
        if serial_port.in_waiting != 0:
            continue
        break
    res = serial_port.read_until(UART_END_MESSAGE)
    return res[:-2]


def _template_read_package(serial_port: serial.Serial, value_type: str = 'i',
                           size_of: int = 4, endian: str = '>') -> Tuple[Any, ...]:
    raw_data = read_package(serial_port)
    if len(raw_data) == 0:
        return 0,
    raw_data = raw_data[:len(raw_data) - len(raw_data) % size_of]
    return struct.unpack(f'{endian}{len(raw_data) // size_of}{value_type}', raw_data)


def read_int_package(serial_port) -> Tuple[int, ...]:
    """
    Читает пакет данных по UART с признаками начала и конца b'$#', b'#$' соответственно и приводит их к кортежу из
     целочисленных значений.
    :param serial_port: UART порт.
    :return: кортеж из целочисленных значений.
    """
    return _template_read_package(serial_port, 'i', size_of=4)


def read_float_package(serial_port) -> Tuple[float, ...]:
    """
    Читает пакет данных по UART с признаками начала и конца b'$#', b'#$' соответственно и приводит их к кортежу из
     значений с плавающей точкой.
    :param serial_port: UART порт.
    :return: кортеж из значений с плавающей точкой.
    """
    return _template_read_package(serial_port, 'f', size_of=4)


def write_package(serial_port, message: bytes):
    """
    Пишет в UART порт сообщение в виде массива из HEX значений.  Признаками начала и конца b'$#', b'#$'
     выставляются автоматически.
    :param serial_port:
    :param message:
    """
    serial_port.write(UART_START_MESSAGE)
    serial_port.write(message)
    serial_port.write(UART_END_MESSAGE)


def _template_write_package(serial_port, message: Tuple[Any, ...], value_type: str = 'i', endian: str = '>'):
    write_package(serial_port, struct.pack(f'{endian}{len(message)}{value_type}', *message))


def write_int_package(serial_port, message: Tuple[int, ...]) -> None:
    """
    Пишет в UART порт сообщение в виде массива из целочисленных значений.  Признаками начала и конца b'$#', b'#$'
     выставляются автоматически.
    :param serial_port:
    :param message:
    """
    _template_write_package(serial_port, message, 'i')


def write_float_package(serial_port, message: Tuple[float, ...]) -> None:
    """
    Пишет в UART порт сообщение в виде массива значений с плавающей точкой.  Признаками начала и конца b'$#', b'#$'
     выставляются автоматически.
    :param serial_port:
    :param message:
    """
    _template_write_package(serial_port, message, 'f')


def read_block(self, register: int, block_size: int = 3, type_size: int = 2) -> Tuple[bool, Tuple[float, ...]]:
    try:
        buf = self._read_bytes(register, block_size * type_size)
        raw_vec = tuple(map(lambda a: a if a < 0x8000 else a - 65536, struct.unpack(f'>{block_size}h', buf)))
        # raw_vec = struct.unpack(f"{block_size}{self.data_size_map[type_size]}", struct.pack(f"{len(buf)}B", *buf))
        return True, raw_vec
    except struct.error as _:
        # raise Exception("Error while reading vector") from struct_err
        return False, tuple(0.0 for _ in range(block_size))


class AccelerometerBNO055(AccelerometerBase):
    """
    Диапазоны измеряемых ускорений
    """
    _filter_ranges = {256: BNO055_FILTER_BW_256,
                      188: BNO055_FILTER_BW_188,
                      98: BNO055_FILTER_BW_98,
                      42: BNO055_FILTER_BW_42,
                      20: BNO055_FILTER_BW_20,
                      10: BNO055_FILTER_BW_10,
                      5: BNO055_FILTER_BW_5}
    """
    Диапазоны измеряемых ускорений
    """
    _acc_ranges = {2: BNO055_ACCEL_RANGE_2G,
                   4: BNO055_ACCEL_RANGE_4G,
                   8: BNO055_ACCEL_RANGE_8G,
                   16: BNO055_ACCEL_RANGE_16G}
    """
    Модификаторы масштаба для ускорений
    """
    _acc_scales = {BNO055_ACCEL_RANGE_2G: BNO055_ACCEL_SCALE_MODIFIER_2G,
                   BNO055_ACCEL_RANGE_4G: BNO055_ACCEL_SCALE_MODIFIER_4G,
                   BNO055_ACCEL_RANGE_8G: BNO055_ACCEL_SCALE_MODIFIER_8G,
                   BNO055_ACCEL_RANGE_16G: BNO055_ACCEL_SCALE_MODIFIER_16G}
    """
    Диапазоны измеряемых угловых скоростей
    """
    _gyro_ranges = {250: BNO055_ACCEL_RANGE_2G,
                    500: BNO055_ACCEL_RANGE_4G,
                    1000: BNO055_ACCEL_RANGE_8G,
                    2000: BNO055_ACCEL_RANGE_16G}
    """
    Модификаторы масштаба для угловых скоростей
    """
    _gyro_scales = {BNO055_GYRO_RANGE_250DEG: BNO055_GYRO_SCALE_MODIFIER_250DEG,
                    BNO055_GYRO_RANGE_500DEG: BNO055_GYRO_SCALE_MODIFIER_500DEG,
                    BNO055_GYRO_RANGE_1000DEG: BNO055_GYRO_SCALE_MODIFIER_1000DEG,
                    BNO055_GYRO_RANGE_2000DEG: BNO055_GYRO_SCALE_MODIFIER_2000DEG}
    """
    Акселерометр основанный на чипе bno0550. Читает ускорения, угловые скорости, углы.
                     Протокол управления акселерометром BNO055.
    Параметры пакета:
        1. Начало пакета: b'$#'.
        2. Конец пакета: b'#$'.

    Форма пакета запроса состоит из начала пакета, байта запроса к акселерометру,
    двух байт сообщения системе управления и конца пакета.

    # Запросы к акселерометру:                  # не используется
    #	Префикс устройства:                     # не используется
    #	b'x\00' (не используется, но желателен) # не используется

    Запрос к акселерометру:
        |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|
        |      bin      |   hex   |              Описание                    |
        |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|
        | 0xb 0000 0001 | b'x\01' | Ускорение.                               |
        | 0xb 0000 0010 | b'x\02' | Угловые скорости.                        |
        | 0xb 0000 0100 | b'x\04' | Углы эйлера.                             |
        | 0xb 0000 1000 | b'x\08' | Кватернион.                              |
        | 0xb 0001 0000 | b'x\10' | Данные магнетометра.                     |
        | 0xb 0010 0000 | b'x\20' | Линейное ускорение(без вектора g).       |
        | 0xb 0100 0000 | b'x\40' | Запрос на калибровку.                    |
        | 0xb 1000 0000 | b'x\80' | Запрос на статус.                        |
        |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|

    Пример запроса на ускорение, углы эйлера и линейное ускорение:
        |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|
        |      bin      |   hex   |                 Описание                 |
        |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|
        | 0xb 0010 0101 | b'x\25' | Ускорение | Углы эйлера | Лин. ускорение |
        |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|

    Пример возвращаемых данных:
        b'$#01&*JH*(K ... (*HKJNL#$'
        В случае запроса ускорение | углы эйлера | лин. ускорение пакет будет
        состоять из 1(байт статуса) + 3(вектора) * 3(координаты вектора) *
        * 8(байт на число) байт, плюс 2 байта на символы начала и 2 байта на
        символы конца.

    Байты статуса:
        |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|
        |      bin      |   hex   |              Описание                    |
        |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|
        | 0xb 0000 0000 | b'x\00' | Готов к чтению измерений.                |
        | 0xb 0000 0001 | b'x\01' | Данные успешно прочитаны.                |
        | 0xb 0000 0010 | b'x\02' | Акселерометр в процессе калибровки,      |
        |			    |		  | чтение недоступно.                       |
        | 0xb 0000 0011 | b'x\03' | Ошибка чтения.                           |
        |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|
    """
    STATUS_READY = b'\x00'
    STATUS_DATA_CAPTURED = b'\x01'
    STATUS_CALIBRATION = b'\x02'
    STATUS_ERROR = b'\x03'

    # i2c registers
    BNO055_ADDRESS = 0x28
    BNO055_ID = 0xA0

    BNO055_CHIP_ID_ADDR = 0x00
    BNO055_SYS_TRIGGER_ADDR = 0X3F
    BNO055_PWR_MODE_ADDR = 0X3E
    BNO055_PAGE_ID_ADDR = 0X07
    BNO055_OPR_MODE_ADDR = 0x3D

    OPERATION_MODE_CONFIG = 0x00
    POWER_MODE_NORMAL = 0X00
    OPERATION_MODE_NDOF = 0X0C

    # Output vector types
    _VECTOR_EULER = 0x1A
    _VECTOR_GYROSCOPE = 0x14
    _VECTOR_MAGNETOMETER = 0x0E
    _VECTOR_ACCELEROMETER = 0x08
    _VECTOR_LINEAR_ACCEL = 0x28
    _VECTOR_QUATERNION = 0X20
    _VECTOR_GRAVITY = 0x2E

    # Scale values, see 3.6.5.5 in the datasheet.
    _EULER_SCALE = 1.0 / 16.0
    _GYROSCOPE_SCALE = 1.0 / 900.0
    _MAGNETOMETER_SCALE = 1.0 / 16.0
    _ACCELEROMETER_SCALE = 1.0 / 100.0
    _LINEAR_ACCEL_SCALE = 1.0 / 100.0
    _QUATERNION_SCALE = (1.0 / (1 << 14))
    _GRAVITY_SCALE = 1.0 / 100.0
    _DATA_SIZE_MAP = {2: "h", 4: "f", 8: "d"}

    def __init__(self):
        super().__init__()

    def _read_bytes(self, register: int, bytes_count: int = 1) -> bytes:
        try:
            return self.device.read_i2c_block_data(self.BNO055_ADDRESS, register, bytes_count)
        except OSError as _:
            return b''

    def _write_bytes(self, register: int, bytes_data: List) -> None:
        self.device.write_i2c_block_data(self.BNO055_ADDRESS, register, bytes_data)

    def _set_mode(self, mode) -> None:
        self._write_bytes(self.BNO055_OPR_MODE_ADDR, [mode])
        sleep(0.03)

    def _read_block(self, register: int, block_size: int = 3, type_size: int = 2) -> Tuple[bool, Tuple[float, ...]]:
        try:
            buf = self._read_bytes(register, block_size * type_size)

            raw_vec = tuple(map(lambda a: a if a < 0x8000 else a - 65536,
                                struct.unpack(f'{block_size}h', struct.pack(f"{len(buf)}B", *buf))))
            return True, raw_vec
        except struct.error as _:
            return False, tuple(0.0 for _ in range(block_size))

    def _request_for_device_connection(self) -> bool:
        try:
            # ports = list_ports.comports()
            # [print(p) for p in ports]
            # target_port = None
            # for p in ports:
            #     with serial.Serial(p.device, baudrate=115200,
            #                        timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE) as target:
            #        write_package(target, b'TEST')
            #        time.sleep(0.1)
            #        package = read_package(target)
            #        if package != b'TEST':
            #            continue
            #        target_port = p.device
            #        break

            # if target_port is None:
            #     raise RuntimeError("BNO055 is not connected...")

            # self._device_connection = serial.Serial('COM5', baudrate=115200,
            #                                timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE)

            # Make sure we have the right device
            self._device_connection = smbus.SMBus(1)
            if self._read_bytes(self.BNO055_CHIP_ID_ADDR)[0] != self.BNO055_ID:
                sleep(1)  # Wait for the device to boot up
                if self._read_bytes(self.BNO055_CHIP_ID_ADDR)[0] != self.BNO055_ID:
                    return False

            # Switch to config mode
            self._set_mode(self.OPERATION_MODE_CONFIG)

            # Trigger a reset and wait for the device to boot up again
            self._write_bytes(self.BNO055_SYS_TRIGGER_ADDR, [0x20])
            sleep(1)

            while self._read_bytes(self.BNO055_CHIP_ID_ADDR)[0] != self.BNO055_ID:
                sleep(0.01)
            sleep(0.05)

            # Set to normal power mode
            self._write_bytes(self.BNO055_PWR_MODE_ADDR, [self.POWER_MODE_NORMAL])
            sleep(0.01)

            self._write_bytes(self.BNO055_PAGE_ID_ADDR, [0])
            self._write_bytes(self.BNO055_SYS_TRIGGER_ADDR, [0])
            sleep(0.01)

            # Set the requested mode
            self._set_mode(self.OPERATION_MODE_NDOF)
            sleep(0.02)

            return True
        except RuntimeError as _:
            return False
        except TimeoutError as _:
            return False
        except NameError as _:
            return False

    def _device_read_request(self, vec_type=_VECTOR_GRAVITY) -> Tuple[bool, Tuple[float, ...]]:
        # if self.device.in_waiting == 0:
        #     message = self.read_config.to_bytes(1, 'big')
        #     write_package(self.device, b'\x00,' + message)
        #     return False, (0.0,)

        # if self.device.in_waiting < self.package_bytes_count+ 7:  # + 4 + 3:
        #     return False, (0.0,)

        # response = read_package(self.device)

        # if len(response) == 0:
        #     return False, (0.0,)

        # if response[0] != 0:
        #     return False, (0.0,)

        # message = self.read_config.to_bytes(1, 'big')
        # write_package(self.device, b'\x00,' + message)

        # try:
        #     self._status = response[2]
        #     if self._status != 1:
        #         return False, (0.0,)
        #     response = response[3:]
        #     response = response[0: len(response) - len(response) % 8]
        # except IndexError as err:
        #     return False, (0.0, )

        # try:
        #     response = struct.unpack(f'<{len(response) // 8}d', response)
        # except ValueError as error:
        #     print(f"AccelerometerBase :: data parce error\n{error.args}")
        #     return False, (0.0, )

        status = False

        response = []

        if self.is_accel_read:
            flag, (x, y, z) = self._read_block(AccelerometerBNO055._VECTOR_ACCELEROMETER, 3)
            response.extend((x * AccelerometerBNO055._ACCELEROMETER_SCALE,
                             y * AccelerometerBNO055._ACCELEROMETER_SCALE,
                             z * AccelerometerBNO055._ACCELEROMETER_SCALE))
            status |= flag

        if self.is_omega_read:
            flag, (x, y, z) = self._read_block(AccelerometerBNO055._VECTOR_GYROSCOPE, 3)
            response.extend((x * AccelerometerBNO055._GYROSCOPE_SCALE,
                             y * AccelerometerBNO055._GYROSCOPE_SCALE,
                             z * AccelerometerBNO055._GYROSCOPE_SCALE))
            status |= flag

        if self.is_angles_read:
            flag, (x, y, z) = self._read_block(AccelerometerBNO055._VECTOR_EULER, 3)
            response.extend((x * AccelerometerBNO055._EULER_SCALE,
                             y * AccelerometerBNO055._EULER_SCALE,
                             z * AccelerometerBNO055._EULER_SCALE))
            status |= flag

        if self.is_quaternion_read:
            flag, (x, y, z, w) = self._read_block(AccelerometerBNO055._VECTOR_QUATERNION, 4)
            response.extend((x * AccelerometerBNO055._QUATERNION_SCALE,
                             y * AccelerometerBNO055._QUATERNION_SCALE,
                             z * AccelerometerBNO055._QUATERNION_SCALE,
                             w * AccelerometerBNO055._QUATERNION_SCALE))
            status |= flag

        if self.is_magnetometer_read:
            flag, (x, y, z) = self._read_block(AccelerometerBNO055._VECTOR_MAGNETOMETER, 3)
            response.extend((x * AccelerometerBNO055._MAGNETOMETER_SCALE,
                             y * AccelerometerBNO055._MAGNETOMETER_SCALE,
                             z * AccelerometerBNO055._MAGNETOMETER_SCALE))
            status |= flag

        if self.is_lin_accel_read:
            flag, (x, y, z) = self._read_block(AccelerometerBNO055._VECTOR_LINEAR_ACCEL, 3)
            response.extend((x * AccelerometerBNO055._LINEAR_ACCEL_SCALE,
                             y * AccelerometerBNO055._LINEAR_ACCEL_SCALE,
                             z * AccelerometerBNO055._LINEAR_ACCEL_SCALE))
            status |= flag

        return status, tuple(response)

    @property
    def acceleration_range_key(self) -> int:
        return self._accel_range_key

    @acceleration_range_key.setter
    def acceleration_range_key(self, accel_range: int) -> None:
        """
        Диапазон измеряемых ускорений
        ACCEL_SCALE_MODIFIER_2G  = 16384.0
        ACCEL_SCALE_MODIFIER_4G  = 8192.0
        ACCEL_SCALE_MODIFIER_8G  = 4096.0
        ACCEL_SCALE_MODIFIER_16G = 2048.0
        """
        if accel_range not in AccelerometerBNO055._acc_ranges:
            return
        self._accel_range_key = accel_range
        self._accel_range_val = AccelerometerBNO055._acc_ranges[self._accel_range_key]
        # self.bus.write_byte_data(self.address, MPU6050_ACCEL_CONFIG, 0x00)
        # self.bus.write_byte_data(self.address, MPU6050_ACCEL_CONFIG, self._acceleration_range_raw)

    @property
    def acceleration_range(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return self._accel_range_val * GRAVITY_CONSTANT

    @property
    def acceleration_scale(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return AccelerometerBNO055._acc_scales[self.acceleration_range_key]

    @property
    def gyroscope_range_key(self) -> int:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG  = 0x00
        GYRO_RANGE_500DEG  = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        return self._gyro_range_key

    @gyroscope_range_key.setter
    def gyroscope_range_key(self, gyro_range: int) -> None:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG  = 0x00
        GYRO_RANGE_500DEG  = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        if gyro_range not in AccelerometerBNO055._gyro_ranges:
            return
        self._gyro_range_key = gyro_range
        self._gyro_range_val = AccelerometerBNO055._gyro_ranges[self._gyro_range_key]
        # self.bus.write_byte_data(self.address, MPU6050_GYRO_CONFIG, 0x00)
        # self.bus.write_byte_data(self.address, MPU6050_GYRO_CONFIG, self._gyroscope_range_raw)

    @property
    def gyroscope_range(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return float(self._gyro_range_val)

    @property
    def gyroscope_scale(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return AccelerometerBNO055._gyro_scales[self.gyroscope_range_key]

