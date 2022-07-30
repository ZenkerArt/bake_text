from calendar import c
import bpy
from .operators import BT_OT_bake_text, BT_OT_invers


class BasePanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BT'
    bl_context = 'objectmode'


class Settings(BasePanel):
    bl_parent_id = 'BT_PT_settings'


class ObjectInfo(BasePanel):
    bl_parent_id = 'BT_PT_object_info'


class BT_PT_settings(BasePanel, bpy.types.Panel):
    bl_label = 'Настройки'

    def draw(self, context: bpy.types.Context):
        settings = context.scene.bake_text_settings
        save_type: str = settings.save_type

        layout = self.layout
        layout.prop(settings, 'save_type', text='')

        if save_type == 'file':
            layout.prop(settings, 'path', text='')

        sub = layout.column(align=True)
        sub.prop(settings, 'fps', text='ФПС')
        sub.prop(settings, 'offset', text='Отступ')
        sub.prop(settings, 'accuracy',
                 text='Точность после запятой', slider=True)

        layout.operator(BT_OT_bake_text.bl_idname, text='Сохранить')


class BT_PT_invers(Settings, bpy.types.Panel):
    bl_label = "Инверсия"

    def draw(self, context: bpy.types.Context):
        scene = context.scene
        layout = self.layout
        vec_names = ['position', 'rotation', 'scale']
        vec_namess = {'position': 'Позиция',
                      'rotation': 'Поворот', 'scale': 'Размер'}
        v = scene.bake_text_invers

        for vec_name in vec_names:
            layout.label(text=f'Инверсия {vec_namess[vec_name].lower()}')
            layout.prop(v, vec_name, text='')


class BT_PT_text_glob_div(Settings, bpy.types.Panel):
    bl_label = "Глобальное деление"

    def draw(self, context: bpy.types.Context):
        settings = context.scene.bake_text_settings
        layout = self.layout

        layout.label(text='Глоб. деление')
        layout.prop(settings, 'global_div', text='')

        box = layout.column(align=True)

        box.prop(settings, 'global_location',
                 text='Позиция')
        box.prop(settings, 'global_rotation',
                 text='Поворот')
        box.prop(settings, 'global_scale', text='Размер')


class BT_PT_particle(BasePanel, bpy.types.Panel):
    bl_label = 'Частицы'

    @classmethod
    def poll(cls, context: bpy.types.Context):
        objects: list[bpy.types.Object] = context.selected_objects

        for obj in objects:
            ps = obj.particle_systems
            if ps:
                return True

        return False

    def draw_particle_system(self, layout: bpy.types.UILayout, particle_system: bpy.types.ParticleSystem):
        settings = particle_system.settings

        layout.prop(settings, 'name', icon='PARTICLES', text='')

        s = layout.column(align=True)
        s.prop(settings, 'size_random')
        s.prop(settings, 'particle_size')

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        objects: list[bpy.types.Object] = context.selected_objects
        is_duplicate = False
        systems = []

        for obj in objects:
            ps = obj.particle_systems
            if not ps:
                continue

            p_sys = ps.active
            is_duplicate = any(p_sys.settings.name ==
                               i.settings.name for i in systems)
            systems.append(p_sys)
            l = layout.box()
            self.draw_particle_system(l, particle_system=p_sys)

        if is_duplicate:
            layout.label(
                text='Обнаружены дубликаты систем частиц', icon='ERROR')


class BT_PT_parents(BasePanel, bpy.types.Panel):
    bl_label: str = 'Паренты'

    @classmethod
    def poll(cls, context: bpy.types.Context):
        objects: list[bpy.types.Object] = context.selected_objects

        for obj in objects:
            childres: list[bpy.types.Object] = obj.children

            if childres:
                return True
        return False

    def draw(self, context: bpy.types.Context):
        objects: list[bpy.types.Object] = context.selected_objects
        layout = self.layout

        for obj in objects:
            childres: list[bpy.types.Object] = obj.children

            if not childres:
                continue

            box = layout.box()
            box.prop(obj, 'name', text='', icon='MESH_CUBE')
            box.label(text=f'Кол. объектов: {len(childres)}')


register, unregister = bpy.utils.register_classes_factory((
    BT_PT_settings,
    BT_PT_invers,
    BT_PT_particle,
    BT_PT_text_glob_div,
    BT_PT_parents,
))
