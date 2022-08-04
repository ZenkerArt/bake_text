import bpy
from ..enums import OBJECT_RENDER_TYPE
from .base_ui import BasePanel


class BT_PT_object_settings(BasePanel, bpy.types.Panel):
    bl_label: str = 'Настройки Объекта'

    def draw(self, context: bpy.types.Context):
        obj: bpy.types.Object = context.active_object
        settings = getattr(obj, 'bt_settings', None)
        layout = self.layout

        if settings is None:
            layout.label(text='Объект не выбран')
            return

        layout.label(text='Тип Запечьки')
        layout.prop(settings, 'bake_type', text='')
