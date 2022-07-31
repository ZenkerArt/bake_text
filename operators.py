import bpy
from .enums import OBJECT_BAKE_TYPE, OBJECT_TYPE
from .gconfig.events import GEventPool
from .utils import bake_object, bake_particle, bake_vertex, prepare, save


def get_object_type(obj: bpy.types.Object) -> str:
    if obj.particle_systems:
        return OBJECT_TYPE.PARTICLE_SYS

    if obj.children:
        return OBJECT_TYPE.PARENT

    return OBJECT_TYPE.OBJECT


class BT_OT_bake_text(bpy.types.Operator):
    bl_label: str = 'BakeText'
    bl_idname: str = 'bt.bake_text'
    fps: bpy.props.FloatProperty(default=10.0)
    offset: bpy.props.FloatProperty(default=1.0)

    @staticmethod
    def bake_parent(obj: bpy.types.Object):
        offset: float = bpy.context.scene.bake_text_settings.offset

        arr = []
        children = obj.children
        for child in children:
            arr.append({"time": offset, "data": [
                "SetParent", f'{child.name},{obj.name}']})

        return arr

    def execute(self, context: bpy.types.Context):
        end = context.scene.frame_end
        arr = []
        objects: list[bpy.types.Object] = context.selected_objects
        ignore: list[bpy.types.Object] = []
        gevents = GEventPool()

        for obj in objects:
            ignore.extend(obj.children)

        for obj in objects:
            ps = obj.particle_systems
            name = obj.name
            object_type = get_object_type(obj)
            bake = None

            if object_type == OBJECT_TYPE.PARENT:
                arr.extend(self.bake_parent(obj))
                gevents.add(prepare(bake_object(obj, end), name))
                continue

            if any(i.name == obj.name for i in ignore):
                continue

            if object_type == OBJECT_TYPE.PARTICLE_SYS:
                bake = bake_particle(obj, end)
                name = ps.active.settings.name
            elif obj.bake_text_info.bake_type == OBJECT_BAKE_TYPE.BAKE_LOCATION:
                bake = bake_object(obj, end)

            if bake:
                gevents.add(prepare(bake, name))

        save(gevents.to_list())

        return {'FINISHED'}


class BT_OT_invers(bpy.types.Operator):
    bl_label: str = 'BakeText'
    bl_idname: str = 'bt.invers'
    vec_name: bpy.props.StringProperty()
    x: bpy.props.BoolProperty(default=False)
    y: bpy.props.BoolProperty(default=False)
    z: bpy.props.BoolProperty(default=False)

    def execute(self, context: bpy.types.Context):
        xyz = getattr(context.scene, f'bt_invers_{self.vec_name}')
        xyz.x = self.x
        xyz.y = self.y
        xyz.z = self.z
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory((
    BT_OT_bake_text,
    BT_OT_invers
))
