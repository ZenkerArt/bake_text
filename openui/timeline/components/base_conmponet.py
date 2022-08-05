from typing import TYPE_CHECKING

from ..shapes import TimelineShapes
from ..tstyle import TimelineStyle

if TYPE_CHECKING:
    from .. import Timeline


class BaseComponent:
    timeline: 'Timeline'
    style: TimelineStyle
    shapes: TimelineShapes
    wh: tuple[float, float]

    def __init__(self, timeline: 'Timeline'):
        self.timeline = timeline
        self.style = timeline.style
        self.shapes = timeline.shapes
        self.init()

    def init(self):
        pass

    @property
    def ext(self):
        return self.timeline.ext

    @property
    def matrix(self):
        return self.timeline.matrix

    @property
    def wh(self):
        return self.timeline.wh
