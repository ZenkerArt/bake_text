import bpy
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

        layout.label(text='Копировать с')
        layout.prop(settings, 'copy_from', text='')
        layout.prop(settings, 'copy_mode', text='Режим наложение', expand=True)

        if settings.copy_from:
            settings = settings.copy_from.bt_settings

        layout.label(text='Тип Запечьки')
        layout.prop(settings, 'bake_type', text='')

        if obj.particle_systems:
            layout.label(text='Ротация всех частиц')
            layout.prop(settings, 'particle_rotation', text='')
