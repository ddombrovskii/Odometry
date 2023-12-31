from pathlib import Path
from typing import List, Tuple, Union
import numpy as np
import struct
import cv2
import io
import os
import re

ImageFilesList = ('jpg', 'jpeg', 'png', 'bmp')


def get_file_type(f_path: str) -> str:
    assert isinstance(f_path, str)
    return f_path[f_path.rfind('.') + 1:].lower()


def clear_folder(folder: str) -> bool:
    assert isinstance(folder, str)
    status = False
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                status |= True
        except Exception as e:
            print(f"clear folder error{e.args}")
    return status


def clear_folder_files_with_ext(folder: str, ext: str) -> bool:
    assert isinstance(folder, str)
    status = False
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if not os.path.isfile(file_path):
                continue
            if get_file_type(file_path) != ext:
                continue
            os.remove(file_path)
            status |= True
        except Exception as e:
            print(f"clear folder error{e.args}")
    return status


def create_dir(dir_name: str) -> bool:
    assert isinstance(dir_name, str)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        return True
    return False


def get_files_paths_from_dir(src_dir: str) -> List[str]:
    assert isinstance(src_dir, str)
    res_list = []
    for (dir_path, dir_names, file_names) in os.walk(src_dir):
        for file_name in file_names:
            file_type = file_name[file_name.rfind('.') + 1:].lower()
            if file_type in ImageFilesList:
                res_list.append(os.path.join(dir_path, file_name))
    return res_list


def get_files_paths_from_dir_with_ext(src_dir: str, ext: str = "png") -> List[str]:
    assert isinstance(src_dir, str)
    assert isinstance(ext, str)
    res_list = []
    for (dir_path, dir_names, file_names) in os.walk(src_dir):
        for file_name in file_names:
            file_type = file_name[file_name.rfind('.') + 1:].lower()
            if file_type == ext:
                res_list.append(os.path.join(dir_path, file_name))
    return res_list


def read_image(src: str, cv_read_args=None) -> np.ndarray:
    try:
        return cv2.imread(src) if cv_read_args is None else cv2.imread(src, cv_read_args)
    except IOError as e:
        print(f"image at path \"{src}\" read error...\n{e.args}")
        return np.zeros((3, 3, 3), dtype=np.uint8)


def get_images_from_dir(src_dir: str, ext: str = None) -> List[np.ndarray]:
    file_names = get_files_paths_from_dir(src_dir) if ext is None else get_files_paths_from_dir_with_ext(src_dir, ext)
    res_list = []
    for temp_f0 in file_names:
        print(f"image loaded: {temp_f0}")
        try:
            res_list.append(cv2.imread(temp_f0))
        except IOError as e:
            print(f"image at path {temp_f0} read error...\n{e.args}")
    return res_list


def get_base_name(src_name: str) -> str:
    assert isinstance(src_name, str)
    return os.path.basename(src_name)


def str_list_new_row(src_list: list) -> str:
    return '\n'.join([str(my_element) for my_element in src_list])


def print_list_new_row(src_list: list):
    print(str_list_new_row(src_list))


def is_file(src: str) -> bool:
    return Path(src).is_file()


def is_dir(src: str) -> bool:
    return Path(src).is_dir()


_UNIT_KM = -3
_UNIT_100M = -2
_UNIT_10M = -1
_UNIT_1M = 0
_UNIT_10CM = 1
_UNIT_CM = 2
_UNIT_MM = 3
_UNIT_0_1MM = 4
_UNIT_0_01MM = 5
_UNIT_UM = 6
_UNIT_INCH = 6
_TIFF_TYPE_SIZES = {
  1: 1,
  2: 1,
  3: 2,
  4: 4,
  5: 8,
  6: 1,
  7: 1,
  8: 2,
  9: 4,
  10: 8,
  11: 4,
  12: 8,
}


def _convert_to_dpi(density, unit):
    if unit == _UNIT_KM:
        return int(density * 0.0000254 + 0.5)
    elif unit == _UNIT_100M:
        return int(density * 0.000254 + 0.5)
    elif unit == _UNIT_10M:
        return int(density * 0.00254 + 0.5)
    elif unit == _UNIT_1M:
        return int(density * 0.0254 + 0.5)
    elif unit == _UNIT_10CM:
        return int(density * 0.254 + 0.5)
    elif unit == _UNIT_CM:
        return int(density * 2.54 + 0.5)
    elif unit == _UNIT_MM:
        return int(density * 25.4 + 0.5)
    elif unit == _UNIT_0_1MM:
        return density * 254
    elif unit == _UNIT_0_01MM:
        return density * 2540
    elif unit == _UNIT_UM:
        return density * 25400
    return density


def _convert_to_pix(value):
    matched = re.match(r"(\d+(?:\.\d+)?)?([a-z]*)$", value)
    if not matched:
        raise ValueError("unknown length value: %s" % value)

    length, unit = matched.groups()
    if unit == "":
        return float(length)
    elif unit == "cm":
        return float(length) * 96 / 2.54
    elif unit == "mm":
        return float(length) * 96 / 2.54 / 10
    elif unit == "in":
        return float(length) * 96
    elif unit == "pc":
        return float(length) * 96 / 6
    elif unit == "pt":
        return float(length) * 96 / 6
    elif unit == "px":
        return float(length)

    raise ValueError("unknown unit type: %s" % unit)


def get_img_size(filepath: Union[str,  io.BytesIO]) -> Tuple[int, int]:
    """
    Return (width, height) for a given img file content
    no requirements
    :type filepath: Union[bytes, str, pathlib.Path]
    :rtype Tuple[int, int]
    """
    height = -1
    width = -1

    if isinstance(filepath, io.BytesIO):  # file-like object
        f_handle = filepath
    else:
        f_handle = open(filepath, 'rb')

    try:
        head = f_handle.read(31)
        size = len(head)
        # handle GIFs
        if size >= 10 and head[:6] in (b'GIF87a', b'GIF89a'):
            # Check to see if content_type is correct
            try:
                width, height = struct.unpack("<hh", head[6:10])
            except struct.error:
                raise ValueError("Invalid GIF file")
        # see png edition spec bytes are below chunk length then and finally the
        elif size >= 24 and head.startswith(b'\211PNG\r\n\032\n') and head[12:16] == b'IHDR':
            try:
                width, height = struct.unpack(">LL", head[16:24])
            except struct.error:
                raise ValueError("Invalid PNG file")
        # Maybe this is for an older PNG version.
        elif size >= 16 and head.startswith(b'\211PNG\r\n\032\n'):
            # Check to see if we have the right content type
            try:
                width, height = struct.unpack(">LL", head[8:16])
            except struct.error:
                raise ValueError("Invalid PNG file")
        # handle JPEGs
        elif size >= 2 and head.startswith(b'\377\330'):
            try:
                f_handle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf or ftype in [0xc4, 0xc8, 0xcc]:
                    f_handle.seek(size, 1)
                    byte = f_handle.read(1)
                    while ord(byte) == 0xff:
                        byte = f_handle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', f_handle.read(2))[0] - 2
                # We are at a SOFn block
                f_handle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', f_handle.read(4))
            except (struct.error, TypeError):
                raise ValueError("Invalid JPEG file")
        # handle JPEG2000s
        elif size >= 12 and head.startswith(b'\x00\x00\x00\x0cjP  \r\n\x87\n'):
            f_handle.seek(48)
            try:
                height, width = struct.unpack('>LL', f_handle.read(8))
            except struct.error:
                raise ValueError("Invalid JPEG2000 file")
        # handle big endian TIFF
        elif size >= 8 and head.startswith(b"\x4d\x4d\x00\x2a"):
            offset = struct.unpack('>L', head[4:8])[0]
            f_handle.seek(offset)
            ifdsize = struct.unpack(">H", f_handle.read(2))[0]
            for i in range(ifdsize):
                tag, datatype, count, data = struct.unpack(">HHLL", f_handle.read(12))
                if tag == 256:
                    if datatype == 3:
                        width = int(data / 65536)
                    elif datatype == 4:
                        width = data
                    else:
                        raise ValueError("Invalid TIFF file: width column data type should be SHORT/LONG.")
                elif tag == 257:
                    if datatype == 3:
                        height = int(data / 65536)
                    elif datatype == 4:
                        height = data
                    else:
                        raise ValueError("Invalid TIFF file: height column data type should be SHORT/LONG.")
                if width != -1 and height != -1:
                    break
            if width == -1 or height == -1:
                raise ValueError("Invalid TIFF file: width and/or height IDS entries are missing.")
        elif size >= 8 and head.startswith(b"\x49\x49\x2a\x00"):
            offset = struct.unpack('<L', head[4:8])[0]
            f_handle.seek(offset)
            ifdsize = struct.unpack("<H", f_handle.read(2))[0]
            for i in range(ifdsize):
                tag, datatype, count, data = struct.unpack("<HHLL", f_handle.read(12))
                if tag == 256:
                    width = data
                elif tag == 257:
                    height = data
                if width != -1 and height != -1:
                    break
            if width == -1 or height == -1:
                raise ValueError("Invalid TIFF file: width and/or height IDS entries are missing.")
        # handle little endian BigTiff
        elif size >= 8 and head.startswith(b"\x49\x49\x2b\x00"):
            bytesize_offset = struct.unpack('<L', head[4:8])[0]
            if bytesize_offset != 8:
                raise ValueError('Invalid BigTIFF file: Expected offset to be 8, found {} instead.'.format(bytesize_offset))
            offset = struct.unpack('<Q', head[8:16])[0]
            f_handle.seek(offset)
            ifdsize = struct.unpack("<Q", f_handle.read(8))[0]
            for i in range(ifdsize):
                tag, datatype, count, data = struct.unpack("<HHQQ", f_handle.read(20))
                if tag == 256:
                    width = data
                elif tag == 257:
                    height = data
                if width != -1 and height != -1:
                    break
            if width == -1 or height == -1:
                raise ValueError("Invalid BigTIFF file: width and/or height IDS entries are missing.")

        # handle SVGs
        elif size >= 5 and (head.startswith(b'<?xml') or head.startswith(b'<svg')):
            f_handle.seek(0)
            data = f_handle.read(1024)
            try:
                data = data.decode('utf-8')
                width = re.search(r'[^-]width="(.*?)"', data).group(1)
                height = re.search(r'[^-]height="(.*?)"', data).group(1)
            except Exception:
                raise ValueError("Invalid SVG file")
            width = _convert_to_pix(width)
            height = _convert_to_pix(height)

        # handle Netpbm
        elif head[:1] == b"P" and head[1:2] in b"123456":
            f_handle.seek(2)
            sizes = []

            while True:
                next_chr = f_handle.read(1)

                if next_chr.isspace():
                    continue

                if next_chr == b"":
                    raise ValueError("Invalid Netpbm file")

                if next_chr == b"#":
                    f_handle.readline()
                    continue

                if not next_chr.isdigit():
                    raise ValueError("Invalid character found on Netpbm file")

                size = next_chr
                next_chr = f_handle.read(1)

                while next_chr.isdigit():
                    size += next_chr
                    next_chr = f_handle.read(1)

                sizes.append(int(size))

                if len(sizes) == 2:
                    break

                f_handle.seek(-1, os.SEEK_CUR)
            width, height = sizes
        elif head.startswith(b"RIFF") and head[8:12] == b"WEBP":
            if head[12:16] == b"VP8 ":
                width, height = struct.unpack("<HH", head[26:30])
            elif head[12:16] == b"VP8X":
                width = struct.unpack("<I", head[24:27] + b"\0")[0]
                height = struct.unpack("<I", head[27:30] + b"\0")[0]
            elif head[12:16] == b"VP8L":
                b = head[21:25]
                width = (((b[1] & 63) << 8) | b[0]) + 1
                height = (((b[3] & 15) << 10) | (b[2] << 2) | ((b[1] & 192) >> 6)) + 1
            else:
                raise ValueError("Unsupported WebP file")

    finally:
        f_handle.close()

    return width, height


def get_img_dpi(filepath: Union[str, bytes]) -> Tuple[int, int]:
    """
    Return (x DPI, y DPI) for a given img file content
    no requirements
    :type filepath: Union[bytes, str, pathlib.Path]
    :rtype Tuple[int, int]
    """
    xDPI = -1
    yDPI = -1

    if not isinstance(filepath, bytes):
        filepath = str(filepath)

    with open(filepath, 'rb') as fhandle:
        head = fhandle.read(24)
        size = len(head)
        # handle GIFs
        # GIFs doesn't have density
        if size >= 10 and head[:6] in (b'GIF87a', b'GIF89a'):
            pass
        # see png edition spec bytes are below chunk length then and finally the
        elif size >= 24 and head.startswith(b'\211PNG\r\n\032\n'):
            chunkOffset = 8
            chunk = head[8:]
            while True:
                chunkType = chunk[4:8]
                if chunkType == b'pHYs':
                    try:
                        xDensity, yDensity, unit = struct.unpack(">LLB", chunk[8:])
                    except struct.error:
                        raise ValueError("Invalid PNG file")
                    if unit:
                        xDPI = _convert_to_dpi(xDensity, _UNIT_1M)
                        yDPI = _convert_to_dpi(yDensity, _UNIT_1M)
                    else:  # no unit
                        xDPI = xDensity
                        yDPI = yDensity
                    break
                elif chunkType == b'IDAT':
                    break
                else:
                    try:
                        dataSize, = struct.unpack(">L", chunk[0:4])
                    except struct.error:
                        raise ValueError("Invalid PNG file")
                    chunkOffset += dataSize + 12
                    fhandle.seek(chunkOffset)
                    chunk = fhandle.read(17)
        # handle JPEGs
        elif size >= 2 and head.startswith(b'\377\330'):
            try:
                fhandle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    if ftype == 0xe0:  # APP0 marker
                        fhandle.seek(7, 1)
                        unit, xDensity, yDensity = struct.unpack(">BHH", fhandle.read(5))
                        if unit == 1 or unit == 0:
                            xDPI = xDensity
                            yDPI = yDensity
                        elif unit == 2:
                            xDPI = _convert_to_dpi(xDensity, _UNIT_CM)
                            yDPI = _convert_to_dpi(yDensity, _UNIT_CM)
                        break
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
            except struct.error:
                raise ValueError("Invalid JPEG file")
        # handle JPEG2000s
        elif size >= 12 and head.startswith(b'\x00\x00\x00\x0cjP  \r\n\x87\n'):
            fhandle.seek(32)
            # skip JP2 image header box
            headerSize = struct.unpack('>L', fhandle.read(4))[0] - 8
            fhandle.seek(4, 1)
            foundResBox = False
            try:
                while headerSize > 0:
                    boxHeader = fhandle.read(8)
                    boxType = boxHeader[4:]
                    if boxType == b'res ':  # find resolution super box
                        foundResBox = True
                        headerSize -= 8
                        break
                    boxSize, = struct.unpack('>L', boxHeader[:4])
                    fhandle.seek(boxSize - 8, 1)
                    headerSize -= boxSize
                if foundResBox:
                    while headerSize > 0:
                        boxHeader = fhandle.read(8)
                        boxType = boxHeader[4:]
                        if boxType == b'resd':  # Display resolution box
                            yDensity, xDensity, yUnit, xUnit = struct.unpack(">HHBB", fhandle.read(10))
                            xDPI = _convert_to_dpi(xDensity, xUnit)
                            yDPI = _convert_to_dpi(yDensity, yUnit)
                            break
                        boxSize, = struct.unpack('>L', boxHeader[:4])
                        fhandle.seek(boxSize - 8, 1)
                        headerSize -= boxSize
            except struct.error as e:
                raise ValueError("Invalid JPEG2000 file")
    return xDPI, yDPI
