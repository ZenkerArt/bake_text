from enum import Enum, auto

import bpy
from ..enums import COPY_MODE


class TIMELINE_STATE(Enum):
    GLOBAL = auto()
    OBJECT = auto()


class TIMELINE_UNIT(Enum):
    FRAME = auto()
    TIME = auto()


class TimelineState:
    @staticmethod
    def store():
        return bpy.context.scene.bt_store_timeline

    @classmethod
    def state(cls) -> TIMELINE_STATE:
        store = cls.store()
        return TIMELINE_STATE(store.state)

    @classmethod
    def set_state(cls, state: TIMELINE_STATE):
        cls.store().state = state.value

    @classmethod
    def active_keyframes(cls):
        store = cls.store()
        state = TIMELINE_STATE(store.state)
        obj = bpy.context.active_object

        if state == TIMELINE_STATE.OBJECT:
            copy_from = obj.bt_settings.copy_from

            if copy_from and obj.bt_settings.copy_mode == COPY_MODE.REPLACE:
                return copy_from.bt_keyframes

            return obj.bt_keyframes

        elif state == TIMELINE_STATE.GLOBAL:
            return store.keyframes()
