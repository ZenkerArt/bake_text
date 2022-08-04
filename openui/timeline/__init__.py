from typing import Union, TypeVar, Any
from uuid import uuid4

import numpy

import bpy
from bpy.types import Event, Context
from mathutils import Matrix, Vector
from .matrix import TimelineMatrix
from .tstyle import TimelineStyle
from ..collison import BoundingBox
from ..objects import Obj, RGB, Box, ALIGN, Text
from ..timeline.ext import TimelineExt, TimelineActiveObj, TimelineExtGroup, REGION, Keyframe, TimelineMove

_T = TypeVar('_T')


class FrameInfo:
    start: int
    end: int
    curr: int

    def __init__(self):
        scene = bpy.context.scene
        self.end, self.start, self.curr = scene.frame_end, scene.frame_start, scene.frame_current


class Timeline(Obj):
    _wh: tuple[float, float] = 0, 0
    zoom: float = 1
    scroll = 0
    style = TimelineStyle()
    cursor: Box
    ext: TimelineExtGroup
    keyframes: dict[str, Keyframe] = {}

    def init(self):
        self.ext = TimelineExtGroup(self)

        self.cursor = Box() \
            .set_color(self.style.cursor.normal) \
            .set_align(ALIGN.CENTER) \
            .set_wh(self.style.cursor_wh.normal)

    def event(self, context: Context, event: Event):
        bounding = BoundingBox(
            *self.pos, *tuple(numpy.array(self.pos) + numpy.array(self._wh)))
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
        self._wh = width, height

    @property
    def matrix(self) -> TimelineMatrix:
        scale = Matrix.Scale(self.zoom, 4)
        trans = Matrix.Translation(Vector((self.scroll, 0, 0)))
        mat = trans @ scale
        return TimelineMatrix(mat, self)

    def add_keyframe(self, index: int, event: str = None):
        obj = self.ext.get_ext(TimelineActiveObj).obj
        m = self.ext.get_ext(TimelineMove)

        ids = str(uuid4())
        keyframe = obj.bt_keyframes.add()
        keyframe.index = index
        keyframe.name = ids
        keyframe.command = keyframe.label()
        keyframe.event = event or keyframe.event
        self.keyframes[ids] = Keyframe(keyframe, self)
        m.active_keyframe = self.keyframes[ids]

    def _draw_line(self, vec: Vector):
        style = self.style

        width, height = self._wh
        title_height = style.title_height
        accent = self.style.accent
        line_top_offset = height - title_height * 2

        line = Box()
        line.set_pos(vec + Vector((0, title_height, 0)))
        line.set_wh(1, line_top_offset)
        line.set_color(accent - 40)
        line.set_align(ALIGN.CENTER)

        return line

    def _draw_lines(self):
        frame = FrameInfo()
        style = self.style

        width, height = self._wh
        accent, bg = style.accent, style.bg
        title_height, line_offset = style.title_height, style.line_offset

        def text(v: Vector, t: Union[str, float]):
            Text() \
                .set_pos(v.x, height - title_height / 2) \
                .set_scale(8) \
                .set_align(ALIGN.CENTER, ALIGN.CENTER) \
                .set_text(t) \
                .set_color(RGB.fill(150)) \
                .render()

        for index in range(frame.start, frame.end + 1):
            vec = self.matrix * (index * line_offset)

            if vec.x > width or vec.x < 0:
                continue

            line = self._draw_line(vec)

            if index % (line_offset / 2) == 0:
                line.set_wh(1)
                line.set_color(line.color + 60)

            if index % line_offset == 0:
                text(vec, index)
                line.set_color(accent + 40).set_wh(2)

            line.render()

    def _cursor(self):
        frame = FrameInfo()
        style = self.style
        width, height = self._wh
        mat = self.matrix

        vec_frame = mat * (frame.curr * style.line_offset, 0, 1)

        cursor = self.cursor
        cursor.set_pos(vec_frame).set_wh(
            h=height - style.title_height).render()

        p = vec_frame + Vector((0, height - style.title_height / 2, 0))
        text = Text()
        text.set_scale(8)
        text.set_pos(p)
        text.set_align(ALIGN.CENTER, ALIGN.CENTER)
        text.set_text(frame.curr)
        text.set_color(RGB.fill(255))

        wt, ht = text.dimensions()

        b = Box().padding(20)
        b.set_pos(p)
        b.set_wh(wt, style.title_height)
        b.set_color(style.bg)
        b.set_align(ALIGN.CENTER, ALIGN.CENTER)
        b.render()

        text.render()

    def _draw_keyframes(self):
        width, height = self._wh

        for i in self.keyframes.values():

            line, text = i.get_line()

            if line.pos[0] > width or line.pos[0] < 0:
                continue

            line.set_wh(2)

            line.render()
            text.render()

    def render(self):
        style = self.style
        width, height = self._wh
        accent, bg = style.accent, style.bg

        Box().set_wh(width, height).set_color(bg).render()  # Background

        self._draw_lines()
        self._draw_keyframes()
        self._cursor()
