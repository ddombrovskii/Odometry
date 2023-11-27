from ...Common.color import Color
from ..vector2 import Vector2
from enum import Enum


_indent_level = 0
_indent = ''


class Units(Enum):
    Inches = 0
    Millimeters = 1
    Centimeters = 2
    Pixels = 3
    Meters = 4
    Percent = 5
    Points = 6


STROKE_LINE_CAPS = {'butt', 'round', 'square'}
STROKE_LINE_JOINS = {'miter', 'round', 'bevel'}
UNITS_SUFFIX = {Units.Inches: 'in',
                Units.Millimeters: 'mm',
                Units.Pixels: 'px',
                Units.Points: 'pt',
                Units.Meters: 'm',
                Units.Percent: '%'}


def _color_code(c: Color) -> str:
    return f"#{int(c)}"


class StrokeStyle:
    def __init__(self):
        self._fill: bool = False
        self._stroke_color: Color = Color(0, 0, 0)
        self._fill_color: Color = Color(255, 255, 255)
        self._stroke_width = 0.2
        self._stroke_units: Units = Units.Centimeters

    @property
    def fill(self) -> bool:
        return self._fill

    @property
    def stroke_color(self) -> Color:
        return self._stroke_color

    @property
    def fill_color(self) -> Color:
        return self._fill_color

    @property
    def stroke_width(self) -> float:
        return self._stroke_width

    @property
    def stroke_units(self) -> Units:
        return self._stroke_units

    @fill.setter
    def fill(self, value: bool) -> None:
        assert isinstance(value, bool)
        self._fill = value

    @stroke_color.setter
    def stroke_color(self, value: bool) -> None:
        assert isinstance(value, Color)
        self._stroke_color = value

    @fill_color.setter
    def fill_color(self, value: bool) -> None:
        assert isinstance(value, Color)
        self._fill_color = value

    @stroke_width.setter
    def stroke_width(self, value: float) -> None:
        assert isinstance(value, float)
        self._stroke_width = value

    @stroke_units.setter
    def stroke_units(self, value: float) -> None:
        assert isinstance(value, Units)
        self._stroke_units = value

    @property
    def svg_code(self) -> str:
        return f'fill=\"{_color_code(self.fill_color) if self.fill else "none"}\" ' \
               f'stroke=\"{_color_code(self.stroke_color) if self.fill else "none"}\" ' \
               f'stroke-width=\"{self.stroke_width}{UNITS_SUFFIX[self.stroke_units]}\"'


def _render_rectangle(p1: Vector2, p2: Vector2, units: Units, style: StrokeStyle):
    u = UNITS_SUFFIX[units]
    return f"{_indent}<rect x=\"{p1.x:.3f}{u}\" y=\"{p1.y:.3f}{u}\" " \
           f"width=\"{p1.x - p2.x:.3f}{u}\" height=\"{p1.y - p2.y:.3f}{u}\" " \
           f"{style.svg_code}></rect>"

