from . import properties, ui, operators, context_menu
from .g import Global

modules = (
    properties,
    ui,
    operators,
    context_menu
)


def register():
    for i in modules:
        i.register()


def unregister():
    Global.unregister()
    for i in modules:
        i.unregister()
