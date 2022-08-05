from mathutils import Vector
from ..objects import Box, ALIGN, Text, RGB
from typing import TYPE_CHECKING
from .tstyle import TimelineStyle

if TYPE_CHECKING:
    from . import Timeline


class TimelineShapes:
    timeline: 'Timeline'
    style: TimelineStyle
    wh: tuple[float, float]

    def __init__(self, timeline: 'Timeline'):
        self.timeline = timeline
        self.style = timeline.style

    @property
    def wh(self):
        return self.timeline.wh

    def draw_line(self, vec: Vector) -> Box:
        style = self.style

        width, height = self.wh
        title_height = style.title_height
        accent = style.accent
        line_top_offset = height - title_height * 2

        line = Box()
        line.set_pos(vec + Vector((0, title_height, 0)))
        line.set_wh(1, line_top_offset)
        line.set_color(accent - 40)
        line.set_align(ALIGN.CENTER)

        return line

    @staticmethod
    def draw_text(pos: tuple[float, float], text: str, color: RGB = RGB.fill(150)) -> Text:
        return Text() \
            .set_pos(*pos) \
            .set_scale(8) \
            .set_align(ALIGN.CENTER, ALIGN.CENTER) \
            .set_text(text) \
            .set_color(color)

    def draw_text_in_header(self, x: float, text: str) -> Text:
        style = self.style

        width, height = self.wh
        title_height, line_offset = style.title_height, style.line_offset
        pos = x, height - title_height / 2

        return self.draw_text(pos, text)

    def draw_text_in_footer(self, x: float, text: str):
        style = self.style

        title_height, line_offset = style.title_height, style.line_offset
        pos = x, title_height / 2

        return self.draw_text(pos, text)
