from typing import Tuple
import platform
import datetime
import os

_DEFAULT_DIR_NAME = "camera_records\\"
_DEFAULT_VIDEO_RECORDS_DIR_NAME = "camera_records\\recorded_videos\\"
_DEFAULT_FRAMES_RECORDS_DIR_NAME = "camera_records\\recorded_frames\\"
_DEFAULT_FRAMES_DIR_NAME = "camera_records\\saved_frames\\"


def create_path_with_time_stamp(file_name: str, directory: str, ext: str, microseconds: bool = False):
    now = datetime.datetime.now()
    if microseconds:
        return f'{directory}{file_name}{now.hour:2}_{now.minute:2}_{now.second:2}_{now.microsecond:4}.{ext}'
    return f'{directory}{file_name}{now.hour:2}_{now.minute:2}_{now.second:2}.{ext}'


def create_directory(dir_path: str) -> Tuple[bool, str]:
    if not isinstance(dir_path, str):
        return False, f"Camera CV: create directory error.\nDirectory path type {type(dir_path)} is unsupported\n"
    dir_path = os.path.dirname(dir_path)
    if not os.path.isdir(dir_path):
        try:
            os.mkdir(dir_path)
            return True, dir_path if dir_path.endswith('\\') else f"{dir_path}\\"
        except IOError as error:
            return False,  f"Camera CV: create directory error. Directory \"{error}\" creation error {error}\n"
    return True, dir_path if dir_path.endswith('\\') else f"{dir_path}\\"


def _get_scr_res_wind_old() -> Tuple[int, int]:
    try:
        cmd = 'wmic desktopmonitor get screenheight, screenwidth'
        h, w = tuple(map(int, os.popen(cmd).read().split()[-2::]))
        return w, h
    except ValueError as _:
        return 0, 0


def _get_scr_res_wind_new() -> Tuple[int, int]:
    try:
        cmd = 'wmic path Win32_VideoController get VideoModeDescription,' \
              'CurrentVerticalResolution,CurrentHorizontalResolution /format:value'
        line = os.popen(cmd).read()
        lines = [v for v in line.split('\n') if v != ''][0:2]
        lines = [int(v.split('=')[-1]) for v in lines]
        return lines[0], lines[1]
    except ValueError as _:
        return 0, 0


def get_screen_resolution() -> Tuple[int, int]:
    try:
        if platform.system() == 'Linux':
            screen = os.popen("xrandr -q -d :0").readlines()[0]
            return int(screen.split()[7]), int(screen.split()[9][:-1])
        if platform.system() == 'Windows':
            w, h = _get_scr_res_wind_old()
            if (w, h) == (0, 0):
                w, h = _get_scr_res_wind_new()
            return w, h
    except ValueError as _:
        return 0, 0