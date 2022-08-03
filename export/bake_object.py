import math

import numpy

import bpy
from bpy.types import Object, Mesh, Particle
from mathutils import Vector
from .utils import apply_transforms, calc_time, ObjTransform, ObjVector, xyz_to_xzy
from ..enums import OBJECT_RENDER_TYPE, OBJECT_BAKE_TYPE, EVENTS_LOCAL


def to_str(func: str, value: tuple[str, str, str], name: str):
    txt = ','.join(value)
    return func, f'{name},{txt}'


def obj_params(obj: Object, frame: int, sums: list, name: str, alive_state=None):
    return frame, sums, obj, name, alive_state


def calc_sums(loc: ObjVector, rot: ObjVector, scale: ObjVector):
    vecs = loc, rot, scale
    vecs: ObjTransform = tuple(xyz_to_xzy(i) for i in vecs)
    sums = tuple(sum(i) for i in vecs)

    return sums, vecs


def save_obj(obj: Object, frame, arr, times, dg=None):
    loc: ObjVector = obj.location
    rot: ObjVector = tuple(math.degrees(i) for i in obj.rotation_euler)
    scale: ObjVector = obj.scale

    sums, vecs = calc_sums(loc, rot, scale)

    params = obj_params(obj, frame, sums, obj.name)
    times.append(params)
    arr.append(vecs)


def save_vertex(obj: Object, frame, arr, times, dg=None):
    ev_obj: Object = obj.evaluated_get(dg)
    mesh: Mesh = ev_obj.data

    for index, i in enumerate(mesh.vertices):
        loc: ObjVector = ev_obj.matrix_world @ i.co
        rot: ObjVector = 0, 0, 0
        scale: ObjVector = ev_obj.matrix_world @ ev_obj.scale

        sums, vecs = calc_sums(loc, rot, scale)

        params = obj_params(obj, frame, sums, f'{ev_obj.name}_{index}')
        times.append(params)

        arr.append(vecs)


def save_particle(obj: Object, frame, arr, times, dg=None):
    ev_obj: Object = obj.evaluated_get(dg)
    ps = ev_obj.particle_systems[0]

    for index, i in enumerate(ps.particles):
        i: Particle
        loc: ObjVector = ev_obj.matrix_world @ i.location
        rot: ObjVector = tuple(math.degrees(r) for r in i.rotation)
        scale: ObjVector = ev_obj.matrix_world @ Vector((i.size,) * 3)

        sums, vecs = calc_sums(loc, rot, scale)

        params = obj_params(obj, frame, sums, f'{ev_obj.name}_{index}', alive_state=i.alive_state)
        times.append(params)

        arr.append(vecs)


def get_position(objects: list[Object], end: int) -> tuple[list[ObjTransform], list]:
    arr: list[ObjTransform] = []
    times = []
    dg = bpy.context.evaluated_depsgraph_get()

    for frame in range(0, end):
        bpy.context.scene.frame_set(frame)

        for obj in objects:
            if obj.particle_systems:
                func = save_particle
            elif obj.bt_settings.bake_type == OBJECT_BAKE_TYPE.BAKE_LOCATION:
                func = save_obj
            else:
                func = save_vertex

            func(obj, frame, arr, times, dg)

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
    test = {}
    skip = True
    for index, arr in enumerate(arr):
        frame, sums, obj, name, alive_state = times[index]
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
            test = {}
            add.append(name)

            for keyframe in obj.bt_keyframes.values():
                event = keyframe.event

                if event == EVENTS_LOCAL.AddEnvironmentObject:
                    e_start = calc_time(keyframe.index)
                    result.append({
                        'time': e_start,
                        'data': (event, f'0,{name}')
                    })
                    test[keyframe.index] = False

                if event == EVENTS_LOCAL.RemoveEnvironmentObject:
                    e_end = calc_time(keyframe.index)
                    result.append({
                        'time': e_end,
                        'data': (event, f'{name}')
                    })
                    test[keyframe.index] = True
            #     result.append({
            #         'time': t,
            #         'data': ('SetSunSensitivity', f'{name},{sun_sensitivity}')
            #     })
            # elif render_type == OBJECT_RENDER_TYPE.SPRITE:
            #     result.append({
            #         'time': t,
            #         'data': ('AddEnvironmentSprite', f'{image},{name},0,#FFFFFFFF')
            #     })
        #

        d = test.get(frame)
        if d is not None:
            skip = d

        if skip:
            continue

        for vec, text, s in fs:
            if s:
                continue
            result.append({
                'time': t,
                'data': to_str(text, vec, name)
            })

        prev_sums = sums

    return result
