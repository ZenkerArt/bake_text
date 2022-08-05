from typing import TypeVar

import numpy

from bpy.types import Event, Context
from mathutils import Matrix, Vector
from .components import TimelineCursor, TimelineLines, TimelineKeyframes
from .matrix import TimelineMatrix
from .shapes import TimelineShapes
from .tstyle import TimelineStyle
from ..collison import BoundingBox
from ..objects import Obj, Box
from ..timeline.ext import TimelineExt, TimelineActiveObj, TimelineExtGroup, REGION, TimelineMove, FrameInfo

_T = TypeVar('_T')


class Timeline(Obj):
    wh: tuple[float, float] = 0, 0
    zoom: float = 1
    scroll = 0
    style = TimelineStyle()
    ext: TimelineExtGroup
    shapes: TimelineShapes
    cursor: TimelineCursor
    lines: TimelineLines
    keyframe: TimelineKeyframes

    def init(self):
        self.shapes = TimelineShapes(self)
        self.ext = TimelineExtGroup(self)
        self.cursor = TimelineCursor(self)
        self.lines = TimelineLines(self)
        self.keyframe = TimelineKeyframes(self)

    def event(self, context: Context, event: Event):
        bounding = BoundingBox(
            *self.pos, *tuple(numpy.array(self.pos) + numpy.array(self.wh)))
        mx, my = event.mouse_region_x, event.mouse_region_y

        main_collide = bounding.collide(mx, my)
        width = 0

        for i in context.area.regions:
            if i.type == 'UI':
                width += i.width

        self.set_wh(context.area.width - width, context.area.height / 4)
        self.ext.event(context, event, REGION.GLOBAL)

        if not main_collide:
            self.ext.reset(context, event)
            return

        self.ext.event(context, event, REGION.LOCAL)

        return {'RUNNING_MODAL'}

    def set_wh(self, width: float = None, height: float = None):
        self.wh = width, height

    @property
    def matrix(self) -> TimelineMatrix:
        scale = Matrix.Scale(self.zoom, 4)
        trans = Matrix.Translation(Vector((self.scroll, 0, 0)))
        mat = trans @ scale
        return TimelineMatrix(mat, self)

    def add_keyframe(self, index: int, event: str = None, keyframes=None):
        self.keyframe.add_keyframe(index, event, keyframes)

    def render(self):
        style = self.style
        width, height = self.wh
        accent, bg = style.accent, style.bg

        Box().set_wh(width, height).set_color(bg).render()  # Background

        self.lines.draw()
        self.cursor.draw()
        self.keyframe.draw()
        # self._draw_keyframes()
