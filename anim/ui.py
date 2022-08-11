import bpy
from .g import Global
from .operators import BT_OT_timeline_action, BT_OT_timeline
from ..ui import BasePanel


class BT_PT_timeline(bpy.types.Panel, BasePanel):
    bl_label: str = 'Timeline'

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        if Global.render is None:
            layout.operator(BT_OT_timeline.bl_idname,
                            text='Показать таймлайн')
            return
        else:
            layout.operator(BT_OT_timeline.bl_idname,
                            text='Скрыть таймлайн')
            o = self.layout.operator(
                BT_OT_timeline_action.bl_idname, text='Перезагрузить таймлаин')
            o.action = 'RESTART'

        o = self.layout.operator(
            BT_OT_timeline_action.bl_idname, text='Удалить все ключи')
        o.action = 'CLEAR'


register, unregister = bpy.utils.register_classes_factory((
    BT_PT_timeline,
))
