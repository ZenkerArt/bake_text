from typing import Iterable, Union, TYPE_CHECKING

from mathutils import Matrix, Vector

if TYPE_CHECKING:
    from ..timeline import Timeline


class TimelineMatrix:
    mat: Matrix
    timeline: 'Timeline'

    def __init__(self, mat: Matrix, timeline: 'Timeline'):
        self.mat = mat
        self.timeline = timeline

    def apply(self, x: float = 0, y: float = 0, z: float = 0) -> Vector:
        vec = self.mat @ Vector((x, y, z))
        return vec

    def transform(self, x: float = 0):
        x -= self.timeline.scroll
        return round((x / self.timeline.style.line_offset) / self.timeline.zoom)

    def __mul__(self, other: Union[float, int, Iterable, Vector]):
        if isinstance(other, float) or isinstance(other, int):
            return self.apply(other)

        if isinstance(other, Iterable):
            return self.apply(*other)
