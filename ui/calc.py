import bpy
from .base_ui import SceneSettings


class BT_PT_invers(SceneSettings, bpy.types.Panel):
    bl_label = "Инверсия"

    def draw(self, context: bpy.types.Context):
        scene = context.scene
        layout = self.layout
        vec_names = ['position', 'rotation', 'scale']
        vec_namess = {'position': 'Позиция',
                      'rotation': 'Поворот', 'scale': 'Размер'}
        v = scene.bt_invers

        for vec_name in vec_names:
            layout.label(text=f'Инверсия {vec_namess[vec_name].lower()}')
            layout.prop(v, vec_name, text='')


class BT_PT_text_glob_div(SceneSettings, bpy.types.Panel):
    bl_label = "Глобальное деление"

    def draw(self, context: bpy.types.Context):
        settings = context.scene.bt_settings
        layout = self.layout

        layout.label(text='Глоб. деление')
        layout.prop(settings, 'global_div', text='')

        box = layout.column(align=True)

        box.prop(settings, 'global_location',
                 text='Позиция')
        box.prop(settings, 'global_rotation',
                 text='Поворот')
        box.prop(settings, 'global_scale', text='Размер')
