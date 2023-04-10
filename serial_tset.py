from serial.tools import list_ports
from typing import Tuple, Any
import struct
import serial
import time
from Utilities import search_serial_ports

UART_START_MESSAGE = b'$'
UART_END_MESSAGE = b'#'
UART_EMPTY_MESSAGE = b'$#'


def read_package(serial_port: serial.Serial) -> bytes:
    if serial_port.in_waiting == 0:
        return UART_END_MESSAGE
    while serial_port.read() != UART_START_MESSAGE:
        pass
    return serial_port.read_until(UART_END_MESSAGE)[:-1]


def _template_read_package(serial_port: serial.Serial, value_type: str = 'i',
                           size_of: int = 4, endian: str = '>') -> Tuple[Any, ...]:
    raw_data = read_package(serial_port)
    if len(raw_data) == 0:
        return 0,
    raw_data = raw_data[:len(raw_data) - len(raw_data) % size_of]
    return struct.unpack(f'{endian}{len(raw_data) // size_of}{value_type}', raw_data)


def read_int_package(serial_port) -> Tuple[int, ...]:
    return _template_read_package(serial_port, 'i', size_of=4)


def read_float_package(serial_port) -> Tuple[float, ...]:
    return _template_read_package(serial_port, 'f', size_of=4)


def _template_write_package(serial_port, message: Tuple[Any, ...], value_type: str = 'i', endian: str = '>'):
    serial_port.write(UART_START_MESSAGE)
    serial_port.write(struct.pack(f'{endian}{len(message)}{value_type}', *message))
    serial_port.write(UART_END_MESSAGE)


def write_int_package(serial_port, message: Tuple[int, ...]) -> None:
    _template_write_package(serial_port, message, 'i')


def write_float_package(serial_port, message: Tuple[float, ...]) -> None:
    _template_write_package(serial_port, message, 'f')


if __name__ == '__main__':
    ports = list_ports.comports()
    [print(p) for p in ports]
    sender = serial.Serial(ports[0].device, baudrate=9600, timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE)
    receiver = serial.Serial(ports[1].device, baudrate=9600, timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE)

    data_int = tuple((i for i in range(10)))
    data_flt = tuple((i * 1.5 for i in range(10)))
    write_int_package(sender, data_int)
    time.sleep(0.01)
    data = read_int_package(receiver)
    print(data)
    write_float_package(sender, data_flt)
    time.sleep(0.01)
    data = read_float_package(receiver)
    print(data)
    sender.close()
    receiver.close()
    # data = s.read(4 * 5 )

    # print(struct.unpack('>iiiii', data))
