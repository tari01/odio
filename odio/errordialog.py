#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk
from .gtk import Dialog

class ErrorDialog (Dialog):

    def postinit (self, lErrors):

        pBuffer =  Gtk.TextBuffer.new (None)
        sText = '\n\n'.join(lErrors)
        pBuffer.set_text (sText)
        self.pTextView.set_buffer (pBuffer)
