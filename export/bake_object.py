import math

import numpy

import bpy
from bpy.types import Object, Mesh
from .utils import apply_transforms, calc_time, ObjTransform, ObjData, ObjVector, xyz_to_xzy
from ..enums import OBJECT_RENDER_TYPE, OBJECT_BAKE_TYPE


def to_str(func: str, value: tuple[str, str, str], name: str):
    txt = ','.join(value)
    return func, f'{name},{txt}'


def save_obj(obj: Object, frame, arr, times, dg=None):
    loc: ObjVector = obj.location
    rot: ObjVector = tuple(math.degrees(i) for i in obj.rotation_euler)
    scale: ObjVector = obj.scale

    vecs = loc, rot, scale
    vecs: ObjTransform = tuple(xyz_to_xzy(i) for i in vecs)
    sums = tuple(sum(i) for i in vecs)

    times.append((frame, sums, obj, obj.name))
    arr.append(vecs)


def save_vertex(obj: Object, frame, arr, times, dg=None):
    obj: Object = obj.evaluated_get(dg)
    mesh: Mesh = obj.data

    for index, i in enumerate(mesh.vertices):
        loc: ObjVector = obj.matrix_world @ i.co
        rot: ObjVector = 0, 0, 0
        scale: ObjVector = obj.matrix_world @ obj.scale

        vecs = loc, rot, scale
        vecs: ObjTransform = tuple(xyz_to_xzy(i) for i in vecs)
        sums = tuple(sum(i) for i in vecs)

        times.append((frame, sums, obj, f'{obj.name}_{index}'))

        arr.append(vecs)


def get_position(objects: list[Object], end: int) -> tuple[list[ObjTransform], list[ObjData]]:
    arr: list[ObjTransform] = []
    times: ObjData = []
    dg = bpy.context.evaluated_depsgraph_get()

    for frame in range(0, end):
        bpy.context.scene.frame_set(frame)

        for obj in objects:
            if obj.bt_settings.bake_type == OBJECT_BAKE_TYPE.BAKE_LOCATION:
                save_obj(obj, frame, arr, times, dg)
            else:
                save_vertex(obj, frame, arr, times, dg)

    arr = numpy.array(arr)

    return arr, times


def bake_object(objects: list[Object], func=get_position) -> dict:
    context = bpy.context
    scene = context.scene
    end = scene.frame_end

    arr, times = func(objects, end)
    arr = apply_transforms(arr)

    result = []
    add = []

    prev_sums = None
    for index, arr in enumerate(arr):
        frame, sums, obj, name = times[index]
        t = calc_time(frame)
        settings = obj.bt_settings
        render_type: str = settings.render_type
        image: str = settings.image
        sun_sensitivity = settings.sun_sensitivity
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
                result.append({
                    'time': t,
                    'data': ('SetSunSensitivity', f'{name},{sun_sensitivity}')
                })
            elif render_type == OBJECT_RENDER_TYPE.SATELLITE:
                result.append({
                    'time': t,
                    'data': ('AddEnvironmentObject', f'1,{name}')
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
