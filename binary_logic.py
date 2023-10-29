from typing import Tuple

# Логические пары используются для проверки and/or/not/xor
pairs = ((1, 1), (1, 0), (0, 1), (0, 0))
# Триплеты вида A, B, C_IN. Используются для проверки полного сумматора.
full_summator_triples = (
    (0, 0, 0),
    (1, 0, 0),
    (0, 1, 0),
    (1, 1, 0),
    (0, 0, 1),
    (1, 0, 1),
    (0, 1, 1),
    (1, 1, 1))

INT_BITS_COUNT = 32
# Единица в бинарной форме для разного размера целого числа
ONE_8_BIT  = (1, 0, 0, 0, 0, 0, 0, 0)
ONE_16_BIT = (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
ONE_32_BIT = (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
ONE_64_BIT = (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

BINARY_ONES = {8: ONE_8_BIT,
               16: ONE_16_BIT,
               32: ONE_32_BIT,
               64: ONE_64_BIT}

BINARY_ONE = BINARY_ONES[INT_BITS_COUNT]

# Степени двойки для разного размера целого числа
POWERS_OF_TWO_8_BIT  = tuple(2 ** v for v in range(8))
POWERS_OF_TWO_16_BIT = tuple(2 ** v for v in range(16))
POWERS_OF_TWO_32_BIT = tuple(2 ** v for v in range(32))
POWERS_OF_TWO_64_BIT = tuple(2 ** v for v in range(64))

POWERS_OF_TWOS = {8:  POWERS_OF_TWO_8_BIT,
                  16: POWERS_OF_TWO_16_BIT,
                  32: POWERS_OF_TWO_32_BIT,
                  64: POWERS_OF_TWO_64_BIT}

POWERS_OF_TWO = POWERS_OF_TWOS[INT_BITS_COUNT]


def xor(left: int, right: int) -> int:
    return left ^ right  # (left & ~right) | (~left & right)


def and_truth_table() -> None:
    """
    Таблица истинности для x and y
    """
    nl = '\n'
    print(f"X{'AND':^5}Y | Z\n{nl.join(f'{left}{right:>6} | {left & right}' for left, right in pairs)}")


def or_truth_table() -> None:
    """
    Таблица истинности для x or y
    """
    nl = '\n'
    print(f"X{'OR':^5}Y | Z\n{nl.join(f'{left}{right:>6} | {left | right}' for left, right in pairs)}")


def xor_truth_table() -> None:
    """
    Таблица истинности для x xor y
    """
    nl = '\n'
    print(f"X{'XOR':^5}Y | Z\n{nl.join(f'{left}{right:>6} | {left ^ right}' for left, right in pairs)}")


def half_summator(left: int, right: int) -> Tuple[int, int]:
    return xor(left, right), left & right


def full_summator(left: int, right: int, carray_in: int) -> Tuple[int, int]:
    """
    param left: левый суммируемый бит
    param right: правый суммируемый бит
    param carray_in: бит переноса
    return: значение суммы и бит переноса
    """
    summ_1, carry_1 = half_summator(left, right)
    summ_2, carry_2 = half_summator(summ_1, carray_in)
    return summ_2, carry_1 | carry_2


def _dec_to_bin_generator(value: int):
    """
    Генератор для перевода числа в массив байт.
    """
    for bit in range(INT_BITS_COUNT - 1):
        yield 0 if value % 2 == 0 else 1
        value //= 2
    yield 0  # sign bit


def invert_bits(bits: Tuple[int, ...]):
    return tuple(0 if v == 1 else 1 for v in bits)


def dec_to_bin(value: int):
    """
    Перевод числа в массив байт.
    """
    if value >= 0:
        return tuple(_dec_to_bin_generator(value))
    # дополненный код ~(value) + 1
    return _summator(invert_bits(tuple(_dec_to_bin_generator(abs(value)))), BINARY_ONE)


def bin_to_int(bits: Tuple[int, ...]) -> int:
    """
    Перевод массива байт в число.
    """
    sign = 1  # множитель знака числа
    if bits[INT_BITS_COUNT - 1] != 0:
        # обращение дополненного кода ~(value) + 1
        bits = _summator(invert_bits(bits), BINARY_ONE)
        sign = -1
    return sign * sum(POWERS_OF_TWO[bit] for bit in range(INT_BITS_COUNT - 1) if bits[bit] != 0)


def _summator_generator(left: Tuple[int, ...], right: Tuple[int, ...]):
    """
    Генератор каскада суммирования
    """
    carry_bit = 0
    for bit in range(INT_BITS_COUNT):
        summ, carry_bit = full_summator(left[bit], right[bit], carry_bit)
        yield summ


def _summator(left: Tuple[int, ...], right: Tuple[int, ...]) -> Tuple[int, ...]:
    """
    Суммирование двух бинарных чисел
    """
    return tuple(_summator_generator(left, right))


def summator(left: int, right: int) -> int:
    """
    Суммирование двух целых чисел
    """
    return bin_to_int(_summator(dec_to_bin(left), dec_to_bin(right)))


def bin_to_str(bytes_data: Tuple[int, ...]) -> str:
    """
    Строковое представление числа, записанного в виде массива байт.
    """
    return f'0b{"".join(str(v) for v in bytes_data[::-1])}'


def multiplicator(left: int, right: int) -> int:
    sign = (1 if left > 0 else -1) * (1 if right > 0 else -1)   # множитель знака произведения чисел left и right
    l_bin = dec_to_bin(abs(left))
    r_bin = dec_to_bin(abs(right))
    m_bin = dec_to_bin(0)
    for shift in range(len(r_bin)):
        t_mul  = dec_to_bin(bin_to_int(tuple(r_bin[shift] & v for v in l_bin)) << shift)
        m_bin = _summator(m_bin, t_mul)
    return sign * bin_to_int(m_bin)


def full_summator_test():
    print(f"{'left':<6} + {'right':<6} + {'carray':<6} = {'summ':<6}, {'carray':<6}")
    for lft, rgt, c_in in full_summator_triples:
        sum_, carry_out = full_summator(lft, rgt, c_in)
        print(f"{lft:^6} + {rgt:^6} + {c_in:^6} = {sum_:^6}, {carry_out:^6}")


def logic_gates_truth_tables():
    or_truth_table()
    print()
    and_truth_table()
    print()
    xor_truth_table()
    print()


if __name__ == "__main__":
    left = -22
    right = 12
    left_bin = dec_to_bin(left)
    right_bin  = dec_to_bin(right)
    print(f"Число {left:^5} в бинарной форме: {bin_to_str(left_bin)}. Размер целого числа {INT_BITS_COUNT} бит.")
    print(f"Число {right:^5} в бинарной форме: {bin_to_str(right_bin)}. Размер целого числа {INT_BITS_COUNT} бит.")

    print(f"Восстановленное число {left:^5} из бинарной формы: {bin_to_int(left_bin):^5}")
    print(f"Восстановленное число {right:^5} из бинарной формы: {bin_to_int(right_bin):^5}")

    first = -17
    second = 7
    print(f"{first:^9} + {second:^9} = {first + second:^9} => "
          f"summator     ({first:^9}, {second:^9}) = {summator(first, second):^9}")

    print(f"{first:^9} * {second:^9} = {first * second:^9} => "
          f"multiplicator({first:^9}, {second:^9}) = {multiplicator(first, second):^9}")

