import bpy
from ..enums import EVENTS_LOCAL
from ..image.operators import image_enum


def update(self, context):
    self.command = self.label()


class TimelineKeyframe(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty()
    name: bpy.props.StringProperty()
    command: bpy.props.StringProperty()

    event: bpy.props.EnumProperty(items=EVENTS_LOCAL.enum(), update=update)

    color: bpy.props.FloatVectorProperty(subtype='COLOR', default=[1.0, 1.0, 1.0])
    image: bpy.props.EnumProperty(items=image_enum)
    sun_sensitivity: bpy.props.FloatProperty(default=10)
    set_player_dist: bpy.props.FloatProperty(default=4)

    def label(self):
        return EVENTS_LOCAL.normal_name(self.event)


reg, unreg = bpy.utils.register_classes_factory((
    TimelineKeyframe,
))


def register():
    reg()
    bpy.types.Object.bt_keyframes = bpy.props.CollectionProperty(type=TimelineKeyframe)


def unregister():
    unreg()


if __name__ == "__main__":
    register()
