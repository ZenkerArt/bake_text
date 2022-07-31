from . import operators, properties, ui, anim, image

bl_info = {
    'name': 'Bake Text',
    'blender': (2, 80, 0),
    'category': 'Object',
    'author': 'Zenker'
}

modules = (
    properties,
    operators,
    ui,
    anim,
    image
)


def register():
    for i in modules:
        i.register()


def unregister():
    for i in modules:
        i.unregister()


if __name__ == '__main__':
    register()
