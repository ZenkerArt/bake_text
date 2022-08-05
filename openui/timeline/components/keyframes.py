from datetime import timedelta
from typing import Any, TYPE_CHECKING, Optional
from uuid import uuid4

from mathutils import Vector
from .base_conmponet import BaseComponent
from ...objects import Box, Text
from ....anim.timeline_states import TimelineState
from ....export.utils import calc_time

if TYPE_CHECKING:
    from .. import Timeline


class Keyframe:
    keyframe: Any
    timeline: 'Timeline'
    box: Box = None
    text: Text = None

    def __init__(self, keyframe: Any, timeline: 'Timeline'):
        self.keyframe = keyframe
        self.timeline = timeline

    def get_line(self) -> tuple[Box, Text]:
        timeline = self.timeline
        vec = timeline.matrix * (self.index * timeline.style.line_offset)
        title_height = self.timeline.style.title_height

        if self.box is None:
            self.box = timeline.shapes.draw_line(vec)
            self.box.set_color(timeline.style.keyframe)
            self.text = self.timeline.shapes.draw_text_in_footer(vec.x, self.command)
        else:
            self.box.set_pos(vec + Vector((0, self.box.pos[1], 0)))
            self.text.set_pos(vec.x, title_height / 2)
            self.text.set_text(self.command)

        return self.box, self.text

    @property
    def name(self) -> str:
        return self.keyframe.name

    @property
    def command(self) -> str:
        return self.keyframe.command

    @property
    def index(self) -> int:
        return self.keyframe.index


class TimelineKeyframes(BaseComponent):
    _active_keyframe: Optional[Keyframe] = None

    keyframes: dict[str, Keyframe] = {}
    context_keyframe: Optional[Keyframe] = None
    mouse_pos: int = 0

    def get_keyframe_by_cord(self, x: float, y: float):
        timeline = self.timeline
        for keyframe in self.keyframes.values():
            keyframe: Keyframe
            collide = keyframe.box.bounding.collide(x, y, add_x=20)
            if collide:
                return keyframe

    @property
    def active_keyframe(self) -> Optional[Keyframe]:
        return self._active_keyframe

    @active_keyframe.setter
    def active_keyframe(self, value: Keyframe):
        if self._active_keyframe:
            self._active_keyframe.box.set_color(self.timeline.style.keyframe)

        self._active_keyframe = value or self._active_keyframe

        if self._active_keyframe and self._active_keyframe.box:
            self._active_keyframe.box.set_color(self.timeline.style.keyframe_active)

    def update(self, keyframes):
        self.keyframes = {key: Keyframe(value, self.timeline) for key, value in keyframes.items()}

    def add_keyframe(self, index: int, event: str = None, keyframes=None):
        ids = str(uuid4())

        keyframes = keyframes if keyframes is not None else TimelineState.active_keyframes()
        keyframe = keyframes.add()
        keyframe.index = index
        keyframe.name = ids
        keyframe.command = keyframe.label()
        keyframe.event = event or keyframe.event

        self.keyframes[ids] = Keyframe(keyframe, self)
        self.active_keyframe = self.keyframes[ids]

    def draw(self):
        width, height = self.wh

        for i in self.keyframes.values():

            line, text = i.get_line()

            if line.pos[0] > width or line.pos[0] < 0:
                continue

            line.set_wh(2)

            line.render()
            text.render()
            tt = timedelta(seconds=round(calc_time(i.index)))
            self.timeline.shapes.draw_text_in_header(text.pos[0], str(tt)).render()
