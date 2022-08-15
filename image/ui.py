import bpy
from bpy.types import Context, Panel, UIList
from ..enums import OBJECT_RENDER_TYPE
from ..ui.base_ui import ObjectSettings
from .operators import BT_OT_add_image, ImageLoader, Image, BT_OT_remove_image, BT_OT_scan_images
from ..ui import BasePanel


class BT_UL_image_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type == 'DEFAULT':
            icon = ImageLoader.get_icon(item.name)
            layout = layout.row(align=True)
            layout.template_icon(icon_value=icon.icon_id, scale=1)
            layout.prop(item, 'name', text='', emboss=False)


class BT_PT_image_list(BasePanel, Panel):
    bl_label = 'Image Manager'
    images_is_loaded = False

    def draw(self, context):
        ImageLoader.init()

        layout = self.layout

        row = layout.row()

        row.template_list('BT_UL_image_list', '', context.scene,
                          'bt_images', context.scene, 'bt_images_active')

        mcol = row.column()
        col = mcol.column(align=True)
        col.operator(BT_OT_add_image.bl_idname, icon='ADD', text='')
        col.operator(BT_OT_remove_image.bl_idname, icon='REMOVE', text='')
        mcol.operator(BT_OT_scan_images.bl_idname, icon='FILE_REFRESH', text='')

        try:
            layout.template_icon(Image.active_icon().icon_id, scale=5)
            img = Image.active()
            layout.label(text='Название файла')
            layout.prop(img, 'name', text='')
        except Exception as e:
            print(e)


class BT_PT_image(ObjectSettings, Panel):
    bl_label = 'Картинка'

    def draw(self, context):
        ImageLoader.init()

        layout = self.layout
        settings = context.active_object.bt_settings
        layout.prop(settings, 'image', text='')
        layout.template_icon(ImageLoader.get_icon(settings.image).icon_id, scale=10)

    @classmethod
    def poll(cls, context: Context):
        try:
            settings = context.active_object.bt_settings
        except Exception:
            return False
        return super().poll(context) and settings.render_type == OBJECT_RENDER_TYPE.SPRITE


reg, unreg = bpy.utils.register_classes_factory((
    BT_UL_image_list,
    BT_PT_image_list,
    # BT_PT_image
))


def register():
    reg()


def unregister():
    unreg()
    if ImageLoader.preview_collection is not None:
        bpy.utils.previews.remove(ImageLoader.preview_collection)
        ImageLoader.preview_collection = None
