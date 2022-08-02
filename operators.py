import json

import numpy

import bpy
from bpy.types import Object, Context
from .btio import ProjectFolders
from .enums import OBJECT_RENDER_TYPE

CONFIG = {
    "configVersion": 3,
    "name": "editor.Test1",
    "info": "Description",
    "levelResources": [],
    "tags": [
        "OneHand"
    ],
    "handCount": 1,
    "moreInfoURL": "",
    "speed": 15.0,
    "lives": 5,
    "maxLives": 5,
    "musicFile": "music.mp3",
    "musicTime": 209.867,
    "iconFile": "icon.png",
    "environmentType": -1,
    "unlockConditions": [],
    "hidden": False,
    "checkpoints": [],
}
ObjVector = tuple[float, float, float]
ObjBool = tuple[bool, bool, bool]
ObjStr = tuple[str, str, str]
ObjTransform = tuple[ObjVector, ObjVector, ObjVector]
ObjTransformStr = tuple[ObjStr, ObjStr, ObjStr]
ObjData = tuple[int, tuple[ObjBool, ObjBool, ObjBool], Object]


def to_str(func: str, value: tuple[str, str, str], name: str):
    txt = ','.join(value)
    return func, f'{name},{txt}'


def xyz_to_xzy(value) -> ObjVector:
    return value[0], value[2], value[1]


def invers_convert(value):
    value = value[0], value[2], value[1]
    return tuple(-1 if d else 1 for d in value)


def calc_time(frame: float) -> float:
    settings = bpy.context.scene.bt_settings
    fps = settings.fps
    offset = settings.offset
    accuracy = settings.accuracy

    t = frame / fps + offset
    t = round(t, accuracy)
    return t


def get_position(objects: list[Object], end: int) -> tuple[list[ObjTransform], list[ObjData]]:
    arr: list[ObjTransform] = []
    times: ObjData = []
    for frame in range(0, end):
        bpy.context.scene.frame_set(frame)
        for obj in objects:
            loc: ObjVector = obj.location
            rot: ObjVector = obj.rotation_euler
            scale: ObjVector = obj.scale

            vecs = loc, rot, scale
            vecs: ObjTransform = tuple(xyz_to_xzy(i) for i in vecs)
            sums = tuple(sum(i) for i in vecs)

            times.append((frame, sums, obj))

            arr.append(vecs)

    arr = numpy.array(arr)

    return arr, times


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


class BT_OT_bake_text(bpy.types.Operator):
    bl_label: str = 'BakeText'
    bl_idname: str = 'bt.bake_text'
    fps: bpy.props.FloatProperty(default=10.0)
    offset: bpy.props.FloatProperty(default=1.0)

    def execute(self, context: bpy.types.Context):
        scene = context.scene
        end = scene.frame_end
        settings = context.scene.bt_settings

        objects: list[bpy.types.Object] = context.selected_objects

        arr, times = get_position(objects, end)
        arr = apply_transforms(arr)

        result = []
        add = []

        prev_sums = None
        for index, arr in enumerate(arr):
            frame, sums, obj = times[index]
            t = calc_time(frame)
            name = obj.name
            render_type: str = obj.bt_settings.render_type
            image: str = obj.bt_settings.image
            s = False, False, False

            if prev_sums:
                s = tuple(numpy.equal(sums, prev_sums))

            fs = zip(arr, ('SetPosition', 'SetRotation', 'SetScale'), s)

            if name not in add:
                add.append(name)
                if render_type == OBJECT_RENDER_TYPE.SUN:
                    result.append({
                        'time': t,
                        'data': ('AddEnvironmentObject', f'0,{name}')
                    })
                elif render_type == OBJECT_RENDER_TYPE.SPRITE:
                    result.append({
                        'time': t,
                        'data': ('AddEnvironmentSprite', f'{image},{name},0,#FFFFFFFF')
                    })

            for vec, text, s in fs:
                if s:
                    continue
                result.append({
                    'time': t,
                    'data': to_str(text, vec, name)
                })

            prev_sums = sums

        config = CONFIG.copy()
        config['events'] = result
        config['name'] = settings.project_name

        config['levelResources'] = [
            {
                'name': i.name,
                'path': ProjectFolders.images.relative_path(i.name),
                'type': 'Sprite',
                'Compress': False
            }
            for i in scene.bt_images]

        # bpy.context.window_manager.clipboard = json.dumps(config)

        with open(ProjectFolders.root.get_file('config.txt'), mode='w') as f:
            f.write(json.dumps(config))
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory((
    BT_OT_bake_text,
))
