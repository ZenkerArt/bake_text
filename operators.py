import json

import bpy
from bpy.types import Object
from .btio import ProjectFolders
from .export.bake_object import bake_object

CONFIG = {
    "configVersion": 3,
    "name": "editor.Test1",
    "info": "Description",
    "levelResources": [],
    "tags": [
        "OneHand"
    ],
    "handCount": 1,
    "moreInfoURL": "",
    "speed": 15.0,
    "lives": 5,
    "maxLives": 5,
    "musicFile": "music.ogg",
    "musicTime": 209.867,
    "iconFile": "icon.png",
    "environmentType": -1,
    "unlockConditions": [],
    "hidden": False,
    "checkpoints": [],
}


class BT_OT_bake_text(bpy.types.Operator):
    bl_label: str = 'BakeText'
    bl_idname: str = 'bt.bake_text'
    fps: bpy.props.FloatProperty(default=10.0)
    offset: bpy.props.FloatProperty(default=1.0)

    def execute(self, context: bpy.types.Context):
        scene = context.scene
        settings = context.scene.bt_settings

        objects: list[bpy.types.Object] = context.selected_objects

        config = CONFIG.copy()
        config['events'] = bake_object(objects)
        config['name'] = settings.project_name

        config['levelResources'] = [
            {
                'name': i.name,
                'path': ProjectFolders.images.relative_path(i.name),
                'type': 'Sprite',
                'Compress': False
            }
            for i in scene.bt_images]

        with open(ProjectFolders.root.get_file('config.txt'), mode='w') as f:
            f.write(json.dumps(config))
        return {'FINISHED'}


class BT_OT_empty(bpy.types.Operator):
    bl_label: str = 'Create Empty'
    bl_idname: str = 'bt.empty'
    fps: bpy.props.FloatProperty(default=10.0)
    offset: bpy.props.FloatProperty(default=1.0)

    def execute(self, context: bpy.types.Context):
        obj: Object = context.active_object
        mesh: bpy.types.Mesh = obj.data

        for vert in mesh.vertices:
            empty = bpy.data.objects.new(obj.name, None)

            empty.location = obj.matrix_world @ vert.co
            empty.scale = (.1,) * 3
            obj.users_collection[0].objects.link(empty)
            empty.select_set(True)

        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory((
    BT_OT_bake_text,
    BT_OT_empty
))
