import bpy
from .properties import TIMELINE_STATE
from ..enums import EVENTS_LOCAL, EVENTS_GLOBAL
from ..image.operators import ImageLoader
from ..openui.timeline import Timeline
from ..openui.timeline.ext import TimelineMove, TimelineActiveObj
from ..ui import BasePanel

timeline: Timeline = None
switch = False


def draw():
    timeline.render()


class BT_OT_timeline_add_keyframe(bpy.types.Operator):
    bl_label: str = 'Add Keyframe'
    bl_idname: str = 'bt.add_keyframe'

    action: bpy.props.StringProperty()
    event: bpy.props.StringProperty()

    def execute(self, context: bpy.types.Context):
        store = context.scene.bt_store_timeline
        global switch
        local_keyframes = context.active_object.bt_keyframes
        global_keyframes = store.keyframes()

        if store.state == TIMELINE_STATE.LOCAL:
            keyframes = local_keyframes
        elif store.state == TIMELINE_STATE.GLOBAL:
            keyframes = global_keyframes

        timeline_move = timeline.ext.get_ext(TimelineMove)
        timeline_active_obj = timeline.ext.get_ext(TimelineActiveObj)

        k = timeline_move.settings_keyframe
        if self.action == 'ADD_MOUSE':
            timeline.add_keyframe(timeline_move.mouse,
                                  None or self.event, keyframes=keyframes)

        if self.action == 'REMOVE_MOUSE' and k:
            for index, key in enumerate(keyframes):
                if k.keyframe.name == key.name:
                    keyframes.remove(index)
                    timeline_active_obj.update(context, keyframes)

        if self.action == 'SWITCH':
            # breakpoint()
            switch = not switch
            store.state = TIMELINE_STATE.GLOBAL if switch else TIMELINE_STATE.LOCAL

            if store.state == TIMELINE_STATE.GLOBAL:
                timeline_active_obj.update(context, global_keyframes)
            elif store.state == TIMELINE_STATE.LOCAL:
                timeline_active_obj.update(context, local_keyframes)

        if self.action == 'CLEAR':
            timeline.keyframes = {}
            keyframes.clear()
        return {'FINISHED'}


class BT_OT_timeline(bpy.types.Operator):
    bl_label: str = 'Timeline'
    bl_idname: str = 'bt.timeline'
    render = None
    click = False
    offset = 0

    @classmethod
    def destroy(cls):
        if cls.render:
            bpy.types.SpaceView3D.draw_handler_remove(cls.render, 'WINDOW')
            cls.render = None

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):
        if context.area:
            context.area.tag_redraw()

        v = timeline.event(context, event)
        if v:
            return v

        if self.render is None:
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        global timeline
        if timeline is None:
            timeline = Timeline()
        context.window_manager.modal_handler_add(self)
        if BT_OT_timeline.render is None:
            BT_OT_timeline.render = bpy.types.SpaceView3D.draw_handler_add(
                draw, (), 'WINDOW', 'POST_PIXEL')
        else:
            self.destroy()
        return {'RUNNING_MODAL'}


class BT_PT_timeline(bpy.types.Panel, BasePanel):
    bl_label: str = 'Timeline'

    def draw(self, context: bpy.types.Context):
        if BT_OT_timeline.render is None:
            self.layout.operator(BT_OT_timeline.bl_idname,
                                 text='Показать таймлайн')
            return
        else:
            self.layout.operator(BT_OT_timeline.bl_idname,
                                 text='Скрыть таймлайн')

        store = context.scene.bt_store_timeline

        text = {
            TIMELINE_STATE.GLOBAL: 'Локальный Таймлайн',
            TIMELINE_STATE.LOCAL: 'Глобальный Таймлайн'
        }

        o = self.layout.operator(BT_OT_timeline_add_keyframe.bl_idname,
                                 text=text[store.state])
        o.action = 'SWITCH'

        o = self.layout.operator(
            BT_OT_timeline_add_keyframe.bl_idname, text='Удалить все ключи')
        o.action = 'CLEAR'

        try:
            t = timeline.ext.get_ext(TimelineMove)
            if t.active_keyframe:
                self.layout.prop(t.active_keyframe.keyframe, 'event', text='')
        except AttributeError:
            pass


class BT_PT_settings_menu(bpy.types.Panel):
    bl_label = "Context Menu"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    def local_menu(self):
        t = timeline.ext.get_ext(TimelineMove)
        layout = self.layout

        keyframe = t.settings_keyframe.keyframe
        layout.prop(keyframe, 'event', text='')

        if keyframe.event == EVENTS_LOCAL.AddEnvironmentSprite or keyframe.event == EVENTS_LOCAL.SetEnvSpriteImage:
            layout.template_icon(ImageLoader.get_icon(
                keyframe.image).icon_id, scale=10)
            layout.prop(keyframe, 'image', text='')

        if keyframe.event == EVENTS_LOCAL.AddEnvironmentSprite:
            layout.prop(keyframe, 'color', text='')

        if keyframe.event == EVENTS_LOCAL.SetSunSensitivity or keyframe.event == EVENTS_LOCAL.AddEnvironmentSprite:
            layout.prop(keyframe, 'sun_sensitivity', text='')

    def global_menu(self):
        t = timeline.ext.get_ext(TimelineMove)
        layout = self.layout

        keyframe = t.settings_keyframe.keyframe
        layout.prop(keyframe, 'event', text='')

        if keyframe.event == EVENTS_GLOBAL.SetPlayerDistance:
            layout.prop(keyframe, 'player_dist', text='')

    def draw(self, context):
        store = context.scene.bt_store_timeline
        try:
            ImageLoader.init()
            if store.state == TIMELINE_STATE.LOCAL:
                self.local_menu()
            elif store.state == TIMELINE_STATE.GLOBAL:
                self.global_menu()

        except AttributeError:
            pass

        o = self.layout.operator(
            BT_OT_timeline_add_keyframe.bl_idname, text='Remove')
        o.action = 'REMOVE_MOUSE'


class BT_MT_context_menu(bpy.types.Menu):
    bl_label = "Context Menu"

    def draw(self, context):
        layout = self.layout
        store = context.scene.bt_store_timeline
        events = EVENTS_LOCAL

        if store.state == TIMELINE_STATE.GLOBAL:
            events = EVENTS_GLOBAL

        for i in events.enum():
            o = layout.operator(
                BT_OT_timeline_add_keyframe.bl_idname, text=i[1])
            o.action = 'ADD_MOUSE'
            o.event = i[0]


reg, unreg = bpy.utils.register_classes_factory((
    BT_OT_timeline,
    BT_PT_timeline,
    BT_OT_timeline_add_keyframe,
    BT_PT_settings_menu,
    BT_MT_context_menu
))


def register():
    reg()


def unregister():
    unreg()
    BT_OT_timeline.destroy()
