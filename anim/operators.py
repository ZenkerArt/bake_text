import bpy
from ..openui.timeline import TimelineMove, TimelineActiveObj
from .g import Global
from .properties import TIMELINE_STATE


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


class BT_OT_timeline_add_keyframe(bpy.types.Operator):
    bl_label: str = 'Add Keyframe'
    bl_idname: str = 'bt.add_keyframe'

    action: bpy.props.StringProperty()
    event: bpy.props.StringProperty()

    def execute(self, context: bpy.types.Context):
        timeline = Global.timeline
        store = context.scene.bt_store_timeline
        local_keyframes = context.active_object.bt_keyframes
        global_keyframes = store.keyframes()

        if store.state == TIMELINE_STATE.LOCAL:
            keyframes = local_keyframes
        elif store.state == TIMELINE_STATE.GLOBAL:
            keyframes = global_keyframes

        timeline_move = timeline.ext.get_ext(TimelineMove)
        timeline_active_obj = timeline.ext.get_ext(TimelineActiveObj)

        k = timeline_move.settings_keyframe
        if self.action == 'ADD_MOUSE':
            timeline.add_keyframe(timeline_move.mouse,
                                  None or self.event, keyframes=keyframes)

        if self.action == 'REMOVE_MOUSE' and k:
            for index, key in enumerate(keyframes):
                if k.keyframe.name == key.name:
                    keyframes.remove(index)
                    timeline_active_obj.update(context, keyframes)

        if self.action == 'SWITCH':
            Global.switch = not Global.switch
            store.state = TIMELINE_STATE.GLOBAL if Global.switch else TIMELINE_STATE.LOCAL

            if store.state == TIMELINE_STATE.GLOBAL:
                timeline_active_obj.update(context, global_keyframes)
            elif store.state == TIMELINE_STATE.LOCAL:
                timeline_active_obj.update(context, local_keyframes)

        if self.action == 'CLEAR':
            timeline.keyframes = {}
            keyframes.clear()
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory((
    BT_OT_timeline,
    BT_OT_timeline_add_keyframe
))
