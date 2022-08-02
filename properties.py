import bpy
from .progress_bar import ProgressBar
from .enums import OBJECT_BAKE_TYPE, OBJECT_RENDER_TYPE
from .image.operators import image_enum


class ObjectSettings(bpy.types.PropertyGroup):
    bake_type: bpy.props.EnumProperty(items=(
        (OBJECT_BAKE_TYPE.BAKE_VERTEX, 'Запечь Вершины', ''),
        (OBJECT_BAKE_TYPE.BAKE_LOCATION, 'Запечь Позицию', '')
    ), default=OBJECT_BAKE_TYPE.BAKE_LOCATION)
    image: bpy.props.EnumProperty(items=image_enum)
    render_type: bpy.props.EnumProperty(items=OBJECT_RENDER_TYPE.enum())
    sun_sensitivity: bpy.props.FloatProperty(default=4)


class InversSettings(bpy.types.PropertyGroup):
    position: bpy.props.BoolVectorProperty(subtype='XYZ')
    rotation: bpy.props.BoolVectorProperty(subtype='XYZ')
    scale: bpy.props.BoolVectorProperty(subtype='XYZ')


class SceneSettings(bpy.types.PropertyGroup):
    save_type: bpy.props.EnumProperty(items=[
        ('copy_buffer', 'Сохранить в буфер обмена', ''),
        ('file', 'Сохранить в файл', '')
    ])

    fps: bpy.props.FloatProperty(default=30.0)
    offset: bpy.props.FloatProperty(default=1.0)
    path: bpy.props.StringProperty(
        subtype='FILE_PATH', default='//untitled.json')

    project_name: bpy.props.StringProperty()
    project_folder: bpy.props.StringProperty(
        subtype='DIR_PATH')

    global_location: bpy.props.FloatVectorProperty(
        default=(1.0,) * 3, subtype='XYZ')
    global_rotation: bpy.props.FloatVectorProperty(
        default=(1.0,) * 3, subtype='XYZ')
    global_scale: bpy.props.FloatVectorProperty(
        default=(1.0,) * 3, subtype='XYZ')
    global_div: bpy.props.FloatVectorProperty(
        default=(1.0,) * 3, subtype='XYZ')

    accuracy: bpy.props.IntProperty(default=4, min=0, max=20)


reg, unreg = bpy.utils.register_classes_factory((
    SceneSettings,
    InversSettings,
    ObjectSettings,
    ProgressBar
))


def register():
    reg()
    ProgressBar.register()

    bpy.types.Scene.bt_settings = bpy.props.PointerProperty(
        type=SceneSettings)

    bpy.types.Scene.bt_invers = bpy.props.PointerProperty(
        type=InversSettings)
    bpy.types.Object.bt_settings = bpy.props.PointerProperty(type=ObjectSettings)


def unregister():
    unreg()
