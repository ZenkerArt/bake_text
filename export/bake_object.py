import numpy

import bpy
from bpy.types import Object
from .export_methods import save_obj, save_vertex, save_particle
from .utils import apply_transforms, calc_time, ObjTransform
from ..enums import OBJECT_BAKE_TYPE


def to_str(func: str, value: tuple[str, str, str], name: str):
    txt = ','.join(value)
    return func, f'{name},{txt}'


def apply_round(value: float):
    settings = bpy.context.scene.bt_settings
    accuracy = settings.accuracy
    return round(value, accuracy)


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
        sun_sens = apply_round(keyframe.sun_sensitivity)
        result.append({
            'time': calc_time(keyframe.index),
            'data': ('SetSunSensitivity', f'{name},{sun_sens}')
        })

    @staticmethod
    def AddEnvironmentSprite(keyframe, result, name, skip_event=None):
        color = numpy.array(keyframe.color) * 255
        color = color.astype(int)
        color = '#%02x%02x%02xff' % tuple(color)
        sun_sens = apply_round(keyframe.sun_sensitivity)
        result.append({
            'time': calc_time(keyframe.index),
            'data': ('AddEnvironmentSprite', f'{keyframe.image},{name},{sun_sens},{color.upper()}')
        })
        skip_event[keyframe.index] = False
        return True

    @staticmethod
    def SetEnvSpriteImage(keyframe, result, name, skip_event=None):
        result.append({
            'time': calc_time(keyframe.index),
            'data': ('SetEnvSpriteImage', f'{name},{keyframe.image}')
        })

    @staticmethod
    def SetPlayerDistance(keyframe, result):
        result.append({
            'time': calc_time(keyframe.index),
            'data': ('SetPlayerDistance', f'{keyframe.player_dist}')
        })

    @staticmethod
    def ClearEnvironment(keyframe, result):
        result.append({
            'time': calc_time(keyframe.index),
            'data': ('ClearEnvironment', '')
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

    for i in context.scene.bt_keyframes:
        event_func = getattr(EventToString, i.event)
        event_func(i, result)

    for index, arr in enumerate(arr):
        frame, sums, obj, name = times[index]
        t = calc_time(frame)

        sums = False, False, False

        if prev_sums:
            sums = tuple(numpy.equal(sums, prev_sums))

        transforms = tuple(zip(arr, ('SetPosition', 'SetRotation', 'SetScale'), sums))

        if name not in add:
            skip_event = {}
            add.append(name)
            for keyframe in obj.bt_keyframes.values():
                event = keyframe.event
                event_func = getattr(EventToString, event)
                event_result = event_func(keyframe, result, name, skip_event)

                trans = transforms or last_transforms
                if event_result:
                    for vec, text, sums in trans:
                        result.append({
                            'time': calc_time(keyframe.index) + .1,
                            'data': to_str(text, vec, name)
                        })

        d = skip_event.get(frame)
        if d is not None:
            skip = d

        if skip:
            continue

        for vec, text, sums in transforms:
            if sums:
                continue
            result.append({
                'time': t,
                'data': to_str(text, vec, name)
            })

        prev_sums = sums
        last_transforms = transforms or last_transforms

    return result
