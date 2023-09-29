import struct

from serial.tools.list_ports import comports
from serial import SerialException
from typing import List
import serial


def gather_com_ports():
    return [p for p in comports()]


def validate_ports(ports: List[str]) -> List[str]:
    valid_pots = []
    for p in ports:
        try:
            port = serial.Serial(p.name)
            port.close()
            valid_pots.append(p)
        except SerialException as ex:
            print(ex)
    return valid_pots


ports = gather_com_ports()
print('\n'.join(str(p)for p in ports))
ports = validate_ports(ports)
print('\n'.join(str(p.name) for p in ports))


ser = serial.Serial( port='COM7', baudrate=9600, parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_TWO, bytesize=serial.SEVENBITS)
if not ser.isOpen():
    raise RuntimeError(f"not ser.isOpen()")

ser.flushInput() #flush input buffer, discarding all its contents
ser.flushOutput()#flush output buffer, aborting current o


MESSAGE_START_B = b"$#"
MESSAGE_END_B   = b"#$"
MESSAGE_START = "$#"
MESSAGE_END   = "#$"


def image_info_message(image_name, image_w, image_h) -> bytes:
    return f"{MESSAGE_START}image;{image_name};{image_w};{image_h}{MESSAGE_END}".encode()


def image_data_message(data: bytes) -> bytes:
    return f"{MESSAGE_START}data;{len(data)};{data}{MESSAGE_END}".encode()


def message_data(message: bytes) -> List[bytes]:
    return message[2:-2].split(b';')



# def image_data_received()

print(message_data(image_info_message("image_test.png", 800, 600)))

print(image_info_message("image_test.png", 800, 600))

print(image_data_message(b"image_test.png"))

image_header = "image:image_1.png w:100 h:200 d:1"
image_data   = "t:run data_length:30 data:sdfjsfjwjerhjbajvdjvsjakfjvrjh"