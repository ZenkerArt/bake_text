import bpy
from bpy.types import Object, Context

ObjVector = tuple[float, float, float]
ObjBool = tuple[bool, bool, bool]
ObjStr = tuple[str, str, str]
ObjTransform = tuple[ObjVector, ObjVector, ObjVector]
ObjTransformStr = tuple[ObjStr, ObjStr, ObjStr]
ObjData = tuple[int, tuple[ObjBool, ObjBool, ObjBool], Object, str]


def calc_time(frame: float) -> float:
    settings = bpy.context.scene.bt_settings
    fps = settings.fps
    offset = settings.offset
    accuracy = settings.accuracy

    t = frame / fps + offset
    t = round(t, accuracy)
    return t


def xyz_to_xzy(value) -> ObjVector:
    return value[0], value[2], value[1]


def invers_convert(value):
    value = value[0], value[2], value[1]
    return tuple(-1 if d else 1 for d in value)


def get_global_div(context: Context):
    settings = context.scene.bt_settings

    global_location = xyz_to_xzy(settings.global_location)
    global_rotation = xyz_to_xzy(settings.global_rotation)
    global_scale = xyz_to_xzy(settings.global_scale)

    return global_location, global_rotation, global_scale


def apply_transforms(arr: list[ObjTransform]) -> list[ObjTransformStr]:
    context = bpy.context
    scene = context.scene

    invers = scene.bt_invers
    settings = context.scene.bt_settings
    accuracy = settings.accuracy

    inv = (invers_convert(invers.position), invers_convert(invers.rotation), invers_convert(invers.scale))
    global_div = (xyz_to_xzy(settings.global_div),) * 3
    arr = (arr * inv) / global_div / get_global_div(context)
    arr = arr.round(accuracy)
    arr = arr.astype(str)

    return arr
