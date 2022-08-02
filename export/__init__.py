from dataclasses import dataclass

from bpy.types import Object
from mathutils import Vector


@dataclass
class Transforms:
    location: Vector
    rotation: Vector
    scale: Vector

    @classmethod
    def from_object(cls, obj: Object, location: Vector = None, rotation: Vector = None, scale: Vector = None):
        location = obj.location or location
        rotation = obj.rotation_euler or rotation
        scale = obj.scale or scale

        return cls(
            location=Vector(location),
            rotation=Vector(rotation),
            scale=Vector(scale)
        )
