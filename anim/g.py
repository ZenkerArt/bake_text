import bpy
from ..openui.timeline import Timeline


class Global:
    timeline: Timeline = None
    switch = False

    render = None

    @classmethod
    def draw(cls):
        cls.timeline.render()

    @classmethod
    def unregister(cls):
        if cls.render:
            bpy.types.SpaceView3D.draw_handler_remove(cls.render, 'WINDOW')
            cls.render = None

    @classmethod
    def register(cls):
        if cls.timeline is None:
            cls.timeline = Timeline()

        if cls.render is None:
            cls.render = bpy.types.SpaceView3D.draw_handler_add(
                cls.draw, (), 'WINDOW', 'POST_PIXEL')
        else:
            cls.unregister()

    @classmethod
    def restart(cls):
        cls.unregister()
        cls.timeline = Timeline()
        cls.register()