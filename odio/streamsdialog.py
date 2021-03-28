#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .gtk import Dialog, quote
from gi.repository import Gtk
import subprocess
import datetime

class StreamsDialog(Dialog):

    lTitles = []
    lChapters = []
    dChapters = {}

    def populate(self, nTitle):

        self.pListstoreChapters.clear()

        for dChapter in self.lTitles[nTitle]['chapter']:

            self.pListstoreChapters.append([str(dChapter['ix']).zfill(2), str(datetime.timedelta(seconds=dChapter['length'])).split('.')[0], dChapter['length']])

        self.pTreeviewChapters.get_selection().select_path(0)

    def preinit(self, pParent, sPath):

        self.lTitles = eval(subprocess.Popen('lsdvd -c -Oy -a ' + quote(sPath) + ' 2>/dev/null', stdout=subprocess.PIPE, shell=True, universal_newlines = True).communicate()[0].split('lsdvd = ', 1)[1], {})['track']

        for dTitle in self.lTitles:

            for dAudio in dTitle['audio']:

                if 'lpcm' in dAudio['format']:

                    return True

        pDlg = Gtk.MessageDialog(parent=pParent, modal=True, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.CLOSE, text=_('Disc {path} contains no LPCM audio').format(path=sPath))
        pDlg.run()
        pDlg.destroy()

        return False

    def postinit(self, sPath):

        self.pTreeviewcolumnLength.get_cells()[0].set_property('xalign', 1.0)
        self.pTreeviewcolumnChapterLength.get_cells()[0].set_property('xalign', 1.0)

        for dTitle in self.lTitles:

            if int(dTitle['length']) > 60:

                self.pListstoreTitles.append([str(dTitle['ix']).zfill(2), str(datetime.timedelta(seconds=dTitle['length'])).split('.')[0]])

        self.pTreeviewTitles.get_selection().select_path(0)

    def onTreeviewSelectionTitlesChanged(self, pTreeSelection):

        pIter = pTreeSelection.get_selected()[1]
        nSelection = int(self.pListstoreTitles.get_string_from_iter(pIter))
        nTitle = int(self.pListstoreTitles[nSelection][0]) - 1

        self.populate(nTitle)

    def onTreeviewSelectionChaptersChanged(self, pTreeSelection):

        if pTreeSelection.count_selected_rows() == 0:

            for nPath in self.lChapters:

                pTreeSelection.select_path(nPath)

        else:

            self.lChapters = pTreeSelection.get_selected_rows()[1]

    def onButtonOKClicked(self, pButton):

        self.dChapters = {'title': self.pListstoreTitles.get_value(self.pTreeviewTitles.get_selection().get_selected()[1], 0).lstrip('0'), 'chapters': [], 'count': len(self.pListstoreChapters)}

        for pPath in self.lChapters:

            self.dChapters['chapters'].append({'chapter': self.pListstoreChapters[pPath][0].lstrip('0'), 'length': self.pListstoreChapters[pPath][2]})
