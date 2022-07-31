from . import ui, operators

modules = (
    ui,
    operators
)


def register():
    for i in modules:
        i.register()


def unregister():
    for i in modules:
        i.unregister()
