#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk
from .gtk import Dialog

class LogDialog(Dialog):

    m_lstEncoded = []

    def postinit(self, lstEncoded):

        self.m_lstEncoded = lstEncoded
        self.pTextBuffer = self.pTextviewLog.get_buffer()
        pTagTable = self.pTextBuffer.get_tag_table()
        pArtistTag = Gtk.TextTag.new('artist')
        pArtistTag.set_property('scale', 1.5)
        pArtistTag.set_property('weight', 750)
        pTagTable.add(pArtistTag)
        self.pComboboxtextGroup.set_active(1)

    def onComboboxtextGroupChanged(self, pWidget):

        dctEncoded = {}
        nGroup = pWidget.get_active()

        for dctTitles in self.m_lstEncoded:

            strCat = dctTitles['album'] + ' (' + dctTitles['albumartist'] + ')'

            if nGroup == 0:

                strCat = dctTitles['albumartist']

            elif nGroup == 1:

                strCat = dctTitles['artist']

                if dctTitles['albumartist'] != strCat:
                    strCat += ' (' + dctTitles['albumartist'] + ')'

            if strCat not in dctEncoded:
                dctEncoded[strCat] = []

            if dctTitles['title'] not in dctEncoded[strCat]:
                dctEncoded[strCat].append(dctTitles['title'])

        self.pTextBuffer.delete(self.pTextBuffer.get_start_iter(), self.pTextBuffer.get_end_iter())

        for strArtist, lstTracks in list(dctEncoded.items()):

            pIter = self.pTextBuffer.get_end_iter()

            if not pIter.is_start():
                strArtist = '\n\n' + strArtist

            self.pTextBuffer.insert_with_tags_by_name(pIter, strArtist + '\n', 'artist')

            lstTracks.sort(key = lambda s: s.replace('\'', '').replace('-', '').replace('(', 'aaa').lower())

            for strTrack in lstTracks:
                self.pTextBuffer.insert(self.pTextBuffer.get_end_iter(), '\n' + strTrack)

    def onButtonClearClicked(self, pWidget):

        self.m_lstEncoded = []
