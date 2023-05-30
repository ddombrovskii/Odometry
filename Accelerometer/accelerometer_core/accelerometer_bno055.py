from Accelerometer.accelerometer_core.accelerometer_base import AccelerometerBase
from .accelerometer_constants import *
from serial.tools import list_ports
from typing import Tuple, Any
import struct
import serial
import time

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
        return UART_EMPTY_MESSAGE
    while serial_port.read(2) != UART_START_MESSAGE:
        if serial_port.in_waiting != 0:
            continue
        return UART_EMPTY_MESSAGE
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


class AccelerometerBNO055(AccelerometerBase):
    """
    Диапазоны измеряемых ускорений
    """
    _filter_ranges = {256: BNO055_FILTER_BW_256,
                      188: BNO055_FILTER_BW_188,
                      98:  BNO055_FILTER_BW_98,
                      42:  BNO055_FILTER_BW_42,
                      20:  BNO055_FILTER_BW_20,
                      10:  BNO055_FILTER_BW_10,
                      5:   BNO055_FILTER_BW_5}
    """
    Диапазоны измеряемых ускорений
    """
    _acc_ranges = {2:  BNO055_ACCEL_RANGE_2G,
                   4:  BNO055_ACCEL_RANGE_4G,
                   8:  BNO055_ACCEL_RANGE_8G,
                   16: BNO055_ACCEL_RANGE_16G}
    """
    Модификаторы масштаба для ускорений
    """
    _acc_scales = {BNO055_ACCEL_RANGE_2G:  BNO055_ACCEL_SCALE_MODIFIER_2G,
                   BNO055_ACCEL_RANGE_4G:  BNO055_ACCEL_SCALE_MODIFIER_4G,
                   BNO055_ACCEL_RANGE_8G:  BNO055_ACCEL_SCALE_MODIFIER_8G,
                   BNO055_ACCEL_RANGE_16G: BNO055_ACCEL_SCALE_MODIFIER_16G}
    """
    Диапазоны измеряемых угловых скоростей
    """
    _gyro_ranges = {250:  BNO055_ACCEL_RANGE_2G,
                    500:  BNO055_ACCEL_RANGE_4G,
                    1000: BNO055_ACCEL_RANGE_8G,
                    2000: BNO055_ACCEL_RANGE_16G}
    """
    Модификаторы масштаба для угловых скоростей
    """
    _gyro_scales = {BNO055_GYRO_RANGE_250DEG:  BNO055_GYRO_SCALE_MODIFIER_250DEG,
                    BNO055_GYRO_RANGE_500DEG:  BNO055_GYRO_SCALE_MODIFIER_500DEG,
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

    def _request_for_device_connection(self) -> bool:
        try:
            ports = list_ports.comports()
            [print(p) for p in ports]
            target_port = None
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

            self._device_connection = serial.Serial('COM3', baudrate=115200,
                                           timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE)
            return True
        except RuntimeError as err:
            return False

    def _request_for_device_disconnection(self) -> bool:
        if "_device_connection" in self.__dict__:
            if self._device_connection is None:
                return False
            self._device_connection.close()
            return True
        return False

    def _device_read_request(self) -> Tuple[bool, Tuple[float, ...]]:
        # TODO сделать асинхронным, добавить ожидание результата со стороны BNO в течении какого-то, по истечении
        #  которого ничего не возвращать.
        message = self.read_config.to_bytes(1, 'big')
        write_package(self.device, message)
        # time.sleep(0.01)
        response = read_package(self.device)
        if len(response) == 0:
            return False, (0.0,)
        self._status = response[0]
        if self._status != 1:
            return False, (0.0, )
        response = response[1:len(response) - (len(response) - 1) % 8]
        try:
            response = struct.unpack(f'<{len(response) // 8}d', response)
        except ValueError as error:
            print(f"AccelerometerBase :: data parce error\n{error.args}")
            return False, (0.0, )

        return True, response

    def __init__(self):
        super().__init__()

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


if __name__ == '__main__':
    acc = AccelerometerBNO055()
    acc.use_filtering = True
    # acc.record('record_bno_test.json')  # запись в файл
    # acc.calibrate_request()
    for _ in range(10):
        acc.read_request()
        print(acc)
        time.sleep(.50)
