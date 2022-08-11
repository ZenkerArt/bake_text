import bpy
from .anim import Global
from .anim.timeline_states import TimelineState
from .enums import OBJECT_BAKE_TYPE, OBJECT_RENDER_TYPE, COPY_MODE
from .image.operators import image_enum


def cameras(self, obj):
    return obj.type == 'CAMERA'


def update_timeline(self, context):
    Global.timeline.keyframe.update(TimelineState.active_keyframes())


def update__(self, context):
    obj = context.active_object

    copy_from = obj.bt_settings.copy_from
    if copy_from and obj.bt_settings.copy_mode == COPY_MODE.REPLACE:
        keyframes = copy_from.bt_keyframes
    else:
        keyframes = obj.bt_keyframes

    Global.timeline.keyframe.update(keyframes)


class ObjectSettings(bpy.types.PropertyGroup):
    bake_type: bpy.props.EnumProperty(items=(
        (OBJECT_BAKE_TYPE.BAKE_VERTEX, 'Запечь Вершины', ''),
        (OBJECT_BAKE_TYPE.BAKE_LOCATION, 'Запечь Позицию', '')
    ), default=OBJECT_BAKE_TYPE.BAKE_LOCATION)
    image: bpy.props.EnumProperty(items=image_enum)
    render_type: bpy.props.EnumProperty(items=OBJECT_RENDER_TYPE.enum())
    sun_sensitivity: bpy.props.FloatProperty(default=4)

    copy_mode: bpy.props.EnumProperty(items=(
        (COPY_MODE.MIX, 'Микс', 'Микс'),
        (COPY_MODE.REPLACE, 'Заменить', 'Заменить')
    ), default=COPY_MODE.MIX, update=update__)
    copy_from: bpy.props.PointerProperty(
        type=bpy.types.Object, update=update_timeline)


class InversSettings(bpy.types.PropertyGroup):
    position: bpy.props.BoolVectorProperty(subtype='XYZ')
    rotation: bpy.props.BoolVectorProperty(subtype='XYZ')
    scale: bpy.props.BoolVectorProperty(subtype='XYZ')


class SceneSettings(bpy.types.PropertyGroup):
    save_type: bpy.props.EnumProperty(items=[
        ('copy_buffer', 'Сохранить в буфер обмена', ''),
        ('file', 'Сохранить в файл', '')
    ])
    camera: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=cameras
    )
    camera_expression: bpy.props.StringProperty(default='abs(cam.location.y)')
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
))


def register():
    reg()

    bpy.types.Scene.bt_settings = bpy.props.PointerProperty(
        type=SceneSettings)

    bpy.types.Scene.bt_invers = bpy.props.PointerProperty(
        type=InversSettings)
    bpy.types.Object.bt_settings = bpy.props.PointerProperty(type=ObjectSettings)

    bpy.types.Scene.bt_cameras = bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=cameras
    )


def unregister():
    unreg()
