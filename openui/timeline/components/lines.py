from .base_conmponet import BaseComponent
from ..ext import FrameInfo


class TimelineLines(BaseComponent):
    def draw(self):
        frame = FrameInfo()
        style = self.style

        width, height = self.wh
        accent = style.accent
        line_offset = style.line_offset

        for index in range(frame.start, frame.end + 1):
            vec = self.matrix * (index * line_offset)

            if vec.x > width or vec.x < 0:
                continue

            line = self.shapes.draw_line(vec)

            if index % (line_offset / 2) == 0:
                line.set_wh(1)
                line.set_color(line.color + 60)

            if index % line_offset == 0:
                self.shapes.draw_text_in_header(vec.x, str(index)).render()
                line.set_color(accent + 40).set_wh(2)

            line.render()