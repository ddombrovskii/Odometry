from PyQt5.QtGui import QKeyEvent
from PyQt5 import QtCore

# LEFT_BTN   = QtCore.Qt.Keyb.LeftButton
# RIGHT_BTN  = QtCore.Qt.MouseButton.RightButton
# MIDDLE_BTN = QtCore.Qt.MouseButton.MidButton
# WHEEL_ROT  = 7
#
BUTTON_RELEASED = 0
BUTTON_PRESSED = 1
BUTTON_HOLD = 2


class KeyboardButton:
    def __init__(self, btn_code:  QtCore.Qt.Key = QtCore.Qt.Key.Key_No):
        self._phase:  int = BUTTON_RELEASED
        self._button: QtCore.Qt.Key = btn_code

    @property
    def key_code(self) -> QtCore.Qt.Key:
        return self._button

    @property
    def is_pressed(self) -> bool:
        return self._phase == BUTTON_PRESSED

    @property
    def is_hold(self) -> bool:
        return self._phase == BUTTON_HOLD

    @property
    def is_released(self) -> bool:
        return self._phase == BUTTON_RELEASED

    def update_on_pressed(self, event: QKeyEvent) -> None:
        if event.key() != self.key_code:
            self._phase = BUTTON_RELEASED
            return
        self._phase = BUTTON_PRESSED

    def update_on_hold(self) -> None:
        self._phase = BUTTON_HOLD if self._phase == BUTTON_PRESSED else BUTTON_RELEASED

    def update_on_release(self, event: QKeyEvent) -> None:
        if event.key() != self.key_code:
            self._phase = BUTTON_RELEASED
            return
        self._phase = BUTTON_RELEASED


class KeyboardController:
    def __init__(self):
        self._w: KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_W)
        self._a: KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_A)
        self._s: KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_S)
        self._d: KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_D)

        self._q: KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_Q)
        self._e: KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_E)

        self._up:    KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_Up)
        self._down:  KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_Down)
        self._left:  KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_Left)
        self._right: KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_Right)

        self._plus:    KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_Plus)
        self._minus:   KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_Minus)

        self._z: KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_Z)
        self._x: KeyboardButton = KeyboardButton(QtCore.Qt.Key.Key_X)

    @property
    def key_w(self):
        return self._w

    @property
    def key_a(self):
        return self._a

    @property
    def key_s(self):
        return self._s

    @property
    def key_d(self):
        return self._d

    @property
    def key_q(self):
        return self._q

    @property
    def key_e(self):
        return self._e

    @property
    def key_up(self):
        return self._up

    @property
    def key_down(self):
        return self._down

    @property
    def key_left(self):
        return self._left

    @property
    def key_right(self):
        return self._right

    @property
    def key_plus(self):
        return self._plus

    @property
    def key_minus(self):
        return self._minus

    @property
    def key_z(self):
        return self._z

    @property
    def key_x(self):
        return self._x

    def update_on_press(self, event: QKeyEvent) -> None:
        self.key_w.update_on_pressed(event)
        self.key_a.update_on_pressed(event)
        self.key_s.update_on_pressed(event)
        self.key_d.update_on_pressed(event)

        self.key_q.update_on_pressed(event)
        self.key_e.update_on_pressed(event)

        self.key_up   .update_on_pressed(event)
        self.key_down .update_on_pressed(event)
        self.key_left .update_on_pressed(event)
        self.key_right.update_on_pressed(event)

        self.key_plus .update_on_pressed(event)
        self.key_minus.update_on_pressed(event)

        self.key_z.update_on_pressed(event)
        self.key_x.update_on_pressed(event)

    def update_on_hold(self) -> None:
        self.key_w.update_on_hold()
        self.key_a.update_on_hold()
        self.key_s.update_on_hold()
        self.key_d.update_on_hold()

        self.key_q.update_on_hold()
        self.key_e.update_on_hold()

        self.key_up   .update_on_hold()
        self.key_down .update_on_hold()
        self.key_left .update_on_hold()
        self.key_right.update_on_hold()

        self.key_plus .update_on_hold()
        self.key_minus.update_on_hold()

        self.key_z.update_on_hold()
        self.key_x.update_on_hold()

    def update_on_release(self, event: QKeyEvent) -> None:
        self.key_w.update_on_release(event)
        self.key_a.update_on_release(event)
        self.key_s.update_on_release(event)
        self.key_d.update_on_release(event)

        self.key_q.update_on_release(event)
        self.key_e.update_on_release(event)

        self.key_up   .update_on_release(event)
        self.key_down .update_on_release(event)
        self.key_left .update_on_release(event)
        self.key_right.update_on_release(event)

        self.key_plus .update_on_release(event)
        self.key_minus.update_on_release(event)

        self.key_z.update_on_release(event)
        self.key_x.update_on_release(event)
