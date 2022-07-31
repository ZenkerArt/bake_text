from . import properties, timeline

modules = (
    properties,
    timeline
)


def register():
    for i in modules:
        i.register()


def unregister():
    for i in modules:
        i.unregister()
