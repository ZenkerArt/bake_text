import math

import numpy

import bpy
from bpy.types import Object
from .utils import apply_transforms, calc_time, ObjTransform, ObjData, ObjVector, xyz_to_xzy
from ..enums import OBJECT_RENDER_TYPE


def to_str(func: str, value: tuple[str, str, str], name: str):
    txt = ','.join(value)
    return func, f'{name},{txt}'


def get_position(objects: list[Object], end: int) -> tuple[list[ObjTransform], list[ObjData]]:
    arr: list[ObjTransform] = []
    times: ObjData = []
    for frame in range(0, end):
        bpy.context.scene.frame_set(frame)
        for obj in objects:
            loc: ObjVector = obj.location
            rot: ObjVector = tuple(math.degrees(i) for i in obj.rotation_euler)
            scale: ObjVector = obj.scale

            vecs = loc, rot, scale
            vecs: ObjTransform = tuple(xyz_to_xzy(i) for i in vecs)
            sums = tuple(sum(i) for i in vecs)

            times.append((frame, sums, obj))

            arr.append(vecs)

    arr = numpy.array(arr)

    return arr, times


def bake_object(objects: list[Object]) -> dict:
    context = bpy.context
    scene = context.scene
    end = scene.frame_end

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

    return result