from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING, Any, Type, TypeVar

import bpy
from bpy.types import Context, Event, Object
from mathutils import Vector
from ..objects import Box, Text, ALIGN, RGB

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
    text: Text = None

    def __init__(self, keyframe: Any, timeline: 'Timeline'):
        self.keyframe = keyframe
        self.timeline = timeline

    def get_line(self) -> tuple[Box, Text]:
        timeline = self.timeline
        vec = timeline.matrix * (self.index * timeline.style.line_offset)
        title_height = self.timeline.style.title_height

        if self.box is None:
            self.box = timeline._draw_line(vec)
            self.box.set_color(timeline.style.keyframe)
            self.text = Text() \
                .set_pos(vec.x, title_height / 2) \
                .set_scale(8) \
                .set_align(ALIGN.CENTER, ALIGN.CENTER) \
                .set_text(self.command) \
                .set_color(RGB.fill(150))

        else:
            self.box.set_pos(vec + Vector((0, self.box.pos[1], 0)))
            self.text.set_pos(vec.x, title_height / 2)
            self.text.set_text(self.command)

        return self.box, self.text

    @property
    def command(self) -> str:
        return self.keyframe.command

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
    prev_offset: float = 0
    _active_keyframe: Optional[Keyframe] = None
    hover_keyframe: Optional[Keyframe] = None
    settings_keyframe: Optional[Keyframe] = None
    mouse: int = 0

    def get_keyframe(self, mx: float, my: float):
        timeline = self.timeline
        for keyframe in timeline.keyframes.values():
            keyframe: Keyframe
            collide = keyframe.box.bounding.collide(mx, my, add_x=10 * timeline.zoom)
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

    def event(self, context: Context, event: Event):
        mx, my = event.mouse_region_x, event.mouse_region_y
        mouse = self.timeline.matrix.transform(mx)
        self.mouse = mouse

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.click = True
            self.offset = event.mouse_region_x
            self.prev_offset = context.scene.frame_current
            keyframe = self.get_keyframe(mx, my)
            self.hover_keyframe = keyframe
            self.active_keyframe = keyframe or self.active_keyframe

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.click = False
            self.hover_keyframe = None

        if event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            keyframe = self.get_keyframe(mx, my)
            self.settings_keyframe = keyframe
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

    def update(self, context: Context, keyframes):
        if context.active_object is None:
            return

        timeline = self.timeline
        timeline.keyframes = {key: Keyframe(value, timeline) for key, value in keyframes.items()}

    def event(self, context: Context, event: Event):
        if self.obj and self.obj.name == context.active_object.name:
            return
        obj = context.active_object
        self.obj = obj
        self.update(context, obj.bt_keyframes)


TimelineExtGroup.local.extend([TimelineControl, TimelineMove])
TimelineExtGroup.glob.append(TimelineActiveObj)
