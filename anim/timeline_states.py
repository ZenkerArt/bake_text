from enum import Enum, auto

import bpy


class TIMELINE_STATE(Enum):
    GLOBAL = auto()
    OBJECT = auto()


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

        if state == TIMELINE_STATE.OBJECT:
            return bpy.context.active_object.bt_keyframes
        elif state == TIMELINE_STATE.GLOBAL:
            return store.keyframes()
