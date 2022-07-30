from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING, Any, Type, TypeVar
from bpy.types import Context, Event, Object
from mathutils import Vector
from ..objects import Box

if TYPE_CHECKING:
    from . import Timeline

_T = TypeVar('_T')

ExtList = list[Type['TimelineExt']]


class REGION:
    GLOBAL = 'GLOBAL'
    LOCAL = 'LOCAL'


class Keyframe:
    keyframe: Any
    timeline: 'Timeline'
    box: Box = None

    def __init__(self, keyframe: Any, timeline: 'Timeline'):
        self.keyframe = keyframe
        self.timeline = timeline

    def get_line(self) -> Box:
        timeline = self.timeline
        vec = timeline.matrix * (self.index * timeline.style.line_offset)

        if self.box is None:
            self.box = timeline._draw_line(vec)
        else:
            self.box.set_pos(vec + Vector((0, self.box.pos[1], 0)))

        return self.box

    @property
    def index(self) -> int:
        return self.keyframe.index

    @property
    def obj_id(self) -> str:
        return self.keyframe.obj_id


class TimelineExt(ABC):
    timeline: 'Timeline'

    def __init__(self, timeline: 'Timeline'):
        self.timeline = timeline

    def reset(self, context: Context, event: Event):
        pass

    @abstractmethod
    def event(self, context: Context, event: Event) -> Optional[str]:
        pass


class TimelineExtGroup:
    glob: ExtList = []
    local: ExtList = []
    exts: list[tuple[TimelineExt, str]]
    timeline: 'Timeline'

    def __init__(self, timeline: 'Timeline'):
        self.timeline = timeline
        self.exts = []
        self.register()

    def _register(self, exts: ExtList, region: str):
        for i in exts:
            ext = i(self.timeline), region
            self.exts.append(ext)

    def register(self):
        self._register(self.glob, region=REGION.GLOBAL)
        self._register(self.local, region=REGION.LOCAL)

    def get_ext(self, cls: Type[_T]) -> _T:
        for ins, reg in self.exts:
            if isinstance(ins, cls):
                return ins

    def event(self, context: Context, event: Event, region: str) -> Optional[str]:
        for cls, reg in self.exts:
            if reg != region:
                continue
            e = cls.event(context, event)
            if e:
                return e

    def reset(self, context: Context, event: Event):
        for cls, region in self.exts:
            return cls.event(context, event)


class TimelineControl(TimelineExt):
    zoom_factor = 1.1
    click: bool = False
    offset: float = 0
    prev_offset: float = 0

    def event(self, context: Context, event: Event):
        zoom_factor = self.zoom_factor
        timeline = self.timeline
        old_scale = timeline.zoom
        mouse = event.mouse_region_x
        offset = timeline.scroll
        diff_scale = mouse / old_scale - offset / old_scale

        if event.type == 'MIDDLEMOUSE':
            self.click = not self.click
            self.offset = event.mouse_region_x
            self.prev_offset = offset

        if event.type == 'WHEELUPMOUSE':
            timeline.zoom *= zoom_factor
            scalechange = timeline.zoom - old_scale

            timeline.scroll += diff_scale * -scalechange

        if event.type == 'WHEELDOWNMOUSE':
            timeline.zoom /= zoom_factor
            scalechange = timeline.zoom - old_scale

            timeline.scroll -= diff_scale * +scalechange

        if self.click:
            timeline.scroll = self.prev_offset + mouse - self.offset

    def reset(self, context: Context, event: Event):
        self.click = False


class TimelineMove(TimelineExt):
    zoom_factor = 1.1
    click: bool = False
    offset: float = 0
    prev_offset: float = 0

    def event(self, context: Context, event: Event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.click = True
            self.offset = event.mouse_region_x
            self.prev_offset = context.scene.frame_current

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.click = False

        if self.click:
            mouse = self.timeline.matrix.transform(event.mouse_region_x)
            context.scene.frame_current = mouse

    def reset(self, context: Context, event: Event):
        self.click = False


class TimelineActiveObj(TimelineExt):
    obj: Object = None

    def event(self, context: Context, event: Event):
        if context.active_object is None:
            return

        if self.obj and self.obj.name == context.active_object.name:
            return

        timeline = self.timeline
        obj = context.active_object
        self.obj = obj
        timeline.keyframes = {key: Keyframe(value, timeline) for key, value in obj.bt_keyframes.items()}


TimelineExtGroup.local.extend([TimelineControl, TimelineMove])
TimelineExtGroup.glob.append(TimelineActiveObj)
