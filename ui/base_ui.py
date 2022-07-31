import bpy


class BasePanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BT'
    bl_context = 'objectmode'

    @classmethod
    def poll(cls, context: bpy.types.Context):
        settings = context.scene.bt_settings

        return settings.project_folder.strip() != ''


class SceneSettings(BasePanel):
    bl_parent_id = 'BT_PT_scene_settings'


class ObjectSettings(BasePanel):
    bl_parent_id = 'BT_PT_object_settings'
