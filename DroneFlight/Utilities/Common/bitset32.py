def set_bit(bytes_: int, bit_: int) -> int:
    bytes_ |= (1 << bit_)
    return bytes_


def is_bit_set(bytes_: int, bit_: int) -> bool:
    return (bytes_ & (1 << bit_)) != 0


def inverse_bit(bytes_: int, bit_: int) -> int:
    bytes_ ^= (1 << bit_)
    return bytes_


def clear_bit(bytes_: int, bit_: int) -> int:
    bytes_ &= ~(1 << bit_)
    return bytes_


class BitSet32:

    _empty_state: int = 0
    _full_state:  int = 4294967295

    __slots__ = "_state"

    def __init__(self, value: int = 0):
        self._state: int = value

    def __repr__(self):
        return f"{{\"bits\": \"0x{''.join(str(bit) for bit in self.bits)}\"}}"
        
    def __str__(self):
        return str(self._state)

    @property
    def bits(self):
        for bit in range(32):
            if self.is_bit_set(bit):
                yield 1
            else:
                yield 0

    @property
    def state(self) -> int:
        return self._state

    @property
    def is_empty(self) -> bool:
        return self._state == BitSet32._empty_state

    @property
    def is_full(self) -> bool:
        return self._state == BitSet32._full_state

    def is_bit_set(self, bit_: int):
        return is_bit_set(self._state, bit_)

    def set_bit(self, bit_: int):
        self._state = set_bit(self._state, bit_)
        return self

    def inverse_bit(self, bit_: int):
        self._state = inverse_bit(self._state, bit_)
        return self

    def clear_bit(self, bit_: int):
        self._state = clear_bit(self._state, bit_)
        return self

    def clear(self):
        self._state = BitSet32._empty_state
        return self

    def inverse(self):
        for i in range(32):
            self._state = inverse_bit(self._state, i)
        return self


def bit_set_test():
    bit_set = BitSet32()
    bit_set.set_bit(0)
    bit_set.set_bit(2)
    bit_set.set_bit(4)
    bit_set.set_bit(6)
    print(bit_set)
    bit_set.inverse()
    print(bit_set)
    bit_set.clear()
    print(bit_set)


if __name__ == '__main__':
    bit_set_test()
    
