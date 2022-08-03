from enum import Enum

import bpy


class EVENTS:
    @classmethod
    def enum(cls):
        arr = []
        for key, value in cls.__dict__.items():
            if key.startswith('_') or not isinstance(value, str):
                continue
            arr.append((key, value, ''))

        return tuple(arr)


class EVENTS_GLOBAL(EVENTS):
    CLEAR_OBJECTS: str = 'ClearEnvironment'
    SET_PLAYER_DIST: str = 'SetPlayerDistance'


class EVENTS_LOCAL(EVENTS):
    AddEnvironmentObject: str = 'AddEnvironmentObject'
    AddEnvironmentSprite: str = 'AddEnvironmentSprite'
    SetEnvSpriteImage: str = 'SetEnvSpriteImage'

    SetSunSensitivity: str = 'SetSunSensitivity'
    RemoveEnvironmentObject: str = 'RemoveEnvironmentObject'


class OBJECT_TYPE:
    PARTICLE_SYS = 'PARTICLE_SYS'
    PARENT = 'PARENT'
    OBJECT = 'OBJECT'

    @classmethod
    def get_type(cls, obj: bpy.types.Object) -> str:
        if obj.particle_systems:
            return cls.PARTICLE_SYS

        if obj.children:
            return cls.PARENT

        return cls.OBJECT


OBJECT_RENDER_TYPE_TRANS = {'SATELLITE': 'Сателлит', 'SUN': 'Солнце', 'SPRITE': 'Картинка'}


class OBJECT_RENDER_TYPE:
    SUN = 'SUN'
    SATELLITE = 'SATELLITE'
    SPRITE = 'SPRITE'

    @classmethod
    def enum(cls):
        arr = []
        for key, value in cls.__dict__.items():
            if key.startswith('_') or not isinstance(value, str):
                continue
            arr.append((value, OBJECT_RENDER_TYPE_TRANS[value], ''))

        return arr


class OBJECT_BAKE_TYPE:
    BAKE_LOCATION = 'BAKE_LOCATION'
    BAKE_VERTEX = 'BAKE_VERTEX'
