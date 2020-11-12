#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2005 Joe Wreschnig, Michael Urman
#           2012, 2013 Christoph Reiter
#           2016 Robert Tari
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

import cairo
import math
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib

class DragScroll(object):

    # A treeview mixin for smooth drag and scroll (needs BaseView). Call scroll_motion in the 'drag-motion' handler and scroll_disable in the 'drag-leave' handler.
    __scroll_delay = None
    __scroll_periodic = None
    __scroll_args = (0, 0, 0, 0)
    __scroll_length = 0
    __scroll_last = None

    def __enable_scroll(self):
        """Start scrolling if it hasn't already"""
        if self.__scroll_periodic is not None or \
                self.__scroll_delay is not None:
            return

        def periodic_scroll():
            """Get the tree coords for 0,0 and scroll from there"""
            wx, wy, dist, ref = self.__scroll_args
            x, y = self.convert_widget_to_tree_coords(0, 0)
            x, y = self.convert_bin_window_to_widget_coords(x, y)

            # We reached an end, stop
            if self.__scroll_last == y:
                self.scroll_disable()
                return
            self.__scroll_last = y

            # If we went full speed for a while.. speed up
            # .. every number is made up here
            if self.__scroll_length >= 50 * ref:
                dist *= self.__scroll_length / (ref * 10)
            if self.__scroll_length < 2000 * ref:
                self.__scroll_length += abs(dist)

            try:
                self.scroll_to_point(-1, y + dist)
            except OverflowError:
                pass
            self.set_drag_dest(wx, wy)
            # we have to re-add the timeout.. otherwise they could add up
            # because scroll can last longer than 50ms
            GLib.source_remove(self.__scroll_periodic)
            self.__scroll_periodic = None
            enable_periodic_scroll()

        def enable_periodic_scroll():
            self.__scroll_periodic = GLib.timeout_add(50, periodic_scroll)
            self.__scroll_delay = None

        self.__scroll_delay = GLib.timeout_add(350, enable_periodic_scroll)

    def scroll_disable(self):
        """Disable all scrolling"""
        if self.__scroll_periodic is not None:
            GLib.source_remove(self.__scroll_periodic)
            self.__scroll_periodic = None
        if self.__scroll_delay is not None:
            GLib.source_remove(self.__scroll_delay)
            self.__scroll_delay = None
        self.__scroll_length = 0
        self.__scroll_last = None

    def scroll_motion(self, x, y):
        """Call with current widget coords during a dnd action to update
           scrolling speed"""

        visible_rect = self.get_visible_rect()
        if visible_rect is None:
            self.scroll_disable()
            return

        # I guess the bin to visible_rect difference is the header height
        # but this could be wrong
        start = self.convert_bin_window_to_widget_coords(0, 0)[1]
        end = visible_rect.height + start

        # Get the font height as size reference
        reference = max(self.create_pango_layout("").get_pixel_size()[1], 1)

        # If the drag is in the scroll area, adjust the speed
        scroll_offset = int(reference * 3)
        in_upper_scroll = (start < y < start + scroll_offset)
        in_lower_scroll = (y > end - scroll_offset)

        # thanks TI200
        def accel(x):
            try:
                return int(1.1 ** (x * 12 / reference)) - (x / reference)
            except ValueError:
                return 0

        if in_lower_scroll:
            diff = accel(y - end + scroll_offset)
        elif in_upper_scroll:
            diff = - accel(start + scroll_offset - y)
        else:
            self.scroll_disable()
            return

        # The area where we can go to full speed
        full_offset = int(reference * 0.8)
        in_upper_full = (start < y < start + full_offset)
        in_lower_full = (y > end - full_offset)
        if not in_upper_full and not in_lower_full:
            self.__scroll_length = 0

        # For the periodic scroll function
        self.__scroll_args = (x, y, diff, reference)

        # The area to trigger a scroll is a bit smaller
        trigger_offset = int(reference * 2.5)
        in_upper_trigger = (start < y < start + trigger_offset)
        in_lower_trigger = (y > end - trigger_offset)

        if in_upper_trigger or in_lower_trigger:
            self.__enable_scroll()

class BaseView():

    def is_accel(self, event, *accels):

        #Checks if the given keypress Gdk.Event matches any of accelerator strings
        assert accels

        if event.type != Gdk.EventType.KEY_PRESS:
            return False

        # ctrl+shift+x gives us ctrl+shift+X and accelerator_parse returns
        # lowercase values for matching, so lowercase it if possible
        keyval = event.keyval
        if not keyval & ~0xFF:
            keyval = ord(chr(keyval).lower())

        default_mod = Gtk.accelerator_get_default_mod_mask()

        for accel in accels:
            accel_keyval, accel_mod = Gtk.accelerator_parse(accel)

            # If the accel contains non default modifiers matching will
            # never work and since no one should use them, complain
            non_default = accel_mod & ~default_mod
            if non_default:
                print_w("Accelerator '%s' contains a non default modifier '%s'." %
                    (accel, Gtk.accelerator_name(0, non_default) or ""))

            # Remove everything except default modifiers and compare
            if (accel_keyval, accel_mod) == (keyval, event.state & default_mod):
                return True

        return False

    def __init__(self, oTreeviev):

        self.oTreeviev = oTreeviev
        self.oTreeviev.connect("key-press-event", self.__key_pressed)

    def __key_pressed(self, view, event):

        def get_first_selected():

            selection = self.oTreeviev.get_selection()
            model, paths = selection.get_selected_rows()
            return paths and paths[0] or None

        if self.is_accel(event, "Right") or self.is_accel(event, "<Primary>Right"):

            first = get_first_selected()

            if first:
                self.oTreeviev.expand_row(first, False)

        elif self.is_accel(event, "Left") or self.is_accel(event, "<Primary>Left"):

            first = get_first_selected()

            if first:

                if self.oTreeviev.row_expanded(first):
                    self.oTreeviev.collapse_row(first)

                else:

                    # if we can't collapse, move the selection to the parent, so that a second attempt collapses the parent
                    model = self.oTreeviev.get_model()
                    parent = model.iter_parent(model.get_iter(first))

                    if parent:
                        self.oTreeviev.set_cursor(model.get_path(parent))

    def set_drag_dest(self, x, y):

        path, pos = (None, None)
        lstPathPos = self.oTreeviev.get_dest_row_at_pos(x, y)

        if lstPathPos is not None:

            path, pos = lstPathPos

            if pos == Gtk.TreeViewDropPosition.INTO_OR_BEFORE:
                pos = Gtk.TreeViewDropPosition.BEFORE
            elif pos == Gtk.TreeViewDropPosition.INTO_OR_AFTER:
                pos = Gtk.TreeViewDropPosition.AFTER

        else:

            oModel = self.oTreeviev.get_model()
            pos = Gtk.TreeViewDropPosition.AFTER
            path = Gtk.TreePath.new_from_indices([len(oModel) - 1])

        self.oTreeviev.set_drag_dest_row(path, pos)

        return path, pos

class DragIconTreeView(BaseView):

    def __init__(self, oTreeviev):

        super(DragIconTreeView, self).__init__(oTreeviev)
        self.oTreeviev.connect('drag-begin', self.__begin)

    def __begin(self, view, drag_ctx):

        model, paths = view.get_selection().get_selected_rows()
        surface = self.create_multi_row_drag_icon(paths, max_rows=3)

        if surface is not None:
            Gtk.drag_set_icon_surface(drag_ctx, surface)

    def create_multi_row_drag_icon(self, paths, max_rows):

        if not paths:
            return

        if len(paths) == 1:
            return self.oTreeviev.create_row_drag_icon(paths[0])

        # create_row_drag_icon can return None
        icons = [self.oTreeviev.create_row_drag_icon(p) for p in paths[:max_rows]]
        icons = [i for i in icons if i is not None]

        if not icons:
            return

        # Gives (x, y, width, height) for a pixbuf or a surface, scale independent
        sizes = []

        for oIcon in icons:

            if isinstance(oIcon, GdkPixbuf.Pixbuf):

                sizes.append((0, 0, oIcon.get_width(), oIcon.get_height()))

            else:

                ctx = cairo.Context(oIcon)
                x1, y1, x2, y2 = ctx.clip_extents()
                x1 = int(math.floor(x1))
                y1 = int(math.floor(y1))
                x2 = int(math.ceil(x2))
                y2 = int(math.ceil(y2))
                x2 -= x1
                y2 -= y1

                sizes.append((x1, y1, x2, y2))
        #~Gives (x, y, width, height) for a pixbuf or a surface, scale independent

        if None in sizes:
            return

        width = max([s[2] for s in sizes])
        height = sum([s[3] for s in sizes])

        # this is the border width we see in the gtk provided surface, not much we can do besides hardcoding it here
        bw = 1
        layout = None

        if len(paths) > max_rows:

            more = _('and {rowcount} more').format(rowcount = len(paths) - max_rows)
            more = "<b><i>%s</i></b>" % more
            layout = self.oTreeviev.create_pango_layout("")
            layout.set_markup(more)
            layout.set_alignment(Pango.Alignment.LEFT)
            layout.set_width(Pango.SCALE * (width - 2 * bw))
            lw, lh = layout.get_pixel_size()
            height += lh
            height += 6  # padding

        surface = icons[0].create_similar(cairo.CONTENT_COLOR_ALPHA, width, height)
        ctx = cairo.Context(surface)

        # render background
        style_ctx = self.oTreeviev.get_style_context()
        Gtk.render_background(style_ctx, ctx, 0, 0, width, height)

        # render rows
        count_y = 0

        for icon, (x, y, icon_width, icon_height) in zip(icons, sizes):

            ctx.save()
            ctx.set_source_surface(icon, -x, count_y + -y)
            ctx.rectangle(bw, count_y + bw, icon_width - 2 * bw, icon_height - 2 * bw)
            ctx.clip()
            ctx.paint()
            ctx.restore()
            count_y += icon_height

        if layout:
            Gtk.render_layout(style_ctx, ctx, bw, count_y, layout)

        # render border
        Gtk.render_line(style_ctx, ctx, 0, 0, 0, height - 1)
        Gtk.render_line(style_ctx, ctx, 0, height - 1, width - 1, height - 1)
        Gtk.render_line(style_ctx, ctx, width - 1, height - 1, width - 1, 0)
        Gtk.render_line(style_ctx, ctx, width - 1, 0, 0, 0)

        return surface

class MultiDragTreeView(BaseView):

    def __init__(self, oTreeviev):

        super(MultiDragTreeView, self).__init__(oTreeviev)
        self.oTreeviev.connect('button-press-event', self.__button_press)
        self.oTreeviev.connect('button-release-event', self.__button_release)
        self.__pending_event = None

    def __button_press(self, view, event):

        if event.button == Gdk.BUTTON_PRIMARY:
            return self.__block_selection(event)

    def __block_selection(self, event):

        x, y = map(int, [event.x, event.y])

        try:
            path, col, cellx, celly = self.oTreeviev.get_path_at_pos(x, y)
        except TypeError:
            return True

        self.oTreeviev.grab_focus()
        selection = self.oTreeviev.get_selection()
        is_selected = selection.path_is_selected(path)
        mod_active = event.get_state() & (Gtk.accelerator_parse("<Primary>")[1] | Gdk.ModifierType.SHIFT_MASK)

        if is_selected and not mod_active:

            self.__pending_event = [x, y]
            selection.set_select_function(lambda *args: False, None)

        elif event.type == Gdk.EventType.BUTTON_PRESS:

            self.__pending_event = None
            selection.set_select_function(lambda *args: True, None)

    def __button_release(self, view, event):

        if self.__pending_event:

            selection = self.oTreeviev.get_selection()
            selection.set_select_function(lambda *args: True, None)
            oldevent = self.__pending_event
            self.__pending_event = None
            x, y = map(int, [event.x, event.y])

            if oldevent != [x, y]:
                return True

            try:
                path, col, cellx, celly = self.oTreeviev.get_path_at_pos(x, y)
            except TypeError:
                return True

            self.oTreeviev.set_cursor(path, col, 0)

class treeviewExtend(DragIconTreeView, MultiDragTreeView):

    def __init__(self, oTreeviev, oClass = None, strTarget = None):

        self.oClass = oClass
        lstTargets = [Gtk.TargetEntry.new('treeview-row', Gtk.TargetFlags.SAME_WIDGET, 0)]

        if strTarget:
                lstTargets.append(Gtk.TargetEntry.new(strTarget, Gtk.TargetFlags.OTHER_APP, 1))

        oTreeviev.drag_dest_set(Gtk.DestDefaults.DROP | Gtk.DestDefaults.MOTION, lstTargets, Gdk.DragAction.MOVE | Gdk.DragAction.COPY)
        oTreeviev.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [lstTargets[0]], Gdk.DragAction.MOVE)
        oTreeviev.connect('drag-motion', self.onDragMotion)
        oTreeviev.connect('drag-leave', self.onDragLeave)
        oTreeviev.connect('drag-data-get', self.onDragDataGet)
        oTreeviev.connect('drag-data-received', self.onDragDataReceived)
        super(treeviewExtend, self).__init__(oTreeviev)

    def onDragMotion(self, oWidget, oDragContext, nX, nY, nTime):

        if oDragContext.list_targets()[0].name() == 'treeview-row':

            lstPaths = oWidget.get_selection().get_selected_rows()[1]

            if len(lstPaths) == 0:
                return False

            oPathDest = self.set_drag_dest(nX, nY)[0]

            if oPathDest.get_indices()[0] in [oPath.get_indices()[0] for oPath in lstPaths]:
                return False

            Gdk.drag_status(oDragContext, Gdk.DragAction.MOVE, nTime)

        else:

            oWidget.drag_highlight()
            Gdk.drag_status(oDragContext, Gdk.DragAction.COPY, nTime)

        return True

    def onDragLeave(self, oWidget, oDragContext, nTime):

        oWidget.drag_unhighlight()

    def onDragDataGet(self, oWidget, oDragContext, oSelectionData, nInfo, nTime):

        lstPaths = oWidget.get_selection().get_selected_rows()[1]

        if len(lstPaths) == 0:
            return

        oSelectionData.set(oSelectionData.get_target(), 8, [oPath.get_indices()[0] for oPath in lstPaths])

    def onDragDataReceived(self, oWidget, oDragContext, nX, nY, oSelectionData, nInfo, nTime):

        if nInfo == 0:

            oModel = oWidget.get_model()
            oPath, nPosition = self.set_drag_dest(nX, nY)
            lstPaths = oSelectionData.get_data()

            if oPath.get_indices()[0] not in lstPaths:

                oDestIter = oModel.get_iter(oPath)

                for oIter in [oModel.get_iter_from_string(str(nPath)) for nPath in lstPaths]:

                    if nPosition == Gtk.TreeViewDropPosition.AFTER:

                        oModel.move_after(oIter, oDestIter)
                        oDestIter = oIter

                    else:

                        oModel.move_before(oIter, oDestIter)

            oWidget.set_drag_dest_row(None, Gtk.TreeViewDropPosition.AFTER)
            Gtk.drag_finish(oDragContext, True, True, nTime)

        else:

            strFunc = Gtk.Buildable.get_name(oWidget)
            strFunc = 'on' + strFunc[:1].upper() + strFunc[1:] + 'DragDataReceived'

            getattr(self.oClass, strFunc)(oSelectionData.get_uris())
            Gtk.drag_finish(oDragContext, True, False, nTime)
