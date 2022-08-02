from time import time

import bpy
from bpy.props import FloatProperty


def update(self, context):
    pass


class ProgressBar(bpy.types.PropertyGroup):
    _timer = 0

    progress: FloatProperty(
        default=0,
        subtype='PERCENTAGE',
        precision=1,
        min=0,
        soft_min=0,
        soft_max=100,
        max=101,
        update=update
    )

    @classmethod
    def update(cls, value: float):
        cls.data().progress = value * 100

    @classmethod
    def timer(cls, value: float):
        delay = .2
        if cls._timer < time():
            cls._timer = time() + delay
            cls.update(value * 100)

    @staticmethod
    def data():
        return bpy.context.scene.bt_progress

    @classmethod
    def register(cls):
        bpy.types.Scene.bt_progress = bpy.props.PointerProperty(type=cls)
