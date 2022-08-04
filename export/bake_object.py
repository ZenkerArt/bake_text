import numpy

import bpy
from bpy.types import Object
from .export_methods import save_obj, save_vertex, save_particle
from .utils import apply_transforms, calc_time, ObjTransform
from ..enums import OBJECT_BAKE_TYPE, EVENTS_LOCAL


def to_str(func: str, value: tuple[str, str, str], name: str):
    txt = ','.join(value)
    return func, f'{name},{txt}'


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


class EventToString:
    @staticmethod
    def add_vecs(result, fs, t, name):
        for vec, text, s in fs:
            if s:
                continue
            result.append({
                'time': t,
                'data': to_str(text, vec, name)
            })

    @staticmethod
    def AddEnvironmentObject(keyframe, result, name, skip_event):
        e_start = calc_time(keyframe.index)
        result.append({
            'time': e_start,
            'data': ('AddEnvironmentObject', f'0,{name}')
        })
        skip_event[keyframe.index] = False
        return True

    @staticmethod
    def RemoveEnvironmentObject(keyframe, result, name, skip_event):
        e_end = calc_time(keyframe.index)
        result.append({
            'time': e_end,
            'data': ('RemoveEnvironmentObject', f'{name}')
        })
        skip_event[keyframe.index] = True

    @staticmethod
    def SetSunSensitivity(keyframe, result, name, skip_event=None):
        result.append({
            'time': calc_time(keyframe.index),
            'data': ('SetSunSensitivity', f'{name},{keyframe.sun_sensitivity}')
        })

    @staticmethod
    def AddEnvironmentSprite(keyframe, result, name, skip_event=None):
        color = numpy.array(keyframe.color) * 255
        color = color.astype(int)
        color = '#%02x%02x%02xff' % tuple(color)
        result.append({
            'time': calc_time(keyframe.index),
            'data': ('AddEnvironmentSprite', f'{keyframe.image},{name},{keyframe.sun_sensitivity},{color.upper()}')
        })
        skip_event[keyframe.index] = False
        return True

    @staticmethod
    def SetEnvSpriteImage(keyframe, result, name, skip_event=None):
        result.append({
            'time': calc_time(keyframe.index),
            'data': ('SetEnvSpriteImage', f'{name},{keyframe.image}')
        })


def bake_object(objects: list[Object]) -> dict:
    context = bpy.context
    scene = context.scene
    end = scene.frame_end

    arr, times = get_position(objects, end)
    arr = apply_transforms(arr)

    result = []
    add = []

    prev_sums = None
    skip_event = {}
    skip = True
    last_transforms = None
    for index, arr in enumerate(arr):
        frame, sums, obj, name, alive_state = times[index]
        t = calc_time(frame)

        s = False, False, False

        if prev_sums:
            s = tuple(numpy.equal(sums, prev_sums))

        transforms = tuple(zip(arr, ('SetPosition', 'SetRotation', 'SetScale'), s))

        if name not in add:
            skip_event = {}
            add.append(name)
            for keyframe in obj.bt_keyframes.values():
                event = keyframe.event
                method = getattr(EventToString, event)
                r = method(keyframe, result, name, skip_event)
                tt = transforms or last_transforms
                if r:
                    for vec, text, s in tt:
                        result.append({
                            'time': calc_time(keyframe.index) + .1,
                            'data': to_str(text, vec, name)
                        })

        # skip = skip_event.get(frame) or skip
        d = skip_event.get(frame)
        if d is not None:
            skip = d

        if skip:
            continue

        for vec, text, s in transforms:
            if s:
                continue
            result.append({
                'time': t,
                'data': to_str(text, vec, name)
            })

        prev_sums = sums
        last_transforms = transforms or last_transforms

    return result
