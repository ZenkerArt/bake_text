import bpy
from ..anim.timeline_states import TIMELINE_STATE
from ..enums import EVENTS_LOCAL, EVENTS_GLOBAL
from ..image.operators import image_enum





def update(self, context):
    self.command = self.label()


class BaseKeyframe:
    index: bpy.props.IntProperty()
    name: bpy.props.StringProperty()
    command: bpy.props.StringProperty()

    event: bpy.props.EnumProperty(items=EVENTS_LOCAL.enum(), update=update)

    def label(self):
        return EVENTS_LOCAL.normal_name(self.event)


class TimelineKeyframe(BaseKeyframe, bpy.types.PropertyGroup):
    color: bpy.props.FloatVectorProperty(subtype='COLOR', default=[1.0, 1.0, 1.0])
    image: bpy.props.EnumProperty(items=image_enum)
    sun_sensitivity: bpy.props.FloatProperty(default=10)
    set_player_dist: bpy.props.FloatProperty(default=4)


class GTimelineKeyframe(BaseKeyframe, bpy.types.PropertyGroup):
    event: bpy.props.EnumProperty(items=EVENTS_GLOBAL.enum(), update=update)
    player_dist: bpy.props.FloatProperty(default=4)


class SettingsTimeline(bpy.types.PropertyGroup):
    state: bpy.props.IntProperty(default=TIMELINE_STATE.OBJECT.value)
    time_unit: bpy.props.IntProperty()

    @staticmethod
    def keyframes():
        return bpy.context.scene.bt_keyframes


reg, unreg = bpy.utils.register_classes_factory((
    TimelineKeyframe,
    GTimelineKeyframe,
    SettingsTimeline
))


def register():
    reg()
    bpy.types.Object.bt_keyframes = bpy.props.CollectionProperty(type=TimelineKeyframe)
    bpy.types.Scene.bt_keyframes = bpy.props.CollectionProperty(type=GTimelineKeyframe)
    bpy.types.Scene.bt_store_timeline = bpy.props.PointerProperty(type=SettingsTimeline)


def unregister():
    unreg()


if __name__ == "__main__":
    register()
