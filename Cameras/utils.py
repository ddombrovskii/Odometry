import os
from typing import Tuple
import platform


def get_screen_resolution() -> Tuple[int, int]:
    if platform.system() == 'Linux':
        screen = os.popen("xrandr -q -d :0").readlines()[0]
        return int(screen.split()[7]), int(screen.split()[9][:-1])
    if platform.system() == 'Windows':
        cmd = 'wmic desktopmonitor get screenheight, screenwidth'
        h, w = tuple(map(int, os.popen(cmd).read().split()[-2::]))
        return w, h
    return 0, 0
