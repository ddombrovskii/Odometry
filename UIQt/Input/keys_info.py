from Utilities import BitSet32


class KeyboardInfo(BitSet32):
    HoldEvent: int = 2
    PressedEvent: int = 1
    ReleaseEvent: int = 0

    ModHoldEvent: int = 5
    ModPressedEvent: int = 4
    ModReleaseEvent: int = 3

    AltButtonEvent: int = 8
    ShiftButtonEvent: int = 7
    CtrlButtonEvent: int = 6
    ModeToState = {4: 8, 1: 7, 2: 6}
    # AltButtonEvent: int = 4
    # ShiftButtonEvent: int = 1
    # CtrlButtonEvent: int = 2

    def __init__(self):

        super().__init__()

        self.__key_code = -1
        self.__scan_code = -1

        self.__event_key_code = -1
        self.__event_scan_code = -1

        self.__mode = 0

    def __str__(self):
        return f"key_code:       {self.__key_code: 3},\n" \
               f"scan_code:      {self.__scan_code: 3},\n" \
               f"event_key_code: {self.__event_key_code: 3},\n" \
               f"event_scan_code:{self.__event_scan_code: 3},\n" \
               f"shift:{self.is_shift_pressed}, alt:{self.is_alt_pressed}, ctrl:{self.is_ctrl_pressed}\n"

    def update_state(self, button: int, scancode: int, action: int, mods: int):

        if action == KeyboardInfo.PressedEvent:
            self.set_bit(KeyboardInfo.PressedEvent)
            self.__key_code = button
            self.__scan_code = scancode

        if action == KeyboardInfo.HoldEvent:
            self.clear_bit(KeyboardInfo.PressedEvent)
            self.set_bit(KeyboardInfo.HoldEvent)

        if action == KeyboardInfo.ReleaseEvent:
            self.clear_bit(KeyboardInfo.HoldEvent)
            self.__key_code = -1
            self.__scan_code = -1

        if mods == 0 or not(mods in KeyboardInfo.ModeToState):
            self.clear_bit(KeyboardInfo.ModHoldEvent)
            self.clear_bit(KeyboardInfo.PressedEvent)
            self.__event_scan_code = -1
            self.__event_key_code = -1
            if self.__mode != 0:
                self.clear_bit(self.__mode)
            self.__mode = 0
            return

        if action == KeyboardInfo.PressedEvent:
            self.__mode = KeyboardInfo.ModeToState[mods]
            self.set_bit(self.__mode)
            self.__event_key_code = button
            self.__event_scan_code = scancode
            self.set_bit(KeyboardInfo.ModPressedEvent)

        if action == KeyboardInfo.HoldEvent:
            self.clear_bit(KeyboardInfo.ModPressedEvent)
            self.set_bit(KeyboardInfo.ModHoldEvent)

    @property
    def is_any_key_pressed(self) -> bool:
        return self.is_bit_set(KeyboardInfo.PressedEvent)

    @property
    def is_any_key_hold(self) -> bool:
        return self.is_bit_set(KeyboardInfo.HoldEvent)

    @property
    def is_shift_pressed(self) -> bool:
        return self.is_bit_set(KeyboardInfo.ShiftButtonEvent)

    @property
    def is_ctrl_pressed(self) -> bool:
        return self.is_bit_set(KeyboardInfo.CtrlButtonEvent)

    @property
    def is_alt_pressed(self) -> bool:
        return self.is_bit_set(KeyboardInfo.AltButtonEvent)

    def is_key(self, key: str) -> bool:
        key_ = ord(key[0])
        if key_ == self.__key_code:
            return True
        if key_ == self.__scan_code:
            return True
        if key_ == self.__event_key_code:
            return True
        if key_ == self.__event_scan_code:
            return True
        return False
