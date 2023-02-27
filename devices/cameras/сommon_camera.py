import numpy as np


class CommonCamera:
    def record(self, path: str) -> None:
        ...

    def show(self) -> None:
        ...

    def calibrate(self) -> None:
        ...

    def grab_frame(self) -> np.dnarray:
        ...

    def grab_frames(self) -> np.dnarray:
        ...

    def save_frame(self, path: str) -> bool:
        ...

    def save_frames(self, path: str, count: int = 10) -> bool:
        ...

    @property
    def width(self) -> int:
        return 0

    @property
    def height(self) -> int:
        return 0
