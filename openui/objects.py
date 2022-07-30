from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Iterable, Union

import numpy

import blf
from bpy.types import Event, Context
from gpu.shader import from_builtin
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector
from .collison import BoundingBox

Vertices = Iterable[tuple[float, float]]
Indices = Iterable[tuple[float, float, float]]
DrawReturn = tuple[Vertices, Indices]


def simple_align(obj: 'Obj', m: tuple[float, float]):
    px, py = obj.pos
    x_max, y_max = m

    if obj._align_x == ALIGN.CENTER:
        px -= x_max / 2

    if obj._align_y == ALIGN.CENTER:
        py -= y_max / 2

    return px, py


class ALIGN(Enum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()


class RGB:
    _rgba: numpy.ndarray

    def __init__(self, r: int = 0, g: int = 0, b: int = 0, a: int = 255):
        self._rgba = numpy.array([r, g, b, a])

    @classmethod
    def fill(cls, value: int, a: int = 255):
        return cls(*(value,) * 3, a)

    def set(self, r: int = None, g: int = None, b: int = None, a: int = None):
        rgba = [r, g, b, a]

        for i in range(len(self._rgba)):
            if rgba[i] is None:
                continue
            self._rgba[i] = rgba[i]

    @property
    def normalize(self):
        return self._rgba / 255

    @property
    def rgb(self) -> tuple[float, float, float]:
        return tuple(self.normalize[:2])

    @property
    def rgba(self):
        return tuple(self.normalize)

    def __sub__(self, other: int):
        x = self._rgba - other
        return RGB(*x)

    def __add__(self, other: int):
        x = self._rgba + other
        return RGB(*x)

    def __mul__(self, other: int):
        x = self._rgba * other
        return RGB(*x)


class Obj(ABC):
    _align_x: ALIGN = ALIGN.LEFT
    _align_y: ALIGN = ALIGN.LEFT
    color: RGB
    scale: list[float, float]
    pos: list[float, float]

    def __init__(self):
        self.color = RGB(255, 255, 255)
        self.scale = [1, 1]
        self.pos = [0, 0]
        self.init()

    def init(self):
        pass

    def set_align(self, x: ALIGN = None, y: ALIGN = None):
        self._align_x = x or self._align_x
        self._align_y = y or self._align_y
        return self

    def set_color(self, r: Union[int, RGB] = None, g: int = None, b: int = None, a: int = None, fill: int = None):
        if isinstance(r, RGB):
            self.color = r
            return self

        if fill:
            self.color.set(fill, fill, fill, a)
            return self
        self.color.set(r, g, b, a)
        return self

    def set_scale(self, x: float = None, y: float = None):
        old_x, old_y = self.scale
        self.scale[0] = x or old_x
        self.scale[1] = y or old_y
        return self

    def set_pos(self, x: Union[float, Vector] = None, y: float = None):
        if isinstance(x, Vector):
            self.pos[0], self.pos[1] = x.xy
            return self

        old_x, old_y = self.pos
        self.pos[0] = x or old_x
        self.pos[1] = y or old_y
        return self

    def event(self, context: Context, event: Event):
        pass

    @abstractmethod
    def render(self):
        pass


class Shape(Obj, ABC):
    bounding: BoundingBox

    def __init__(self):
        super().__init__()
        self.bounding = BoundingBox(0, 0, 0, 0)

    @abstractmethod
    def draw(self) -> DrawReturn:
        pass

    def render(self):
        vertices, indices = self.draw()
        vert = []
        sx, sy = self.scale

        a = numpy.array(vertices)
        px, py = simple_align(self, a.max(axis=0))

        scale = Matrix((
            (sx, 0, 0, 0),
            (0, sy, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1)
        ))
        trans = Matrix.Translation(Vector((px, py, 0)))
        mat = trans @ scale

        for i in vertices:
            vec = Vector((*i, 0))
            vert.append((mat @ vec).xy)

        a = numpy.array(vert)
        b = (*a.min(axis=0), *a.max(axis=0))
        self.bounding = BoundingBox(*b)

        shader = from_builtin('2D_UNIFORM_COLOR')

        batch = batch_for_shader(
            shader, 'TRIS', {'pos': vert}, indices=indices)

        shader.bind()
        shader.uniform_float('color', self.color.rgba)
        batch.draw(shader)
        return self


class Box(Shape):
    _wh: tuple[float, float] = (0, 0)
    _padding: tuple[float, float] = (0, 0)

    def padding(self, x: float = None, y: float = None):
        px, py = self._padding
        self._padding = x or px, y or py
        return self

    def set_wh(self, w: float = None, h: float = None):
        px, py = self._wh
        self._wh = w or px, h or py
        return self

    def draw(self) -> DrawReturn:
        width, height = self._wh
        px, py = self._padding

        vertices = (
            (0, 0), (width + px, 0),
            (0, height), (width + px, height)
        )

        indices = (
            (0, 1, 2), (2, 1, 3))

        return vertices, indices


class Text(Obj):
    DPI: int = 120
    _text: str

    def set_text(self, value: Union[str, float]):
        self._text = value
        return self

    def dimensions(self):
        sx, sy = self.scale

        blf.size(0, sx, self.DPI)
        return blf.dimensions(0, str(self._text))

    def render(self):
        sx, sy = self.scale

        blf.size(0, sx, self.DPI)
        wt, ht = blf.dimensions(0, str(self._text))
        px, py = simple_align(self, (wt, ht))

        blf.position(0, px, py, 0)
        blf.color(0, *self.color.rgba)
        blf.draw(0, str(self._text))
