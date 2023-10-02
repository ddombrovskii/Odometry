import os.path
import struct
import time

import PIL.Image
import numpy as np
from serial.tools.list_ports_common import ListPortInfo
from serial.tools.list_ports import comports
from serial import SerialException
from collections import namedtuple
from typing import List, Union
import serial


def gather_com_ports() -> List[ListPortInfo]:
    return [p for p in comports()]


def validate_ports(ports: List[ListPortInfo]) -> List[ListPortInfo]:
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
print('\n'.join(str(p.device) for p in ports))


MESSAGE_START = "$#"
MESSAGE_END   = "#$"
MESSAGE_START_B = b"$#"
MESSAGE_END_B   = b"#$"
IMAGE_KEY = 'image'
DATA_KEY = 'data'
IMAGE_KEY_B = b'image'
DATA_KEY_B = b'data'
RESPONSE_KEY = 'response'
RESPONSE_KEY_B = b'response'
NEW_LINE = ',\n'


def read_message(serial_port: serial.Serial) -> bytes:
    # print(serial_port.read_all())
    if serial_port.in_waiting == 0:
        return b''
    while serial_port.read(2) != MESSAGE_START_B:
        if serial_port.in_waiting != 0:
            continue
        return b''
    res = serial_port.read_until(MESSAGE_END_B)
    return res[:-2]


def image_info_message(image_name: str, image_w: int, image_h: int, bpp: int = 1) -> bytes:
    return f"{MESSAGE_START}{IMAGE_KEY} {image_name} {image_w} {image_h} {bpp}{MESSAGE_END}".encode()


def image_data_message(data: bytes) -> bytes:
    data_len = str(len(data)).encode('utf-8')
    return struct.pack(f"2s{len(data_len)}s1s{len(data)}s2s", MESSAGE_START_B, data_len, b' ', data, MESSAGE_END_B)


def message_data(message: bytes) -> List[bytes]:
    if message.startswith(MESSAGE_START_B):
        message = message[2:]
    if message.endswith(MESSAGE_END_B):
        message = message[:-2]
    return message.split(b' ')


def response_message(success: bool) -> bytes:
    return f"{MESSAGE_START}{RESPONSE_KEY} {1 if success else 0}{MESSAGE_END}".encode()


class ImageInfo(namedtuple('ImageInfo', 'image_name, width, height, bpp')):
    # Сообщение о начале передачи картинки + информация о картинке, такая как размер и количество цветов
    def __new__(cls, image_name: str, width: int, height: int, bpp: int = 1):
        return super().__new__(cls, image_name, width, height, bpp)

    def __str__(self):
        return f"{{\n" \
               f"\t\"image_name\": {self.image_name},\n" \
               f"\t\"width\"     : {self.width},\n" \
               f"\t\"height\"    : {self.height},\n" \
               f"\t\"bpp\"       : {self.bpp}\n" \
               f"}}"

    @classmethod
    def from_message(cls, message: bytes):
        m_data = message_data(message)
        # image image_name image_width image_height image_bytes_per_pixel
        if m_data[0] != IMAGE_KEY_B or len(m_data) != 5:
            raise ValueError(f"ImageInfo::from_message::incorrect message::message: {' '.join(str(v)for v in m_data)}")
        return cls(m_data[1].decode('utf-8'),
                   int(m_data[2].decode('utf-8')),
                   int(m_data[3].decode('utf-8')),
                   int(m_data[4].decode('utf-8')))

    def to_message(self) -> bytes:
        return image_info_message(self.image_name, self.width, self.height, self.bpp)


class ImageData(namedtuple('ImageData', 'image_mem_dump')):
    # Сообщение с частью данных изображения
    def __new__(cls, image_mem_bytes: bytes):
        return super().__new__(cls, image_mem_bytes)

    def __len__(self):
        return len(self.image_mem_dump)

    def __str__(self):
        return f"{{\n" \
               f"\t\"image_mem_size\": {len(self)},\n" \
               f"\t\"image_mem_dump\": {self.image_mem_dump}\n" \
               f"}}"

    @classmethod
    def from_message(cls, message: bytes):
        m_data = message_data(message)
        if m_data[0] != DATA_KEY_B or len(m_data) != 3:  # data bytes_count_in_message bytes_in_message
            raise ValueError(f"ImageData::from_message::incorrect message::message: {' '.join(str(v)for v in m_data)}")
        return cls(m_data[2])

    def to_message(self) -> bytes:
        return image_data_message(self.image_mem_dump)


class Response(namedtuple('ImageData', 'status')):
    # Сообщение с частью данных изображения
    def __new__(cls, status: bool):
        return super().__new__(cls, status)

    def __str__(self):
        return f"{{\"status\": {1 if self.status else 0}}}"

    def __bool__(self) -> bool:
        return self.status

    @classmethod
    def from_message(cls, message: bytes):
        m_data = message_data(message)
        if m_data[0] != RESPONSE_KEY_B or len(m_data) != 2:  # response response_status
            raise ValueError(f"ImageData::from_message::incorrect message::message: {' '.join(str(v)for v in m_data)}")
        return cls(m_data[1] == b'1')

    def to_message(self) -> bytes:
        return response_message(self.status)


class UARTPort(namedtuple('UARTPort', 'port')):
    def __new__(cls, **args):
        try:
            port = serial.Serial(**args)
        except Exception as ex:
            print(f"UARTPort::New::incorrect\nerror: {ex},\nargs:"
                  f"\n{NEW_LINE.join(f'key: {k} arg: {v}' for k, v in args.items())}")
            exit(-1)
        except SerialException as ex:
            print(f"UARTPort::New::incorrect\nerror: {ex},\nargs:"
                  f"\n{NEW_LINE.join(f'key: {k} arg: {v}' for k, v in args.items())}")
            exit(-1)

        if not port.isOpen():
            raise RuntimeError(f"not serial.isOpen(),"
                               f" with args:\n{NEW_LINE.join(f'key: {k} arg: {v}' for k, v in args.items())}")
        port.flushInput()  # flush input buffer, discarding all its contents
        port.flushOutput()  # flush output buffer, aborting current o
        return super().__new__(cls, port)

    def __del__(self):
        # self.clear()
        self.port.close()

    def write(self, message: bytes) -> Response:
        # print(message)
        # Пишет сообщение, а после ожидает подтверждения, что сообщение было получено
        write_amount = self.port.write(message)
        if write_amount is None:
            return Response(False)
        if write_amount != len(message):
            return Response(False)
        # return Response(True)
        start_t = time.perf_counter()
        while time.perf_counter() - start_t < self.port.timeout:
            try:
                return Response.from_message(self.read())
            except ValueError as _:
                continue
        return Response(False)

    def read(self) -> bytes:
        if self.port.in_waiting == 0:
            return b''
        start_t = time.perf_counter()
        while self.port.read(2) != MESSAGE_START_B:
            if time.perf_counter() - start_t < self.port.timeout:
                return b''
            if self.port.in_waiting != 0:
                continue
            return b''
        return self.port.read_until(MESSAGE_END_B)[:-2]

    def clear(self):
        self.port.flushInput()  # flush input buffer, discarding all its contents
        self.port.flushOutput()  # flush output buffer, aborting current o


def _try_to_send_data(port: UARTPort, data: bytes, send_tries_amount: int = 32) -> Response:
    for _ in range(send_tries_amount):
        sending_status = port.write(data)
        if sending_status:
            return Response(True)
    return Response(False)


def send_image(port: UARTPort, image_src: str, image_chunk_size: int = 4096, send_tries_amount: int = 32) -> Response:
    if not os.path.exists(image_src):
        return Response(False)
    port.clear()
    image_info = PIL.Image.open(image_src)
    with open(image_src, 'rb') as input_image:
        im_info_message = ImageInfo(image_src,
                                    *image_info.size,
                                    image_info.layers if "layes" in image_info.__dict__ else 1).to_message()
        # пытаемся отправить информацию о передаваемой картинке
        sending_status = _try_to_send_data(port, im_info_message, send_tries_amount)
        # не получилось
        if not sending_status:
            print("Image chunk sending exceed maximum amount of tries")
            return sending_status
        # получилось
        while True:
            # читаем файл по кускам, до тех пор пока читается
            data = input_image.read(image_chunk_size)
            if data == b'':
                break
            # пытаемся отправить прочитанный кусок
            sending_status = _try_to_send_data(port, data, send_tries_amount)
            # не получилось
            if not sending_status:
                print("Image chunk sending exceed maximum amount of tries")
                return sending_status
            # получилось
        sending_status = _try_to_send_data(port, b"$#END#$", send_tries_amount)
        return sending_status


def read_image(port: UARTPort, image_dst: str, read_tries_amount: int = 32, image_read_max_time: float = 10):
    im_info: Union[ImageInfo, None] = None
    im_done: bool = False
    with open(image_src, 'wb') as output_image:
        t_start = time.perf_counter()
        while not im_done:
            for _ in range(read_tries_amount):
                message = port.read()
                if message.startswith(b"END"):
                    im_done = True
                    break
                if message.startswith(IMAGE_KEY_B):
                    im_info = ImageInfo.from_message(message)
                    break
                if message.startswith(DATA_KEY_B):
                    im_data = ImageData.from_message(message)
                    if len(im_data) != output_image.write(im_data.image_mem_dump):
                        raise IOError(f"image_dst: {image_dst} write error")
                    break
            if time.perf_counter() - t_start > image_read_max_time:
                raise RuntimeError(f"Image reading time exceeds...")
    return im_info


port: UARTPort = UARTPort(port='COM3', baudrate=115200, timeout=0.1)
port.clear()
image_src = "image_0.png"
image_bytes = b''
chunk_size = 4096

    #  image_bytes = input_image.read()


print(port.write(image_data_message(b"sdfjsfjwjerhjbajvdjvsjakfjvrjh")))
time.sleep(0.10)
print(port.read())

# print(message_data(image_info_message("image_test.png", 800, 600)))

# print(ImageInfo.from_message(image_info_message("image_test.png", 800, 600)))

# print(image_data_message(b"sdfjsfjwjerhjbajvdjvsjakfjvrjh"))

# image_header = "image:image_1.png w:100 h:200 d:1"
# image_data   = "t:run data_length:30 data:sdfjsfjwjerhjbajvdjvsjakfjvrjh"