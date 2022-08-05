from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING, Type, TypeVar

import bpy
from bpy.types import Context, Event, Object

if TYPE_CHECKING:
    from . import Timeline
    from .components.keyframes import Keyframe

_T = TypeVar('_T')

ExtList = list[Type['TimelineExt']]


class FrameInfo:
    start: int
    end: int
    curr: int

    def __init__(self):
        scene = bpy.context.scene
        self.end, self.start, self.curr = scene.frame_end, scene.frame_start, scene.frame_current


class REGION:
    GLOBAL = 'GLOBAL'
    LOCAL = 'OBJECT'


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

        if event.type == 'MIDDLEMOUSE' and event.value == 'PRESS':
            self.click = not self.click
            self.offset = event.mouse_region_x
            self.prev_offset = offset

        if event.type == 'MIDDLEMOUSE' and event.value == 'RELEASE':
            self.click = False

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
    _active_keyframe: Optional['Keyframe'] = None
    hover_keyframe: Optional['Keyframe'] = None
    settings_keyframe: Optional['Keyframe'] = None
    mouse: int = 0

    def event(self, context: Context, event: Event):
        mx, my = event.mouse_region_x, event.mouse_region_y
        mouse = self.timeline.matrix.transform(mx)
        self.timeline.keyframe.mouse_pos = mouse

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.click = True
            keyframe = self.timeline.keyframe.get_keyframe_by_cord(mx, my)
            self.hover_keyframe = keyframe
            self.timeline.keyframe.active_keyframe = keyframe

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.click = False
            self.hover_keyframe = None

        if event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            keyframe = self.timeline.keyframe.get_keyframe_by_cord(mx, my)

            self.timeline.keyframe.context_keyframe = keyframe
            if keyframe:
                bpy.ops.wm.call_panel(name='BT_PT_settings_menu')
            else:
                bpy.ops.wm.call_menu(name='BT_MT_context_menu')

        if self.hover_keyframe:
            self.hover_keyframe.keyframe.index = mouse
            return

        if self.click:
            context.scene.frame_current = mouse

    def reset(self, context: Context, event: Event):
        self.click = False


class TimelineActiveObj(TimelineExt):
    obj: Object = None

    def event(self, context: Context, event: Event):
        try:
            if self.obj and self.obj.name == context.active_object.name:
                return
            obj = context.active_object
            self.obj = obj
            self.timeline.keyframe.update(obj.bt_keyframes)
        except ReferenceError:
            pass


TimelineExtGroup.local.extend([TimelineControl, TimelineMove])
TimelineExtGroup.glob.append(TimelineActiveObj)
