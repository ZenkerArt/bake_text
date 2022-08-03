import re

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

    replace_image: bpy.props.EnumProperty(items=image_enum)
    set_sun_sens: bpy.props.FloatProperty()
    set_player_dist: bpy.props.FloatProperty()

    def label(self):
        name = re.sub(r'(?<!^)(?=[A-Z])', ' ', self.event)
        return name.title()


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
