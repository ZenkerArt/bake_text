from typing import Optional

import bpy
from bpy.props import StringProperty, CollectionProperty
from bpy.utils.previews import ImagePreviewCollection
from bpy_extras.io_utils import ImportHelper
from bpy_types import Operator, PropertyGroup
from .enums import IMAGE_ACTION
from ..btio import ProjectFolders


def image_enum(self, context):
    scene = context.scene
    arr = []
    for i in scene.bt_images:
        arr.append((
            i.name, i.label, ''
        ))
    return tuple(arr)


def on_image_rename(self, context):
    old_name = self.prev_name
    new_name = self.name
    self.prev_name = new_name
    self.path = ProjectFolders.images.get_file(new_name)

    try:
        ProjectFolders.images.rename_file(old_name, new_name)
    except PermissionError:
        pass
    ImageLoader.load_icons()


class Image(PropertyGroup):
    label: bpy.props.StringProperty()
    name: bpy.props.StringProperty(update=on_image_rename)
    prev_name: bpy.props.StringProperty()
    path: bpy.props.StringProperty()

    @classmethod
    def active(cls):
        scene = bpy.context.scene
        return scene.bt_images[scene.bt_images_action]

    @classmethod
    def active_icon(cls):
        name = cls.active().name
        return ImageLoader.preview_collection[name]


class ImageLoader:
    _is_loaded = False
    preview_collection: Optional[ImagePreviewCollection] = None

    @classmethod
    def init(cls):
        if cls._is_loaded:
            return
        ImageLoader.load_icons()
        cls._is_loaded = True

    @classmethod
    def load_icons(cls):
        preview_collection = cls.preview_collection
        if preview_collection is not None:
            bpy.utils.previews.remove(preview_collection)

        pcoll = bpy.utils.previews.new()
        cls.preview_collection = pcoll

        for image in bpy.context.scene.bt_images.values():
            cls.add_icon(image.name, image.path)

    @classmethod
    def add_icon(cls, name: str, path: str):
        cls.preview_collection.load(name, path, 'IMAGE')

    @classmethod
    def get_icon(cls, name: str):
        return cls.preview_collection[name]


class BT_OT_action_image(Operator, ImportHelper):
    bl_idname = 'bt.load_image'
    bl_label = 'Load image'
    action: bpy.props.EnumProperty(IMAGE_ACTION.enum())

    filter_glob: StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp', options={'HIDDEN'})

    def execute(self, context: bpy.types.Context):
        filepath: str = self.properties.filepath

        file = ProjectFolders.images.save_file(filepath)
        ImageLoader.add_icon(file.name, file.path)

        image = context.scene.bt_images.add()
        image.path = file.path
        image.name = file.name
        image.label = file.name.rsplit('.', 1)[0]
        image.prev_name = file.name
        return {'FINISHED'}


class BT_OT_clear_images(Operator):
    bl_idname = 'bt.clear_images'
    bl_label = 'Clear Images'

    def execute(self, context: bpy.types.Context):
        for image in context.scene.bt_images.values():
            ProjectFolders.images.remove_file(image.name)
        context.scene.bt_images.clear()
        return {'FINISHED'}


reg, unreg = bpy.utils.register_classes_factory((
    BT_OT_clear_images,
    BT_OT_action_image,
    Image
))


def register():
    reg()
    bpy.types.Scene.bt_images = CollectionProperty(type=Image)
    bpy.types.Scene.bt_images_action = bpy.props.IntProperty()


def unregister():
    unreg()
    if ImageLoader.preview_collection is not None:
        bpy.utils.previews.remove(ImageLoader.preview_collection)
        ImageLoader.preview_collection = None
