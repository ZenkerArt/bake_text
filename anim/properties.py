from ..enums import OBJECT_BAKE_TYPE
import bpy


class ObjectSettings(bpy.types.PropertyGroup):
    bake_type: bpy.props.EnumProperty(items=(
        (OBJECT_BAKE_TYPE.BAKE_VERTEX, 'Запечь Вершины', ''),
        (OBJECT_BAKE_TYPE.BAKE_LOCATION, 'Запечь Позицию', '')
    ), default=OBJECT_BAKE_TYPE.BAKE_LOCATION)


class TimelineKeyframe(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty()
    name: bpy.props.StringProperty()


reg, unreg = bpy.utils.register_classes_factory((
    ObjectSettings,
    TimelineKeyframe
))


def register():
    reg()
    bpy.types.Object.bt_settings = bpy.props.PointerProperty(
        type=ObjectSettings)
    bpy.types.Object.bt_keyframes = bpy.props.CollectionProperty(type=TimelineKeyframe)


def unregister():
    unreg()


if __name__ == "__main__":
    register()
