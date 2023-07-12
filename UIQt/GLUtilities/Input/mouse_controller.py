from PyQt5.QtGui import QMouseEvent, QWheelEvent
from Utilities.Geometry import Vector2
from Utilities import BitSet32
from PyQt5 import QtCore

LEFT_BTN   = QtCore.Qt.MouseButton.LeftButton
RIGHT_BTN  = QtCore.Qt.MouseButton.RightButton
MIDDLE_BTN = QtCore.Qt.MouseButton.MidButton
WHEEL_ROT  = 7

BUTTON_RELEASED = 0
BUTTON_PRESSED = 1
BUTTON_HOLD = 2


class MouseButton:
    def __init__(self, btn_code:  QtCore.Qt.MouseButton = QtCore.Qt.MouseButton.NoButton):
        self._phase:  int = BUTTON_RELEASED
        self._button: QtCore.Qt.MouseButton = btn_code
        self._pressed_pos:  Vector2 = Vector2(0, 0)
        self._hold_pos:     Vector2 = Vector2(0, 0)
        self._released_pos: Vector2 = Vector2(0, 0)
        self._delta_pos:    Vector2 = Vector2(0, 0)

    @property
    def delta_pos_from_start(self) -> Vector2:
        return self._hold_pos - self._pressed_pos

    @property
    def delta_pos(self) -> Vector2:
        return self._delta_pos

    @property
    def key_code(self) -> QtCore.Qt.MouseButton:
        return self._button

    @property
    def pressed_pos(self) -> Vector2:
        return self._pressed_pos

    @property
    def hold_pos(self) -> Vector2:
        return self._hold_pos

    @property
    def released_pos(self) -> Vector2:
        return self._released_pos

    @property
    def is_pressed(self) -> bool:
        return self._phase == BUTTON_PRESSED

    @property
    def is_hold(self) -> bool:
        return self._phase == BUTTON_HOLD

    @property
    def is_released(self) -> bool:
        return self._phase == BUTTON_RELEASED

    def update_on_pressed(self, event: QMouseEvent) -> None:
        if event.buttons() != self.key_code:
            self._phase = BUTTON_RELEASED
            self._delta_pos = Vector2(0, 0)
            return
        self._phase = BUTTON_PRESSED
        self._pressed_pos = Vector2(event.x(), event.y())
        self._hold_pos    = Vector2(event.x(), event.y())
        self._delta_pos   = Vector2(0, 0)

    def update_on_hold(self, event: QMouseEvent) -> None:
        if event.buttons() != self.key_code:
            self._phase = BUTTON_RELEASED
            self._delta_pos = Vector2(0, 0)
            return
        self._phase     = BUTTON_HOLD
        self._delta_pos = Vector2(event.x() - self._hold_pos.x, event.y() - self._hold_pos.y)
        self._hold_pos  = Vector2(event.x(), event.y())

    def update_on_release(self, event: QMouseEvent) -> None:
        if event.buttons() != self.key_code:
            self._phase = BUTTON_RELEASED
            self._delta_pos = Vector2(0, 0)
            return
        self._phase = BUTTON_RELEASED
        self._released_pos = Vector2(event.x(), event.y())
        self._delta_pos   = Vector2(0, 0)


class MouseController:
    def __init__(self):
        self._left_btn:   MouseButton = MouseButton(LEFT_BTN)
        self._right_btn:  MouseButton = MouseButton(RIGHT_BTN)
        self._middle_btn: MouseButton = MouseButton(MIDDLE_BTN)
        self._wheel_delta = 0.0
        self._phase: BitSet32 = BitSet32()

    @property
    def is_wheel_rotated(self) -> bool:
        return self._phase.is_bit_set(WHEEL_ROT)

    @property
    def is_any_pressed(self) -> bool:
        return self._phase.is_bit_set(BUTTON_PRESSED)

    @property
    def is_any_hold(self) -> bool:
        return self._phase.is_bit_set(BUTTON_HOLD)

    @property
    def is_any_released(self) -> bool:
        return self._phase.is_bit_set(BUTTON_RELEASED)

    @property
    def wheel_delta(self):
        return self._wheel_delta

    #######################################
    #               left_btn              #
    #######################################

    @property
    def left_btn(self) -> MouseButton:
        return self._left_btn

    #######################################
    #              middle_btn             #
    #######################################

    @property
    def middle_btn(self) -> MouseButton:
        return self._middle_btn

    #######################################
    #              right_btn              #
    #######################################

    @property
    def right_btn(self) -> MouseButton:
        return self._right_btn

    def update_on_press(self, event: QMouseEvent) -> None:
        self._phase.set_bit(BUTTON_PRESSED)
        self._left_btn.update_on_pressed(event)
        self._right_btn.update_on_pressed(event)
        self._middle_btn.update_on_pressed(event)

    def update_on_hold(self, event: QMouseEvent) -> None:
        self._phase.clear_bit(BUTTON_PRESSED)
        self._phase.set_bit(BUTTON_HOLD)

        self._left_btn.update_on_hold(event)
        self._right_btn.update_on_hold(event)
        self._middle_btn.update_on_hold(event)

    def update_on_release(self, event: QMouseEvent) -> None:
        self._phase.clear_bit(BUTTON_HOLD)
        self._phase.clear_bit(BUTTON_PRESSED)

        self._left_btn.update_on_release(event)
        self._right_btn.update_on_release(event)
        self._middle_btn.update_on_release(event)

    def update_on_wheel(self, event: QWheelEvent):
        self._phase.set_bit(WHEEL_ROT)
        self._wheel_delta = event.angleDelta().y()
