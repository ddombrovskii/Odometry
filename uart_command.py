from typing import List, Union, Tuple
from collections import namedtuple
import json
import glob
import sys


def _comas(v):
    return f'\"{str(v)}\"'


def _parse_error(error, error_string: str = None) -> str:
    if error_string is None:
        return f'{COMA_SEPARATOR.join(_comas(v) for v in error.args)}'
    return f'{error_string}{","if len(error_string) != 0 else ""}{COMA_SEPARATOR.join(_comas(v) for v in error.args)}'


try:
    from serial import SerialException
    import serial
except ImportError as er:
    print(_parse_error(er))

# mode 0 - send / mode 1 - read
SYS_ARGV_EXAMPLE = \
    '''
{
    \"port\":     \"COM5\",
    \"mode\":     0,
    \"baudrate\": 115200,
    \"timeout\":  1,
    \"bytesize\": 8,
    \"stopbits\": 1,
    \"message\":  \"1.000,2.000|3.000,4.000|5.000,6.000\"
}
'''
UART_START_MESSAGE = b'$#'
UART_END_MESSAGE = b'#$'
COMA_SEPARATOR = ','


def _read_package(serial_port: serial.Serial) -> bytes:
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


def _errors_json(errors: str):
    return f'{{\n\t\"errors\": [{errors}]\n}}'


def _response_json(response: str, errors: str = ''):
    return f'{{\n\t\"response\": [{response}],\n\t\"errors\": [{errors}]\n}}'


def _collect_com_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(32)]
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


class COMCommand(namedtuple('COMCommand', 'port, mode, message, baudrate, timeout, bytesize, stopbits')):
    __slots__ = ()

    def __new__(cls, port: str, message: str, mode: int = 0, baudrate: int = 115200, timeout: int = 1, bytesize: int = 9,
                stopbits: int = serial.STOPBITS_ONE):
        return super().__new__(cls, port, mode, message, baudrate, timeout, bytesize, stopbits)

    def __repr__(self):
        return f'{{\n' \
               f'\t\"port\":     \"{self.port}\",\n' \
               f'\t\"mode\":     {self.mode},\n' \
               f'\t\"baudrate\": {self.baudrate},\n' \
               f'\t\"bytesize\": {self.bytesize},\n' \
               f'\t\"timeout\":  {self.timeout},\n' \
               f'\t\"stopbits\": {self.stopbits},\n' \
               f'\t\"message\":  \"{self.message}\"\n' \
               f'}}'

    def __str__(self):
        return self.message  # '|'.join(f'{x:.3f},{y:.3f}' for x, y in zip(self.message[:-1:2], self.message[1::2]))

    def __bytes__(self):
        return bytes(str(self), 'utf-8')

    def __len__(self) -> int:
        return 1

    @property
    def is_read(self) -> bool:
        return self.mode == 1

    @property
    def is_write(self) -> bool:
        return self.mode == 0

    def _send(self) -> str:
        status = ''
        try:
            with serial.Serial(self.port, baudrate=self.baudrate, bytesize=self.bytesize,
                               write_timeout=self.timeout, stopbits=self.stopbits) as serial_port:
                # serial_port.open() ???
                serial_port.write(UART_START_MESSAGE)
                serial_port.write(bytes(self))
                serial_port.write(UART_END_MESSAGE)
        except SerialException as ex:
            status = _parse_error(ex, status)
        except ValueError as ex:
            status = _parse_error(ex, status)
        return _errors_json(status)

    def _read(self) -> str:
        status = ''
        data = ''
        try:
            with serial.Serial(self.port, baudrate=self.baudrate, bytesize=self.bytesize,
                               write_timeout=self.timeout, stopbits=self.stopbits) as serial_port:
                # serial_port.open() ???
                data = _read_package(serial_port).decode('utf-8')
        except SerialException as ex:
            status = _parse_error(ex, status)
        except ValueError as ex:
            status = _parse_error(ex, status)
        return _response_json(data, status)

    def execute(self) -> str:
        return self._send() if self.is_write else self._read()


def build_message(argv) -> Union[str, COMCommand]:
    try:
        raw_command = json.loads(argv)
    except Exception as ex:
        return _errors_json(_parse_error(ex))
    response = ''
    try:
        port     = raw_command['port']
        mode     = min(max(0, int(raw_command['mode'])), 1)if 'mode' in raw_command else 1
        baudrate = int(raw_command['baudrate'])
        bytesize = int(raw_command['bytesize'])
        timeout  = int(raw_command['timeout'])
        stopbits = int(raw_command['stopbits'])
        message = raw_command['message'] if 'message' in raw_command else ""
    except ValueError as ex:
        response = _parse_error(ex, response)
    except KeyError as ex:
        response = _parse_error(ex, response)
    except RuntimeError as ex:
        response = _parse_error(ex, response)
    if response != '':
        return _errors_json(response)
    return COMCommand(port, message, mode, baudrate, timeout, bytesize, stopbits)


def collect_com_ports():
    error = ''
    ports = []
    try:
        ports = _collect_com_ports()
    except EnvironmentError as ex:
        error = _parse_error(ex, error)
    except RuntimeError as ex:
        error = _parse_error(ex, error)
    if len(error) != 0:
        return _errors_json(error)
    return f'{{\n\t\"ports\":[{COMA_SEPARATOR.join(_comas(v) for v in ports)}]\n}}'


def execute_command(args: Tuple[str, ...] = None) -> str:
    if args is None:
        args = sys.argv[1:]
    if len(args) < 1:
        return _errors_json("\"empty command\"")
    if args[0] == 'collect_ports':
        return collect_com_ports()

    if len(args) < 2:
        return _errors_json("\"nothing to send/read...\"")

    if args[0] == 'uart_command':
        command = build_message(args[1])
        if isinstance(command, str):
            return command
        return command.execute()

    return _errors_json(f"\"unknown command: {args[0]}\"")


if __name__ == '__main__':
    '''
    Пример параметров командной строки при отправки сообщения в UART 
    ...\\uart_command.py uart_send {\"port\":\"COM3\",\"baudrate\":115200,\"timeout\":1,\"bytesize\":8,\"stopbits\":1,\"message\":[1.0,2.0,3.0,4.0,5.0,6.0]}
     Пример параметров командной строки при сканировании COM портов 
    ...\\uart_command.py collect_ports
    '''
    print(execute_command())  # 'collect_ports', SYS_ARGV_EXAMPLE)))
