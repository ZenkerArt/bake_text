from typing import TypeVar, Generic

from ..objects import RGB

_T = TypeVar('_T')


class StyleState(Generic[_T]):
    hover: _T
    normal: _T

    def __init__(self, normal: _T, hover: _T):
        self.hover = hover
        self.normal = normal


class TimelineStyle:
    accent = RGB(66, 109, 174)
    keyframe = RGB(239, 83, 80)
    keyframe_active = RGB(255, 205, 210)
    bg = RGB.fill(20)

    title_height = 35
    line_offset = 10

    cursor = StyleState(normal=accent + 40, hover=accent + 100)
    cursor_wh = StyleState(normal=4, hover=6)
