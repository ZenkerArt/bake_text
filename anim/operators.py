import bpy
from .g import Global
from .timeline_states import TimelineState, TIMELINE_STATE


class BT_OT_timeline(bpy.types.Operator):
    bl_label: str = 'Timeline'
    bl_idname: str = 'bt.timeline'

    @classmethod
    def destroy(cls):
        Global.unregister()

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):
        if context.area:
            context.area.tag_redraw()

        v = Global.timeline.event(context, event)
        if v:
            return v

        if Global.render is None:
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        Global.register()
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class BT_OT_timeline_action(bpy.types.Operator):
    bl_label: str = 'Timeline Action'
    bl_idname: str = 'bt.timeline_action'

    action: bpy.props.StringProperty()
    event: bpy.props.StringProperty()

    def execute(self, context: bpy.types.Context):
        timeline = Global.timeline
        mouse = timeline.keyframe.mouse_pos

        keyframes = TimelineState.active_keyframes()
        context_keyframe = timeline.keyframe.context_keyframe

        if self.action == 'ADD_MOUSE':
            timeline.add_keyframe(mouse, self.event, keyframes)

        if self.action == 'REMOVE_MOUSE' and context_keyframe:
            for index, key in enumerate(keyframes):
                if context_keyframe.name == key.name:
                    keyframes.remove(index)
                    timeline.keyframe.update(keyframes)

        if self.action == 'SWITCH':
            Global.switch = not Global.switch
            TimelineState.set_state(TIMELINE_STATE.GLOBAL if Global.switch else TIMELINE_STATE.OBJECT)
            timeline.keyframe.update(TimelineState.active_keyframes())

        if self.action == 'CLEAR':
            timeline.keyframe.keyframes = {}
            keyframes.clear()
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory((
    BT_OT_timeline,
    BT_OT_timeline_action
))
