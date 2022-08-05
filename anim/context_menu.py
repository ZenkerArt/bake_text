import bpy
from bpy.types import Panel, Menu
from .timeline_states import TIMELINE_STATE, TimelineState
from ..openui.timeline import TimelineMove
from .g import Global
from .operators import BT_OT_timeline_action
from ..enums import EVENTS_LOCAL, EVENTS_GLOBAL
from ..image.operators import ImageLoader


class BT_PT_settings_menu(Panel):
    bl_label = 'Context Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    def local_menu(self):
        layout = self.layout

        keyframe = Global.timeline.keyframe.context_keyframe.keyframe
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
        t = Global.timeline.ext.get_ext(TimelineMove)
        layout = self.layout

        keyframe = t.settings_keyframe.keyframe
        layout.prop(keyframe, 'event', text='')

        if keyframe.event == EVENTS_GLOBAL.SetPlayerDistance:
            layout.prop(keyframe, 'player_dist', text='')

    def draw(self, context):
        state = TimelineState.state()

        try:
            ImageLoader.init()
            if state == TIMELINE_STATE.OBJECT:
                self.local_menu()
            elif state == TIMELINE_STATE.GLOBAL:
                self.global_menu()

        except AttributeError:
            pass

        o = self.layout.operator(
            BT_OT_timeline_action.bl_idname, text='Remove')
        o.action = 'REMOVE_MOUSE'


class BT_MT_context_menu(Menu):
    bl_label = 'Context Menu'

    def draw(self, context):
        layout = self.layout
        events = EVENTS_LOCAL

        if TimelineState.state() == TIMELINE_STATE.GLOBAL:
            events = EVENTS_GLOBAL

        for i in events.enum():
            o = layout.operator(
                BT_OT_timeline_action.bl_idname, text=i[1])
            o.action = 'ADD_MOUSE'
            o.event = i[0]


register, unregister = bpy.utils.register_classes_factory((
    BT_PT_settings_menu,
    BT_MT_context_menu
))
