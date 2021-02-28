#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk
from .gtk import g_pSettings, Dialog, APPVERSION

class SettingsDialog(Dialog):

    def postinit(self, pData):

        self.m_strFLAC = g_pSettings.get_string('destination-flac')
        self.m_strAAC = g_pSettings.get_string('destination-aac')
        self.m_strCompress = g_pSettings.get_string('default-compress')
        self.m_strTemp = g_pSettings.get_string('temp-location')
        self.pCheckButtonFakeStereo.set_active(g_pSettings.get_boolean('check-fake-stereo'))
        self.pCheckButtonRemoveSilent.set_active(g_pSettings.get_boolean('remove-silent-channels'))
        self.pCheckButtonRemoveLfe.set_active(g_pSettings.get_boolean('remove-lfe-channel'))
        self.pCheckButtonSaturate.set_active(g_pSettings.get_boolean('saturate-multichannel'))
        self.pCheckButtonTitleCase.set_active(g_pSettings.get_boolean('titlecase'))
        self.pFilechooserbuttonFLAC.set_filename(self.m_strFLAC)
        self.pFilechooserbuttonAAC.set_filename(self.m_strAAC)

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

        g_pSettings.set_string('destination-flac', self.m_strFLAC)
        g_pSettings.set_string('destination-aac', self.m_strAAC)
        g_pSettings.set_boolean('check-fake-stereo', self.pCheckButtonFakeStereo.get_active())
        g_pSettings.set_boolean('remove-silent-channels', self.pCheckButtonRemoveSilent.get_active())
        g_pSettings.set_boolean('remove-lfe-channel', self.pCheckButtonRemoveLfe.get_active())
        g_pSettings.set_boolean('saturate-multichannel', self.pCheckButtonSaturate.get_active())
        g_pSettings.set_boolean('titlecase', self.pCheckButtonTitleCase.get_active())
        g_pSettings.set_string('default-compress', self.m_strCompress)
        g_pSettings.set_string('temp-location', self.m_strTemp)

    def onFilechooserbuttonFLACSelectionChanged(self, pWidget):

        self.m_strFLAC = pWidget.get_filename()

    def onFilechooserbuttonAACSelectionChanged(self, pWidget):

        self.m_strAAC = pWidget.get_filename()

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
