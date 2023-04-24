from PyQt5.QtCore import Qt

from Utilities import BitSet32


class MouseInfo(BitSet32):
    # for Qt
    PressedEvent = 3
    ReleaseEvent = 5
    DragEvent = 6
    MoveEvent = 0

    LeftButtonEvent = 1
    RightButtonEvent = 2
    WheelButtonEvent = 4
    WheelRotationEvent = 7

    #  PressedEvent = 0
    #  ReleaseEvent = 1
    #  DragEvent = 2
    #  MoveEvent = 3

    #  LeftButtonEvent = 4
    #  RightButtonEvent = 5
    #  WheelButtonEvent = 6
    #  WheelRotationEvent = 7

    def __init__(self):
        super().__init__()
        self.__wheel_delta: int = 0
        self.__x_screen_prev: int = 0
        self.__y_screen_prev: int = 0
        self.__x_screen: int = 0
        self.__y_screen: int = 0
        self.__x_screen_delta: int = 0
        self.__y_screen_delta: int = 0
        self.__x: float = 0
        self.__y: float = 0
        self.__x_delta: float = 0
        self.__y_delta: float = 0

        self.__x_pressed: float = 0
        self.__y_pressed: float = 0

        self.__x_drag_delta: float = 0
        self.__y_drag_delta: float = 0

    def __str__(self):
        return f"screen   :{self.__x_screen}, {self.__y_screen}\n" \
               f"d screen :{self.__x_screen}, {self.__y_screen}\n" \
               f"local    :{self.__x}, {self.__y}\n" \
               f"d local  :{self.__x_delta}, {self.__y_delta}\n"\
               f"pressed {self.is_pressed}, move {self.is_move}, drag {self.is_drag}, left {self.is_left_button}, "\
               f"right {self.is_right_button}, middle {self.is_wheel_button}\n"

    @property
    def x_screen(self) -> int:
        return self.__x_screen

    @property
    def y_screen(self) -> int:
        return self.__y_screen

    @property
    def xy_screen(self) -> (int, int):
        return self.__x_screen, self.__y_screen

    @property
    def x_screen_delta(self) -> int:
        return self.__x_screen_delta

    @property
    def y_screen_delta(self) -> int:
        return self.__y_screen_delta

    @property
    def xy_screen_delta(self) -> (int, int):
        return self.__x_screen_delta, self.__y_screen_delta

    @property
    def x(self) -> float:
        return self.__x

    @property
    def y(self) -> float:
        return self.__y

    @property
    def xy(self) -> (float, float):
        return self.__x, self.__y

    @property
    def x_delta(self) -> float:
        return self.__x_delta

    @property
    def y_delta(self) -> float:
        return self.__y_delta

    @property
    def xy_delta(self) -> (float, float):
        return self.__x_delta, self.__y_delta

    @property
    def x_start(self) -> float:
        return self.__x_pressed

    @property
    def y_start(self) -> float:
        return self.__y_pressed

    @property
    def xy_start(self) -> (float, float):
        return self.__x_pressed, self.__y_pressed

    @property
    def x_drag_delta(self) -> float:
        return self.__x_drag_delta

    @property
    def y_drag_delta(self) -> float:
        return self.__y_drag_delta

    @property
    def xy_drag_delta(self) -> (float, float):
        return self.__x_drag_delta, self.__y_drag_delta

    @property
    def is_pressed(self) -> bool:
        return self.is_bit_set(MouseInfo.PressedEvent)

    @property
    def is_drag(self) -> bool:
        return self.is_bit_set(MouseInfo.DragEvent)

    @property
    def is_release(self) -> bool:
        return self.is_bit_set(MouseInfo.ReleaseEvent)

    @property
    def is_move(self) -> bool:
        return self.is_bit_set(MouseInfo.MoveEvent)

    @property
    def is_left_button(self) -> bool:
        return self.is_bit_set(MouseInfo.LeftButtonEvent)

    @property
    def is_right_button(self) -> bool:
        return self.is_bit_set(MouseInfo.RightButtonEvent)

    @property
    def is_wheel_button(self) -> bool:
        return self.is_bit_set(MouseInfo.WheelButtonEvent)

    @property
    def is_wheel_rotation(self) -> bool:
        return self.is_bit_set(MouseInfo.WheelRotationEvent)

    def update_position(self, x: int, y: int, scr_w: int, scr_h: int):

        self.__x_screen = x

        self.__y_screen = y

        self.__x_screen_delta = self.__x_screen - self.__x_screen_prev

        self.__y_screen_delta = self.__y_screen - self.__y_screen_prev

        self.__x_screen_prev = self.__x_screen

        self.__y_screen_prev = self.__y_screen

        self.clear_bit(MouseInfo.DragEvent)

        self.clear_bit(MouseInfo.MoveEvent)

        if self.__x_screen_delta != 0:
            self.set_bit(MouseInfo.MoveEvent)

        if self.__y_screen_delta != 0:
            self.set_bit(MouseInfo.MoveEvent)

        if self.is_bit_set(MouseInfo.PressedEvent) and self.is_bit_set(MouseInfo.MoveEvent):
            self.set_bit(MouseInfo.DragEvent)

        self.__x_screen = x
        self.__y_screen = y

        aspect = scr_w * 1.0 / scr_h

        if aspect > 1.0:
            self.__x = ((self.__x_screen - scr_w * 0.5) / scr_w) * 2.0 * aspect
            self.__y = ((self.__y_screen - scr_h * 0.5) / scr_h) * 2.0

            self.__x_delta = self.__x_screen_delta * 2.0 / scr_w * aspect
            self.__y_delta = self.__y_screen_delta * 2.0 / scr_h

            if self.is_pressed:
                self.__x_drag_delta = self.x - self.__x_pressed
                self.__y_drag_delta = self.y - self.__y_pressed
            return

        self.__x = ((self.__x_screen - scr_w * 0.5) / scr_w) * 2.0
        self.__y = ((self.__y_screen - scr_h * 0.5) / scr_h) * 2.0 / aspect

        self.__x_delta = self.__x_screen_delta * 2.0 / scr_w
        self.__y_delta = self.__y_screen_delta * 2.0 / scr_h / aspect
        if self.is_pressed:
            self.__x_drag_delta = self.x - self.__x_pressed
            self.__y_drag_delta = self.y - self.__y_pressed

    """
    def update_state(self, key: int, state: int):
        self.clear_bit(MouseInfo.ReleaseEvent)
        if key == Qt.LeftButton:
            if state == 1:
                self.set_bit(MouseInfo.PressedEvent)
                self.set_bit(MouseInfo.LeftButtonEvent)
                self.__x_pressed = self.x
                self.__y_pressed = self.y
                return
            self.__x_pressed = 0.0
            self.__y_pressed = 0.0
            self.__x_drag_delta = 0.0
            self.__x_drag_delta = 0.0
            self.set_bit(MouseInfo.ReleaseEvent)
            self.clear_bit(MouseInfo.PressedEvent)
            self.clear_bit(MouseInfo.DragEvent)
            self.clear_bit(MouseInfo.LeftButtonEvent)
            return

        if key == Qt.RightButton:
            if state == 1:
                self.set_bit(MouseInfo.PressedEvent)
                self.set_bit(MouseInfo.RightButtonEvent)
                return
            self.set_bit(MouseInfo.ReleaseEvent)
            self.clear_bit(MouseInfo.PressedEvent)
            self.clear_bit(MouseInfo.DragEvent)
            self.clear_bit(MouseInfo.RightButtonEvent)
            return

        if key == Qt.MidButton:
            if state == 1:
                self.set_bit(MouseInfo.PressedEvent)
                self.set_bit(MouseInfo.WheelButtonEvent)
                return
            self.set_bit(MouseInfo.ReleaseEvent)
            self.clear_bit(MouseInfo.PressedEvent)
            self.clear_bit(MouseInfo.DragEvent)
            self.clear_bit(MouseInfo.WheelButtonEvent)
    """
    def update_state(self, key: int):
        self.clear_bit(MouseInfo.ReleaseEvent)
        if key == Qt.LeftButton:
            self.set_bit(MouseInfo.PressedEvent)
            self.set_bit(MouseInfo.LeftButtonEvent)
            self.__x_pressed = self.x
            self.__y_pressed = self.y
            return

        if key == Qt.RightButton:
            self.set_bit(MouseInfo.PressedEvent)
            self.set_bit(MouseInfo.RightButtonEvent)
            return

        if key == Qt.MidButton:
            self.set_bit(MouseInfo.PressedEvent)
            self.set_bit(MouseInfo.WheelButtonEvent)
            return

        self.__x_pressed = 0.0
        self.__y_pressed = 0.0
        self.__x_drag_delta = 0.0
        self.__x_drag_delta = 0.0

        self.clear_bit(MouseInfo.WheelButtonEvent)
        self.clear_bit(MouseInfo.RightButtonEvent)
        self.clear_bit(MouseInfo.LeftButtonEvent)

        self.set_bit(MouseInfo.ReleaseEvent)
        self.clear_bit(MouseInfo.PressedEvent)
        self.clear_bit(MouseInfo.DragEvent)
        self.clear_bit(MouseInfo.LeftButtonEvent)

    def update_wheel_state(self, delta: int):
        pass




