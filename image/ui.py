from ..ui import BasePanel
import bpy


class BT_UL_matslots_example(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.label(text='Id')
            row.prop(item, 'id', text='')


class BT_PT_object_list(BasePanel, bpy.types.Panel):
    bl_label = "UIList Panel"

    def draw(self, context):
        layout = self.layout




register, unregister = bpy.utils.register_classes_factory((
    BT_UL_matslots_example,
    BT_PT_object_list
))
