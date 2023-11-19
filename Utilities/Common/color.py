from typing import Tuple, List

_r_shift = 0
_g_shift = 8
_b_shift = 16
_a_shift = 24
_255     = 255
_mask_r  = _255 << _r_shift
_mask_g  = _mask_r << _g_shift
_mask_b  = _mask_r << _b_shift
_mask_a  = _mask_r << _a_shift


def create_color_rgba(*rgba) -> int:
    assert len(rgba) == 4
    color: int = 0
    color |= ((int(rgba[0]) & _255) << _r_shift)
    color |= ((int(rgba[1]) & _255) << _g_shift)
    color |= ((int(rgba[2]) & _255) << _b_shift)
    color |= ((int(rgba[3]) & _255) << _a_shift)
    return color


def create_color_rgb(*rgb) -> int:
    assert len(rgb) == 3
    color: int = 0
    color |= ((int(rgb[0]) & _255) << _r_shift)
    color |= ((int(rgb[1]) & _255) << _g_shift)
    color |= ((int(rgb[2]) & _255) << _b_shift)
    return color


def _get_channel(value: int, stride: int) -> int:
    return (value & (_255 << stride)) >> stride


def _red(value: int) -> int:
    return _get_channel(value, _r_shift)  # (value & _mask_r) >> _r_shift


def _green(value: int) -> int:
    return _get_channel(value, _g_shift)  # (value & _mask_g) >> _g_shift


def _blue(value: int) -> int:
    return _get_channel(value, _b_shift)  # (value & _mask_b) >> _b_shift


def _alpha(value: int) -> int:
    return _get_channel(value, _a_shift)  # (value & _mask_a) >> _a_shift


def _set_channel(channels: int, channel: int, channel_stride: int) -> int:
    channels &= ~(_255 << channel_stride)
    channels |= (channel & _255) << channel_stride
    return channels


def _set_red(value: int, value_red: int) -> int:
    return _set_channel(value, value_red, _r_shift)


def _set_green(value: int, value_green: int) -> int:
    return _set_channel(value, value_green, _g_shift)


def _set_blue(value: int, value_blue: int) -> int:
    return _set_channel(value, value_blue, _b_shift)


def _set_alpha(value: int, value_alpha: int) -> int:
    return _set_channel(value, value_alpha, _a_shift)


class Color:
    @staticmethod
    def _build_color_single_arg(arg) -> int:
        if isinstance(arg, Color):
            return int(arg)
        if isinstance(arg, int):
            return create_color_rgba(arg, arg, arg, arg)
        if isinstance(arg, float):
            c = int(255 * arg)
            return create_color_rgba(c, c, c, 0)

    @staticmethod
    def _build_color_three_arg(r, g, b) -> int:
        return create_color_rgb(r, g, b)

    @staticmethod
    def _build_color_four_arg(r, g, b, a) -> int:
        return create_color_rgba(r, g, b, a)

    _build_methods = {0: lambda: 0,
                      1: _build_color_single_arg,
                      3: _build_color_three_arg,
                      4: _build_color_four_arg}

    @staticmethod
    def _unpack_args(*args) -> int:
        args = args[0]
        n_args = len(args)
        if n_args not in Color._build_methods:
            raise ValueError(f"Unsupported amount of args in Color init method. "
                             f"Args: [{', '.join(str(v) for v in args)}]")
        return Color._build_methods[n_args](*args)

    __slots__ = "_rgba"

    def __init__(self, *args):
        self._rgba: int = Color._unpack_args(args)

    def __int__(self) -> int:
        return self._rgba

    def __str__(self):
        return f"{{" \
               f"\"red\"  : {self.red:>3}, " \
               f"\"green\": {self.green:>3}, " \
               f"\"blue\" : {self.blue:>3}, " \
               f"\"alpha\": {self.alpha:>3}" \
               f"}}"

    def __getitem__(self, index: int):
        if index < 0 or index >= 4:
            raise IndexError(f"RGBA color got only 4 components.\n Trying to access index: {index}")
        return _get_channel(self._rgba, index * 8)  # (self._rgba & (255 << (index * 8))) >> (index * 8)

    def __setitem__(self, index: int, value: int):
        if index < 0 or index >= 4:
            raise IndexError(f"RGBA color got only 4 components.\n Trying to access index: {index}")
        self._rgba = _set_channel(self._rgba, int(value) & 255, 8 * index)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Color):
            return False
        if self._rgba != other._rgba:
            return False
        return True

    def __copy__(self):
        color = Color()
        color._rgba = self._rgba
        return color

    copy = __copy__

    def __hash__(self) -> int:
        return hash(self._rgba)

    def __iadd__(self, other):
        if isinstance(other, Color):
            self.red   = (self.red   + other.red)   & 255
            self.green = (self.green + other.green) & 255
            self.blue  = (self.blue  + other.blue)  & 255
            self.alpha = (self.alpha + other.alpha) & 255
            return self
        if isinstance(other, int) or isinstance(other, float):
            self.red   = int(self.red   + other) & 255
            self.green = int(self.green + other) & 255
            self.blue  = int(self.blue  + other) & 255
            self.alpha = int(self.alpha + other) & 255
            return self
        raise RuntimeError(f"Color::Add::wrong argument type {type(other)}")

    def __add__(self, other):
        new_color = self.copy()
        new_color += other
        return new_color

    __radd__ = __add__

    def __isub__(self, other):
        if isinstance(other, Color):
            self.red   = (self.red   - other.red)   & 255
            self.green = (self.green - other.green) & 255
            self.blue  = (self.blue  - other.blue)  & 255
            self.alpha = (self.alpha - other.alpha) & 255
            return self
        if isinstance(other, int) or isinstance(other, float):
            self.red   = int(self.red   - other) & 255
            self.green = int(self.green - other) & 255
            self.blue  = int(self.blue  - other) & 255
            self.alpha = int(self.alpha - other) & 255
            return self
        raise RuntimeError(f"Color::Isub::wrong argument type {type(other)}")

    def __sub__(self, other):
        new_color = self.copy()
        new_color -= other
        return new_color

    def __rsub__(self, other):
        if isinstance(other, Color):
            new_color = self.copy()
            new_color.red   = (other.red   - self.red  ) & 255
            new_color.green = (other.green - self.green) & 255
            new_color.blue  = (other.blue  - self.blue ) & 255
            new_color.alpha = (other.alpha - self.alpha) & 255
            return new_color
        if isinstance(other, int) or isinstance(other, float):
            new_color = self.copy()
            new_color.red   = int(other - self.red  ) & 255
            new_color.green = int(other - self.green) & 255
            new_color.blue  = int(other - self.blue ) & 255
            new_color.alpha = int(other - self.alpha) & 255
            return new_color
        raise RuntimeError(f"Color::rsub::wrong argument type {type(other)}")

    def __imul__(self, other):
        if isinstance(other, Color):
            self.red   = (self.red   * other.red)   & 255
            self.green = (self.green * other.green) & 255
            self.blue  = (self.blue  * other.blue)  & 255
            self.alpha = (self.alpha * other.alpha) & 255
            return self
        if isinstance(other, int) or isinstance(other, float):
            self.red   = int(self.red   * other) & 255
            self.green = int(self.green * other) & 255
            self.blue  = int(self.blue  * other) & 255
            self.alpha = int(self.alpha * other) & 255
            return self
        raise RuntimeError(f"Color::Add::wrong argument type {type(other)}")

    def __mul__(self, other):
        new_color = self.copy()
        new_color *= other
        return new_color

    __rmul__ = __mul__

    @property
    def red(self) -> int:
        return _red(self._rgba)

    @property
    def green(self) -> int:
        return _green(self._rgba)

    @property
    def blue(self) -> int:
        return _blue(self._rgba)

    @property
    def alpha(self) -> int:
        return _alpha(self._rgba)

    @red.setter
    def red(self, val: int) -> None:
        self._rgba = _set_red(self._rgba, val)

    @green.setter
    def green(self, val: int) -> None:
        self._rgba = _set_green(self._rgba, val)

    @blue.setter
    def blue(self, val: int) -> None:
        self._rgba = _set_blue(self._rgba, val)

    @alpha.setter
    def alpha(self, val: int) -> None:
        self._rgba = _set_alpha(self._rgba, val)

    @property
    def as_tuple(self) -> Tuple[int, int, int, int]:
        return self.red, self.green, self.blue, self.alpha

    @property
    def as_list(self) -> List[int]:
        return [self.red, self.green, self.blue, self.alpha]

    @classmethod
    def color_map_quadratic(cls, map_amount: int = 3) -> list:
        colors = []
        dx = 1.0 / (map_amount - 1)
        for i in range(map_amount):
            xi = i * dx
            colors.append(cls(int(255.0 * max(1.0 - (2.0 * xi - 1.0) ** 2, 0.0)),
                              int(255.0 * max(1.0 - (2.0 * xi - 2.0) ** 2, 0.0)),
                              int(255.0 * max(1.0 - (2.0 * xi - 0.0) ** 2, 0.0))))
        return colors

    @classmethod
    def color_map_linear(cls, map_amount: int = 3) -> list:
        colors = []
        dx = 1.0 / (map_amount - 1)
        for i in range(map_amount):
            xi = i * dx
            colors.append(cls(int(255.0 * max(1.0 - 2.0 * xi, 0.0)),
                              int(255.0 * (1.0 - abs(2.0 * xi - 1.0))),
                              int(255.0 * max(2.0 * xi - 1, 0.0))))
        return colors

    @property
    def matplotlib_color_code(self) -> str:
        return f"#{''.join('{:02X}'.format(a) for a in (self.red, self.green, self.blue))}"

    def __hex__(self):
        return ''.join('{:02X}'.format(a) for a in (self.red, self.green, self.blue, self.alpha))

    def __index__(self):
        return self._rgba

    def __bytes__(self):
        return str(int(self)).encode()


if __name__ == "__main__":
    color1 = Color()
    color1[0] = 10
    color1[1] = 33
    color1[2] = 12
    color2 = Color()
    color2.red   = 22
    color2.green = 23
    color2.blue  = 13

    print(f"int color1: {int(color1)}\nint color2: {int(color2)}")
    print(f"bin color1: {bytes(color1)}\nbin color2: {bytes(color2)}")
    print(f"hex color1: {hex(color1)}\nhex color2: {hex(color2)}")

    print(f"color1           : {color1}")
    print(f"color2           : {color2}")

    print(f"color2 - color1  : {color2 - color1}")
    print(f"color1 - color2  : {color1 - color2}")

    print(f"color2 + color1  : {color1 + color2}")
    color2 += color1
    print(f"color2 * color1  : {color1 * color2}")
    color1 *= color2
    print(f"color2 *= color1 : {color1}")

    def color_get(n: int) -> Tuple[int, ...]:
        if n == 1:
            return 128,
        if n == 3:
            return 128, 138, 148
        if n == 4:
            return 128, 138, 148, 10
    print(Color(*color_get(1)))
    print(Color(*color_get(3)))
    print(Color(*color_get(4)))
"""
"""
