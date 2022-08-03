import bpy
from ..openui.timeline.ext import TimelineMove
from ..openui.timeline import Timeline
from ..ui import BasePanel

timeline: Timeline = None


def draw():
    timeline.render()


class BT_OT_timeline_add_keyframe(bpy.types.Operator):
    bl_label: str = 'Add Keyframe'
    bl_idname: str = 'bt.add_keyframe'

    action: bpy.props.StringProperty()

    def execute(self, context: bpy.types.Context):
        if self.action == 'ADD':
            timeline.add_keyframe(context.scene.frame_current)

        if self.action == 'REMOVE':

            for index, key in enumerate(context.active_object.bt_keyframes.keys()):
                k = timeline.ext.get_ext(TimelineMove).active_keyframe.keyframe
                if k.name == key:
                    context.active_object.bt_keyframes.remove(index)
                    del timeline.keyframes[key]

        if self.action == 'CLEAR':
            timeline.keyframes = {}
            context.active_object.bt_keyframes.clear()
        return {'FINISHED'}


class BT_OT_timeline(bpy.types.Operator):
    bl_label: str = 'Timeline'
    bl_idname: str = 'bt.timeline'
    render = None
    click = False
    offset = 0

    @classmethod
    def destroy(cls):
        if cls.render:
            bpy.types.SpaceView3D.draw_handler_remove(cls.render, 'WINDOW')
            cls.render = None

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):
        if context.area:
            context.area.tag_redraw()

        v = timeline.event(context, event)
        if v:
            return v

        if self.render is None:
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        global timeline
        if timeline is None:
            timeline = Timeline()
        context.window_manager.modal_handler_add(self)
        if BT_OT_timeline.render is None:
            BT_OT_timeline.render = bpy.types.SpaceView3D.draw_handler_add(
                draw, (), 'WINDOW', 'POST_PIXEL')
        else:
            self.destroy()
        return {'RUNNING_MODAL'}


class BT_PT_timeline(bpy.types.Panel, BasePanel):
    bl_label: str = 'Timeline'

    def draw(self, context: bpy.types.Context):
        if BT_OT_timeline.render is None:
            self.layout.operator(BT_OT_timeline.bl_idname,
                                 text='Показать таймлайн')
            return
        else:
            self.layout.operator(BT_OT_timeline.bl_idname,
                                 text='Скрыть таймлайн')

        # event = context.scene.bt_event

        o = self.layout.operator(BT_OT_timeline_add_keyframe.bl_idname)
        o.action = 'ADD'

        o = self.layout.operator(BT_OT_timeline_add_keyframe.bl_idname, text='Remove')
        o.action = 'REMOVE'

        o = self.layout.operator(BT_OT_timeline_add_keyframe.bl_idname, text='Clear')
        o.action = 'CLEAR'

        try:
            t = timeline.ext.get_ext(TimelineMove)
            if t.active_keyframe:
                self.layout.prop(t.active_keyframe.keyframe, 'event', text='')
        except AttributeError:
            pass


reg, unreg = bpy.utils.register_classes_factory((
    BT_OT_timeline,
    BT_PT_timeline,
    BT_OT_timeline_add_keyframe,
))


def register():
    reg()


def unregister():
    unreg()
    BT_OT_timeline.destroy()
