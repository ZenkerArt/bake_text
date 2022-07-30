from ..ui import BasePanel
from . import properties, timeline
import bpy


class BT_PT_animation(BasePanel, bpy.types.Panel):
    bl_label: str = 'Настройки Объекта'

    def draw(self, context: bpy.types.Context):
        object: bpy.types.Object = context.active_object
        info = getattr(object, 'bt_settings', None)
        layout = self.layout

        if info is None:
            layout.label(text='Объект не выбран')
            return
        layout.label(text='Тип Запечьки')
        layout.prop(info, 'bake_type', text='')
        layout.label(text='ID')
        layout.prop(info, 'id', text='')


reg, unreg = bpy.utils.register_classes_factory((
    BT_PT_animation,
))

modules = (
    properties,
    timeline
)


def register():
    for i in modules:
        i.register()
    reg()


def unregister():
    for i in modules:
        i.unregister()
    unreg()
