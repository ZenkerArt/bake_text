import bpy


class OBJECT_TYPE:
    PARTICLE_SYS = 'PARTICLE_SYS'
    PARENT = 'PARENT'
    OBJECT = 'OBJECT'

    @classmethod
    def get_type(cls, obj: bpy.types.Object) -> str:
        if obj.particle_systems:
            return cls.PARTICLE_SYS

        if obj.children:
            return cls.PARENT

        return cls.OBJECT


class OBJECT_BAKE_TYPE:
    BAKE_LOCATION = 'BAKE_LOCATION'
    BAKE_VERTEX = 'BAKE_VERTEX'
