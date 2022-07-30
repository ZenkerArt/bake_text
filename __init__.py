from . import operators, properties, ui, anim

bl_info = {
    'name': 'Bake Text',
    'blender': (2, 80, 0),
    'category': 'Object',
    'author': 'Zenker'
}
1
modules = (
    properties,
    operators,
    ui,
    anim
)


def register():
    for i in modules:
        i.register()


def unregister():
    for i in modules:
        i.unregister()


if __name__ == '__main__':
    register()
