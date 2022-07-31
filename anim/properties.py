import bpy


class TimelineKeyframe(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty()
    name: bpy.props.StringProperty()


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
