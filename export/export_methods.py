import math

from bpy.types import Object, Mesh, Particle
from mathutils import Vector
from .utils import ObjVector, ObjTransform, xyz_to_xzy


def obj_params(obj: Object, frame: int, sums: list, name: str):
    return frame, sums, obj, name


def calc_sums(loc: ObjVector, rot: ObjVector, scale: ObjVector):
    vecs = loc, rot, scale
    vecs: ObjTransform = tuple(xyz_to_xzy(i) for i in vecs)
    sums = tuple(sum(i) for i in vecs)

    return sums, vecs


def save_obj(obj: Object, frame, arr, times, dg=None):
    loc: ObjVector = obj.location
    rot: ObjVector = tuple(math.degrees(i) for i in obj.rotation_euler)
    scale: ObjVector = obj.scale

    sums, vecs = calc_sums(loc, rot, scale)

    params = obj_params(obj, frame, sums, obj.name)
    times.append(params)
    arr.append(vecs)


def save_vertex(obj: Object, frame, arr, times, dg=None):
    ev_obj: Object = obj.evaluated_get(dg)
    mesh: Mesh = ev_obj.data

    for index, i in enumerate(mesh.vertices):
        loc: ObjVector = ev_obj.matrix_world @ i.co
        rot: ObjVector = 0, 0, 0
        scale: ObjVector = ev_obj.matrix_world @ ev_obj.scale

        sums, vecs = calc_sums(loc, rot, scale)

        params = obj_params(obj, frame, sums, f'{ev_obj.name}_{index}')
        times.append(params)

        arr.append(vecs)


def save_particle(obj: Object, frame, arr, times, dg=None):
    ev_obj: Object = obj.evaluated_get(dg)
    ps = ev_obj.particle_systems[0]
    rot = tuple(math.degrees(r) for r in obj.bt_settings.particle_rotation)

    for index, i in enumerate(ps.particles):
        i: Particle
        loc: ObjVector = ev_obj.matrix_world @ i.location
        # rot: ObjVector = tuple(math.degrees(r) for r in i.rotation)
        scale: ObjVector = ev_obj.matrix_world @ Vector((i.size,) * 3)

        sums, vecs = calc_sums(loc, rot, scale)

        params = obj_params(obj, frame, sums, f'{ev_obj.name}_{index}')
        times.append(params)

        arr.append(vecs)
