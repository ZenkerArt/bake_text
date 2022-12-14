import bpy
from . import BasePanel
from ..operators import BT_OT_bake_text


class BT_PT_scene_settings(BasePanel, bpy.types.Panel):
    bl_label = 'Настройки'

    def draw(self, context: bpy.types.Context):
        settings = context.scene.bt_settings

        layout = self.layout
        layout.label(text='Папка проекта')
        layout.prop(settings, 'project_folder', text='')
        layout.label(text='Камера')
        layout.prop(settings, 'camera', text='')
        layout.prop(settings, 'camera_expression', text='')

        if settings.project_folder.strip() == '':
            return

        layout.label(text='Название проекта')
        layout.prop(settings, 'project_name', text='')

        sub = layout.column(align=True)
        sub.prop(settings, 'fps', text='ФПС')
        sub.prop(settings, 'offset', text='Отступ')
        sub.prop(settings, 'accuracy',
                 text='Точность после запятой', slider=True)

        layout.operator(BT_OT_bake_text.bl_idname, text='Сохранить')

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True
