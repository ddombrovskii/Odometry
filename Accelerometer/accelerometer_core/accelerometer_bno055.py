from Utilities.Geometry import Vector3, Quaternion
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


def _is_bit_set(bytes_: int, bit_: int) -> bool:
    return (bytes_ & (1 << bit_)) != 0


def _set_bit(bytes_: int, bit_: int) -> int:
    bytes_ |= (1 << bit_)
    return bytes_


def _clear_bit(bytes_: int, bit_: int) -> int:
    bytes_ &= ~(1 << bit_)
    return bytes_


def _device_progres_bar(val: float, label: str = "", max_chars: int = 55,
                       char_progress: str = '#', char_stand_by: str = '.') -> str:
    filler_l = int(min(max(0.0, val), 1.0) * max_chars)  # max_chars - title chars count
    filler_r = max_chars - filler_l
    if len(label) == 0:
        return f'\r|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|' if filler_r != 0 else \
            f'\r|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|\n'

    return f'\r|{label:15}|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|' if filler_r != 0 else \
        f'\r|{label:15}|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|\n'


TIME = "\"time\""
DTIME = "\"dtime\""
ACCELERATION = "\"acceleration\""
QUATERNION = "\"quaternion\""
ACCELERATION_LIN = "\"acceleration_linear\""
VELOCITY = "\"velocity\""
POSITION = "\"position\""
ANGLES_VELOCITY = "\"angles_velocity\""
ANGLES = "\"angles\""
MAGNETOMETER = "\"magnetometer\""
DEVICE_NAME = "\"device_name\""
LOG_TIME_START = "\"log_time_start\""
WAY_POINTS = "\"way_points\""


class AccelerometerBNO055:
    """
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
    ACCELERATION_BIT = 0
    OMEGA_BIT = 1
    ANGLES_BIT = 2
    QUATERNION_BIT = 3
    MAGNETOMETER_BIT = 4
    ACCELERATION_LINEAR_BIT = 5
    CALIBRATION_BIT = 6
    STATUS_BIT = 7

    STATUS_READY = b'\x00'
    STATUS_DATA_CAPTURED = b'\x01'
    STATUS_CALIBRATION = b'\x02'
    STATUS_ERROR = b'\x03'

    def __init__(self):
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

        self._bno_port = serial.Serial('COM7', baudrate=115200,
                                       timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE)

        self._accel_curr = Vector3(0, 0, 0)
        self._accel_prev = Vector3(0, 0, 0)

        self._accel_lin_curr = Vector3(0, 0, 0)
        self._accel_lin_prev = Vector3(0, 0, 0)

        self._omega_curr = Vector3(0, 0, 0)
        self._omega_prev = Vector3(0, 0, 0)

        self._magneto_curr = Vector3(0, 0, 0)
        self._magneto_prev = Vector3(0, 0, 0)

        self._angle_curr = Vector3(0, 0, 0)
        self._angle_prev = Vector3(0, 0, 0)

        self._quat_curr = Quaternion(0, 0, 0, 0)
        self._quat_prev = Quaternion(0, 0, 0, 0)

        self._curr_t = -1.0
        self._prev_t = -1.0

        self._status = 0
        self._read_config = 0
        self.is_accel_read = True
        self.is_omega_read = True
        self.is_angles_read = True
        self.is_lin_accel_read = True
        self.is_quaternion_read = True

    def __str__(self):

        data = [f"\t{DTIME:22}: {str(self.delta_t)}"]

        if _is_bit_set(self._read_config, AccelerometerBNO055.ACCELERATION_BIT):
            data.append(f"\t{ACCELERATION:22}: {str(self.acceleration)}")

        if _is_bit_set(self._read_config, AccelerometerBNO055.OMEGA_BIT):
            data.append(f"\t{ANGLES_VELOCITY:22}: {str(self.omega)}")

        if _is_bit_set(self._read_config, AccelerometerBNO055.ANGLES_BIT):
            data.append(f"\t{ANGLES:22}: {str(self.angles)}")

        if _is_bit_set(self._read_config, AccelerometerBNO055.QUATERNION_BIT):
            data.append(f"\t{QUATERNION:22}: {str(self.quaternion)}")

        if _is_bit_set(self._read_config, AccelerometerBNO055.MAGNETOMETER_BIT):
            data.append(f"\t{MAGNETOMETER:22}: {str(self.magnetometer)}")

        if _is_bit_set(self._read_config, AccelerometerBNO055.ACCELERATION_LINEAR_BIT):
            data.append(f"\t{ACCELERATION_LIN:22}: {str(self.acceleration_linear)}")

        sep = ',\n'

        return f" {{\n{sep.join(val for val in data)}\n }}"

    def __del__(self):
        if "_bno_port" in self.__dict__:
            self._bno_port.close()

    @property
    def current_time(self) -> float:
        return self._curr_t

    @property
    def delta_t(self) -> float:
        return self._curr_t - self._prev_t

    @property
    def read_config(self) -> int:
        return self._read_config

    @property
    def is_accel_read(self) -> bool:
        return _is_bit_set(self.read_config, AccelerometerBNO055.ACCELERATION_BIT)

    @property
    def is_lin_accel_read(self) -> bool:
        return _is_bit_set(self.read_config, AccelerometerBNO055.ACCELERATION_LINEAR_BIT)

    @property
    def is_omega_read(self) -> bool:
        return _is_bit_set(self.read_config, AccelerometerBNO055.OMEGA_BIT)

    @property
    def is_angles_read(self) -> bool:
        return _is_bit_set(self.read_config, AccelerometerBNO055.ANGLES_BIT)

    @property
    def is_quaternion_read(self) -> bool:
        return _is_bit_set(self.read_config, AccelerometerBNO055.QUATERNION_BIT)

    @property
    def is_magnetometer_read(self) -> bool:
        return _is_bit_set(self.read_config, AccelerometerBNO055.MAGNETOMETER_BIT)

    @is_accel_read.setter
    def is_accel_read(self, val: bool) -> None:
        self._read_config = _set_bit(self.read_config, AccelerometerBNO055.ACCELERATION_BIT) if val else \
            _clear_bit(self.read_config, AccelerometerBNO055.ACCELERATION_BIT)

    @is_lin_accel_read.setter
    def is_lin_accel_read(self, val: bool) -> None:
        self._read_config = _set_bit(self.read_config, AccelerometerBNO055.ACCELERATION_LINEAR_BIT) if val else \
            _clear_bit(self.read_config, AccelerometerBNO055.ACCELERATION_LINEAR_BIT)

    @is_omega_read.setter
    def is_omega_read(self, val: bool) -> None:
        self._read_config = _set_bit(self.read_config, AccelerometerBNO055.OMEGA_BIT) if val else \
            _clear_bit(self.read_config, AccelerometerBNO055.OMEGA_BIT)

    @is_angles_read.setter
    def is_angles_read(self, val: bool) -> None:
        self._read_config = _set_bit(self.read_config, AccelerometerBNO055.ANGLES_BIT) if val else \
            _clear_bit(self.read_config, AccelerometerBNO055.ANGLES_BIT)

    @is_quaternion_read.setter
    def is_quaternion_read(self, val: bool) -> None:
        self._read_config = _set_bit(self.read_config, AccelerometerBNO055.QUATERNION_BIT) if val else \
            _clear_bit(self.read_config, AccelerometerBNO055.QUATERNION_BIT)

    @is_magnetometer_read.setter
    def is_magnetometer_read(self, val: bool) -> None:
        self._read_config = _set_bit(self.read_config, AccelerometerBNO055.MAGNETOMETER_BIT) if val else \
            _clear_bit(self.read_config, AccelerometerBNO055.MAGNETOMETER_BIT)

    @property
    def acceleration(self) -> Vector3:
        return self._accel_curr

    @property
    def acceleration_linear(self) -> Vector3:
        return self._accel_lin_curr

    @property
    def omega(self) -> Vector3:
        return self._omega_curr

    @property
    def angles(self) -> Vector3:
        return self._angle_curr

    @property
    def quaternion(self) -> Quaternion:
        return self._quat_curr

    @property
    def magnetometer(self) -> Vector3:
        return self._magneto_curr

    @property
    def config_info(self) -> str:
        config = []
        if _is_bit_set(self.read_config, AccelerometerBNO055.ACCELERATION_BIT):
            config.append('\t\"Accelerations\": true')
        else:
            config.append('\t\"Accelerations\": false')

        if _is_bit_set(self.read_config, AccelerometerBNO055.OMEGA_BIT):
            config.append('\t\"Omegas\": true')
        else:
            config.append('\t\"Omegas\": false')

        if _is_bit_set(self.read_config, AccelerometerBNO055.ANGLES_BIT):
            config.append('\t\"Angles\": true')
        else:
            config.append('\t\"Angles\": false')

        if _is_bit_set(self.read_config, AccelerometerBNO055.QUATERNION_BIT):
            config.append('\t\"Quaternion\": true')
        else:
            config.append('\t\"Quaternion\": false')

        if _is_bit_set(self.read_config, AccelerometerBNO055.MAGNETOMETER_BIT):
            config.append('\t\"Magnetometer\": true')
        else:
            config.append('\t\"Magnetometer\": false')

        if _is_bit_set(self.read_config, AccelerometerBNO055.ACCELERATION_LINEAR_BIT):
            config.append('\t\"LinearAccelerations\": true')
        else:
            config.append('\t\"LinearAccelerations\": false')

        sep = ',\n'

        return f" {{\n{sep.join(val for val in config)}\n }}"

    def _set_accel(self, x: float, y: float, z: float):
        self._accel_prev = self._accel_curr
        self._accel_curr = Vector3(x, y, z)

    def _set_lin_accel(self, x: float, y: float, z: float):
        self._accel_lin_prev = self._accel_lin_curr
        self._accel_lin_curr = Vector3(x, y, z)

    def _set_omega(self, x: float, y: float, z: float):
        self._omega_prev = self._omega_curr
        self._omega_curr = Vector3(x, y, z)

    def _set_angles(self, x: float, y: float, z: float):
        self._angle_prev = self._angle_curr
        self._angle_curr = Vector3(x, y, z)

    def _set_magnetometer(self, x: float, y: float, z: float):
        self._magneto_prev = self._magneto_curr
        self._magneto_curr = Vector3(x, y, z)

    def _set_quaternion(self, w: float, x: float, y: float, z: float):
        self._quat_prev = self._quat_curr
        self._quat_curr = Quaternion(w, x, y, z)

    def _read_request(self):
        # TODO сделать асинхронным, добавить ожидание результата со стороны BNO в течении какого-то, по истечении
        #  которого ничего не возвращать.
        message = self.read_config.to_bytes(1, 'big')
        write_package(self._bno_port, message)
        # time.sleep(0.01)
        response = read_package(self._bno_port)
        self._status = response[0]
        if self._status != 1:
            return

        response = response[1:len(response) - (len(response) - 1) % 8]
        try:
            response = struct.unpack(f'<{len(response) // 8}d', response)
        except ValueError as error:
            print(f"BNO055 data parce error\n{error.args}")
            return

        if self._curr_t < 0:
            self._curr_t = time.perf_counter()
            self._prev_t = time.perf_counter()
        else:
            self._prev_t = self._curr_t
            self._curr_t = time.perf_counter()

        stride = 0

        if len(response) < 3:
            print('EMPTY PACKAGE')
            return

        if _is_bit_set(self.read_config, AccelerometerBNO055.ACCELERATION_BIT):
            self._set_accel(response[stride], response[stride + 1], response[stride + 2])
            stride += 3

        if stride >= len(response):
            return

        if _is_bit_set(self.read_config, AccelerometerBNO055.OMEGA_BIT):
            self._set_omega(response[stride], response[stride + 1], response[stride + 2])
            stride += 3
        if stride >= len(response):
            return

        if _is_bit_set(self.read_config, AccelerometerBNO055.ANGLES_BIT):
            self._set_angles(response[stride], response[stride + 1], response[stride + 2])
            stride += 3
        if stride >= len(response):
            return

        if _is_bit_set(self.read_config, AccelerometerBNO055.QUATERNION_BIT):
            self._set_quaternion(response[stride], response[stride + 1], response[stride + 2], response[stride + 3])
            stride += 4
        if stride >= len(response):
            return

        if _is_bit_set(self.read_config, AccelerometerBNO055.MAGNETOMETER_BIT):
            self._set_magnetometer(response[stride], response[stride + 1], response[stride + 2])
            stride += 3
        if stride >= len(response):
            return

        if _is_bit_set(self.read_config, AccelerometerBNO055.ACCELERATION_LINEAR_BIT):
            self._set_lin_accel(response[stride], response[stride + 1], response[stride + 2])
            stride += 3
        if stride >= len(response):
            return

    def calibrate_request(self):
        message = _set_bit(0, AccelerometerBNO055.CALIBRATION_BIT).to_bytes(1, 'big')
        print(message)
        write_package(self._bno_port, message)

    def update(self):
        self._read_request()

    def record(self, file_path: str, time_out: float = 0.016, record_time: float = 180.0):
        """
        Пишет измерения акселерометра в файл с интервалом time_out на протяжении времени record_time.
        :param file_path: куда пишем
        :param time_out: время между записями
        :param record_time: общее время записи
        """
        import datetime as dt
        with open(file_path, 'wt') as record:
            t_elapsed = 0.0
            d_t = 0.0
            print(f"{{\n\"record_date\": \"{dt.datetime.now().strftime('%H; %M; %S')}\",\n", file=record)
            print("\"way_points\" :[", file=record)
            while t_elapsed <= record_time:
                d_t = time.perf_counter()
                self.update()
                print(self, file=record)
                d_t = time.perf_counter() - d_t
                print(' ,', file=record)
                if d_t > time_out:
                    t_elapsed += d_t
                    print(_device_progres_bar(t_elapsed / record_time, label='RECORDING...'), end='')
                    continue
                t_elapsed += time_out
                print(_device_progres_bar(t_elapsed / record_time, label='RECORDING...'), end='')
                time.sleep(time_out - d_t)
            record.seek(record.tell() - 3, 0)
            print("]\n}", file=record)


if __name__ == '__main__':
    acc = AccelerometerBNO055()
    # acc.record('record_bno_test.json')  # запись в файл
    # acc.calibrate_request()
    for _ in range(10):
        acc.update()
        print(acc)
        time.sleep(.50)
