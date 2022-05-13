#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk
from .gtk import g_pSettings, Dialog, APPVERSION

class SettingsDialog(Dialog):

    def postinit(self, pData):

        self.m_lDestinations = g_pSettings.get_strv('destinations')
        self.m_strCompress = g_pSettings.get_string('default-compress')
        self.m_strTemp = g_pSettings.get_string('temp-location')
        self.pCheckButtonFakeStereo.set_active(g_pSettings.get_boolean('check-fake-stereo'))
        self.pCheckButtonRemoveSilent.set_active(g_pSettings.get_boolean('remove-silent-channels'))
        self.pCheckButtonRemoveLfe.set_active(g_pSettings.get_boolean('remove-lfe-channel'))
        self.pCheckButtonSaturate.set_active(g_pSettings.get_boolean('saturate-multichannel'))
        self.pCheckButtonTitleCase.set_active(g_pSettings.get_boolean('titlecase'))

        for sDestination in self.m_lDestinations:

            self.pListStore.append([sDestination])

        pTreeSelection = self.pTreeView.get_selection()
        pTreeSelection.select_path('0')

        if self.m_strCompress == 'flac':
            self.pRadiobuttonCompressFLAC.set_active(True)
        elif self.m_strCompress == 'aac':
            self.pRadiobuttonCompressAAC.set_active(True)
        else:
            self.pRadiobuttonCompressAuto.set_active(True)

        if self.m_strTemp == 'tmp':
            self.pRadiobuttonTempTmp.set_active(True)
        else:
            self.pRadiobuttonTempSource.set_active(True)

        g_pSettings.set_int('settings-last-shown', int(''.join([('0' + n)[-2:] for n in APPVERSION.split('.')])))

    def onButtonSaveClicked(self, pWidget):

        g_pSettings.set_strv('destinations', self.m_lDestinations)
        g_pSettings.set_boolean('check-fake-stereo', self.pCheckButtonFakeStereo.get_active())
        g_pSettings.set_boolean('remove-silent-channels', self.pCheckButtonRemoveSilent.get_active())
        g_pSettings.set_boolean('remove-lfe-channel', self.pCheckButtonRemoveLfe.get_active())
        g_pSettings.set_boolean('saturate-multichannel', self.pCheckButtonSaturate.get_active())
        g_pSettings.set_boolean('titlecase', self.pCheckButtonTitleCase.get_active())
        g_pSettings.set_string('default-compress', self.m_strCompress)
        g_pSettings.set_string('temp-location', self.m_strTemp)

    def onTreeSelectionChanged(self, pTreeSelection):

        if pTreeSelection.count_selected_rows() == 0:

            self.pButtonRemove.set_sensitive(False)
            self.pButtonDefault.set_sensitive(False)

        else:

            sRow = pTreeSelection.get_selected_rows()[1][0].to_string()

            if sRow == '0':

                self.pButtonDefault.set_sensitive(False)

            else:

                self.pButtonDefault.set_sensitive(True)

            if len(self.pListStore) > 1:

                self.pButtonRemove.set_sensitive(True)

            else:

                self.pButtonRemove.set_sensitive(False)

    def onButtonAddClicked(self, pWidget):

        pDialog = Gtk.FileChooserDialog(_('Add a base folder'), self.pDialog, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        pDialog.set_current_folder(self.m_lDestinations[0])

        if pDialog.run() == Gtk.ResponseType.OK:

            sFolder = pDialog.get_current_folder()
            self.m_lDestinations.append(sFolder)
            self.pListStore.append([sFolder])
            pTreeSelection = self.pTreeView.get_selection()
            sPath = str(len(self.pListStore) - 1)
            pTreeSelection.select_path(sPath)

        pDialog.destroy()

    def onButtonRemoveClicked(self, pWidget):

        pTreeSelection = self.pTreeView.get_selection()
        nRow = int(pTreeSelection.get_selected_rows()[1][0].to_string())
        del self.m_lDestinations[nRow]
        del self.pListStore[nRow]
        pTreeSelection.select_path('0')

    def onButtonDefaultClicked(self, pWidget):

        pTreeSelection = self.pTreeView.get_selection()
        nRow = int(pTreeSelection.get_selected_rows()[1][0].to_string())
        sPath = self.pListStore[nRow][0]
        del self.m_lDestinations[nRow]
        self.m_lDestinations.insert(0, sPath)
        del self.pListStore[nRow]
        self.pListStore.insert(0, [sPath])
        pTreeSelection.select_path('0')

    def onRadiobuttonCompressToggled(self, pWidget):

        if self.pRadiobuttonCompressFLAC.get_active():
            self.m_strCompress = 'flac'
        elif self.pRadiobuttonCompressAAC.get_active():
            self.m_strCompress = 'aac'
        else:
            self.m_strCompress = 'auto'

    def onRadiobuttonTempToggled(self, pWidget):

        if self.pRadiobuttonTempTmp.get_active():
            self.m_strTemp = 'tmp'
        else:
            self.m_strTemp = 'src'
