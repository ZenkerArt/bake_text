from dataclasses import dataclass
import json
import bpy
from .gconfig.events import GEventPool
from mathutils import Vector
import numpy


@dataclass
class ObjData:
    frame: int
    loc: list[float]
    rot: list[float]
    scale: list[float]
    id: str = None


def bake_object(obj: bpy.types.Object, end_frame: int):
    arr = []

    for i in range(0, end_frame):
        bpy.context.scene.frame_set(i)
        data = ObjData(
            frame=i,
            loc=list(obj.location),
            rot=list(obj.rotation_euler),
            scale=list(obj.scale)
        )

        arr.append(data)

    return arr


def bake_vertex(obj: bpy.types.Object, end_frame: int):
    context: bpy.types.Context = bpy.context
    mat = obj.matrix_world
    verts = []

    for i in range(0, end_frame):
        context.scene.frame_set(i)
        mesh: bpy.types.Mesh = obj.data
        for index, vert in enumerate(mesh.vertices):
            data = ObjData(
                frame=i,
                loc=list(mat @ vert.co),
                rot=[90, 0, 0],
                scale=list(mat @ Vector([1] * 3)),
                id=str(index)
            )
            verts.append(data)

    return verts


def bake_particle(obj: bpy.types.Object, end_frame: int):
    context: bpy.types.Context = bpy.context
    dg = context.evaluated_depsgraph_get()
    ob: bpy.types.Object = obj.evaluated_get(dg)

    ps = ob.particle_systems.active
    particles = []
    mat = ob.matrix_world

    for i in range(0, end_frame):
        context.scene.frame_set(i)
        for index, p in enumerate(ps.particles):
            obj = ObjData(
                frame=i,
                loc=list(mat @ p.location),
                rot=list(p.rotation)[:3],
                scale=list(mat @ Vector([p.size] * 3)),
                id=str(index)
            )
            particles.append(obj)

    return particles


def bool_to_int(b: bool) -> int:
    return 1 if b else -1


def xyz_to_arr(xyz) -> tuple[bool, bool, bool]:
    return xyz[0], xyz[2], xyz[1]


def to_numpy(arr) -> numpy.ndarray:
    return numpy.array(arr)


def apply_global_div(obj_data: ObjData):
    context = bpy.context
    settings = context.scene.bake_text_settings
    global_location = settings.global_location
    global_rotation = settings.global_rotation
    global_scale = settings.global_scale
    global_div = settings.global_div
    accuracy = settings.accuracy

    loc = to_numpy(obj_data.loc) / global_location / global_div
    rot = to_numpy(obj_data.rot) / global_rotation / global_div
    scale = to_numpy(obj_data.scale) / global_scale / global_div

    return tuple(i.round(accuracy) for i in (loc, rot, scale))


def apply_accuracy(value: float) -> float:
    accuracy = bpy.context.scene.bake_text_settings.accuracy
    return round(value, accuracy)


def apply_invers_round(vecs, invers):
    for vec, invers in zip(vecs, invers):
        for index, force in enumerate(vec):
            if invers[index]:
                vec[index] = -force


def calc_time(frame: float) -> float:
    settings = bpy.context.scene.bake_text_settings
    fps = settings.fps
    offset = settings.offset

    time = frame / fps + offset
    time = apply_accuracy(time)
    return time


def prepare(bake_data: list[ObjData], name: str) -> GEventPool:
    gevent: GEventPool = GEventPool()
    context = bpy.context
    scene = context.scene
    invers = scene.bake_text_invers

    invers = [
        xyz_to_arr(invers.position),
        xyz_to_arr(invers.rotation),
        xyz_to_arr(invers.scale)
    ]

    for obj_data in bake_data:
        time = calc_time(obj_data.frame)
        loc, rot, scale = apply_global_div(obj_data)

        vecs = [loc, rot, scale]

        apply_invers_round(vecs, invers)

        n = name
        if obj_data.id is not None:
            n = f'{n}_{obj_data.id}'

        gevent.set_position(time, n, loc)
        gevent.set_rotation(time, n, rot)
        gevent.set_scale(time, n, scale)
    return gevent


def save(arr: list[str]):
    settings = bpy.context.scene.bake_text_settings
    save_type: str = settings.save_type
    path = settings.path

    arr = json.dumps(arr).replace(' ', '')[1:-1]
    if save_type == 'file':
        with open(bpy.path.abspath(path), mode='w') as f:
            f.write(arr)
    else:
        bpy.context.window_manager.clipboard = arr
