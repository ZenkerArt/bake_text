import bpy
from .timeline_states import TIMELINE_STATE, TimelineState
from ..openui.timeline import TimelineMove
from .g import Global
from .operators import BT_OT_timeline_action, BT_OT_timeline
from ..ui import BasePanel


class BT_PT_timeline(bpy.types.Panel, BasePanel):
    bl_label: str = 'Timeline'

    def draw(self, context: bpy.types.Context):
        if Global.render is None:
            self.layout.operator(BT_OT_timeline.bl_idname,
                                 text='Показать таймлайн')
            return
        else:
            self.layout.operator(BT_OT_timeline.bl_idname,
                                 text='Скрыть таймлайн')

        text = {
            TIMELINE_STATE.OBJECT: 'Сейчас Локальный Таймлайн',
            TIMELINE_STATE.GLOBAL: 'Сейчас Глобальный Таймлайн'
        }

        o = self.layout.operator(BT_OT_timeline_action.bl_idname,
                                 text=text[TimelineState.state()])
        o.action = 'SWITCH'

        o = self.layout.operator(
            BT_OT_timeline_action.bl_idname, text='Удалить все ключи')
        o.action = 'CLEAR'

        try:
            t = Global.timeline.ext.get_ext(TimelineMove)
            if t.active_keyframe:
                self.layout.prop(t.active_keyframe.keyframe, 'event', text='')
        except AttributeError:
            pass


register, unregister = bpy.utils.register_classes_factory((
    BT_PT_timeline,
))
