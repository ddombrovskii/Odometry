from typing import Tuple, Any
import struct
import serial
import glob
import sys

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


def search_serial_ports():
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
