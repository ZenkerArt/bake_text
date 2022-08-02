from typing import Optional

import bpy
from bpy.props import StringProperty, CollectionProperty
from bpy.utils.previews import ImagePreviewCollection
from bpy_extras.io_utils import ImportHelper
from bpy_types import Operator, PropertyGroup
from ..btio import ProjectFolders


def image_enum(self, context):
    scene = context.scene
    arr = []
    for i in scene.bt_images:
        arr.append((
            i.name, i.name, ''
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


def add_image(filepath: str):
    file = ProjectFolders.images.save_file(filepath)
    ImageLoader.add_icon(file.name, file.path)

    image = bpy.context.scene.bt_images.add()
    image.path = file.path
    image.name = file.name
    image.prev_name = file.name


class Image(PropertyGroup):
    name: bpy.props.StringProperty(update=on_image_rename)
    prev_name: bpy.props.StringProperty()
    path: bpy.props.StringProperty()

    @classmethod
    def active(cls):
        scene = bpy.context.scene
        return scene.bt_images[scene.bt_images_active]

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


class BT_OT_add_image(Operator, ImportHelper):
    bl_idname = 'bt.add_image'
    bl_label = 'Add Image'

    filter_glob: StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp', options={'HIDDEN'})

    def execute(self, context: bpy.types.Context):
        filepath: str = self.properties.filepath
        add_image(filepath)
        return {'FINISHED'}


class BT_OT_remove_image(Operator):
    bl_idname = 'bt.remove_image'
    bl_label = 'Remove Image'

    def execute(self, context: bpy.types.Context):
        try:
            ProjectFolders.images.remove_file(Image.active().name)
        except FileNotFoundError:
            pass
        context.scene.bt_images.remove(context.scene.bt_images_active)
        return {'FINISHED'}


class BT_OT_clear_images(Operator):
    bl_idname = 'bt.clear_images'
    bl_label = 'Clear Images'

    def execute(self, context: bpy.types.Context):
        for image in context.scene.bt_images.values():
            ProjectFolders.images.remove_file(image.name)
        context.scene.bt_images.clear()
        return {'FINISHED'}


class BT_OT_scan_images(Operator):
    bl_idname = 'bt.scan_images'
    bl_label = 'Scan Images'

    def execute(self, context: bpy.types.Context):
        names: list[str] = context.scene.bt_images.keys()
        s = ProjectFolders.images.scan()
        s_names = [i.name for i in s]

        for i in ProjectFolders.images.scan():
            if i.name in names:
                continue
            add_image(i.path)

        for index, name in enumerate(context.scene.bt_images.keys()):
            if name in s_names:
                continue
            context.scene.bt_images.remove(index)
        # context.scene.bt_images.clear()
        ImageLoader.load_icons()
        return {'FINISHED'}


reg, unreg = bpy.utils.register_classes_factory((
    BT_OT_clear_images,
    BT_OT_add_image,
    BT_OT_remove_image,
    BT_OT_scan_images,
    Image
))


def register():
    reg()
    bpy.types.Scene.bt_images = CollectionProperty(type=Image)
    bpy.types.Scene.bt_images_active = bpy.props.IntProperty()


def unregister():
    unreg()
    if ImageLoader.preview_collection is not None:
        bpy.utils.previews.remove(ImageLoader.preview_collection)
        ImageLoader.preview_collection = None
