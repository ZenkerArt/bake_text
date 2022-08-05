from mathutils import Vector
from .base_conmponet import BaseComponent
from ..ext import FrameInfo
from ...objects import Box, ALIGN, RGB


class TimelineCursor(BaseComponent):
    cursor: Box

    def init(self):
        self.cursor = Box() \
            .set_color(self.style.cursor.normal) \
            .set_align(ALIGN.CENTER) \
            .set_wh(self.style.cursor_wh.normal)

    def draw(self):
        frame = FrameInfo()
        style = self.style
        width, height = self.wh
        mat = self.matrix

        vec_frame = mat * (frame.curr * style.line_offset, 0, 1)

        cursor = self.cursor
        cursor.set_pos(vec_frame).set_wh(
            h=height - style.title_height).render()

        p = vec_frame + Vector((0, height - style.title_height / 2, 0))
        text = self.shapes.draw_text_in_header(p.x, str(frame.curr))

        text.set_align(ALIGN.CENTER, ALIGN.CENTER)
        text.set_color(RGB.fill(255))

        wt, ht = text.dimensions()

        b = Box().padding(20)
        b.set_pos(p)
        b.set_wh(wt, style.title_height)
        b.set_color(style.bg)
        b.set_align(ALIGN.CENTER, ALIGN.CENTER)
        b.render()

        text.render()
