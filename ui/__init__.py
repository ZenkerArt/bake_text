import bpy
from .base_ui import BasePanel, SceneSettings
from .calc import BT_PT_text_glob_div, BT_PT_invers
from .object_settings import BT_PT_object_settings
from .scene_settings import BT_PT_scene_settings


class BT_PT_particle(BasePanel, bpy.types.Panel):
    bl_label = 'Частицы'

    @classmethod
    def poll(cls, context: bpy.types.Context):
        objects: list[bpy.types.Object] = context.selected_objects
        p = super().poll(context)

        for obj in objects:
            ps = obj.particle_systems
            if ps:
                return True and p

        return False and p

    @staticmethod
    def draw_particle_system(layout: bpy.types.UILayout, particle_system: bpy.types.ParticleSystem):
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
        p = super().poll(context)

        for obj in objects:
            childres: list[bpy.types.Object] = obj.children

            if childres:
                return True and p
        return False and p

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
    BT_PT_scene_settings,
    BT_PT_invers,
    BT_PT_particle,
    BT_PT_text_glob_div,
    BT_PT_parents,
    BT_PT_object_settings
))
