import bpy


class InversSettings(bpy.types.PropertyGroup):
    position: bpy.props.BoolVectorProperty(subtype='XYZ')
    rotation: bpy.props.BoolVectorProperty(subtype='XYZ')
    scale: bpy.props.BoolVectorProperty(subtype='XYZ')


class BakeTextSettings(bpy.types.PropertyGroup):
    save_type: bpy.props.EnumProperty(items=[
        ('copy_buffer', 'Сохранить в буфер обмена', ''),
        ('file', 'Сохранить в файл', '')
    ])

    fps: bpy.props.FloatProperty(default=30.0)
    offset: bpy.props.FloatProperty(default=1.0)
    path: bpy.props.StringProperty(
        subtype='FILE_PATH', default='//untitled.json')

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
    BakeTextSettings,
    InversSettings,
))


def register():
    reg()
    bpy.types.Scene.bake_text_settings = bpy.props.PointerProperty(
        type=BakeTextSettings)

    bpy.types.Scene.bake_text_invers = bpy.props.PointerProperty(
        type=InversSettings)


def unregister():
    del bpy.types.Scene.bake_text_settings

    unreg()
