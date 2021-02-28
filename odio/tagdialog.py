#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GdkPixbuf
from bs4 import BeautifulSoup
from .gtk import g_pSettings, Dialog
from .appdata import *
from .titlecase import titlecase
import os
import re
import urllib.request

class TagDialog(Dialog):

    def postinit(self, lstParams):

        self.m_nCurrentFile = 1
        self.pListstore = lstParams[0]
        self.m_lstSelection = lstParams[1]
        self.bClipboardPaste = False

        self.pComboboxTrackNum.set_model(self.pListstoreNumbers)
        self.pComboboxTrackTotal.set_model(self.pListstoreNumbers)
        self.pComboboxDiscNum.set_model(self.pListstoreNumbers)
        self.pComboboxDiscTotal.set_model(self.pListstoreNumbers)
        self.pComboboxGenre.set_model(self.pListstoreGenres)

        self.onButtonFileUpClicked(None)

    def onButtonFileUpClicked(self, pButton):

        self.m_nCurrentFile -= 1

        if self.m_nCurrentFile == 0:
            self.pButtonFileUp.set_sensitive(False)

        if len(self.m_lstSelection) == 1:
            self.pButtonFileDown.set_sensitive(False)
        else:
            self.pButtonFileDown.set_sensitive(True)

        self.displayFileTag()

    def onButtonFileDownClicked(self, pButton):

        self.m_nCurrentFile += 1

        if self.m_nCurrentFile == len(self.m_lstSelection) - 1:
            self.pButtonFileDown.set_sensitive(False)

        self.pButtonFileUp.set_sensitive(True)
        self.displayFileTag()

        return True

    @staticmethod
    def ReplaceChars(strText):

        return strText.replace('"', '').replace('*', '-').replace('/', '-').replace(':', '-').replace('<', '-').replace('>', '-').replace('?', '').replace('\\', '-').replace('|', '-')

    def onButtonGetTagFromWebClicked(self, pButton):

        try:

            strPage = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).wait_for_text()

            if strPage == None or 'allmusic' not in strPage:

                pDlg = Gtk.MessageDialog(self.pDialog, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, _('No allmusic.com page address found on the clipboard'))
                pDlg.run()
                pDlg.destroy()
                return

            pMatch = re.match('^(\d*)(.+)', strPage)
            strPage = pMatch.group(2)
            nTitleOffset = 0

            if len(pMatch.group(1)) > 0:
                nTitleOffset = int(pMatch.group(1))

            if not strPage.startswith('http'):
                strPage = 'http://' + strPage

            class FancyURLopener(urllib.request.FancyURLopener):
                version = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/43.0.2357.130 Chrome/43.0.2357.130 Safari/537.36'

            hFancyURLopener = FancyURLopener()
            pPage = hFancyURLopener.open(strPage)

            strPage = pPage.read()

            pPage.close()

            pDoc = BeautifulSoup(strPage, 'html.parser')
            strGenre = ''
            nYear = 0

            pReleaseYear = pDoc.find('div', {'class': 'release-date'})
            pRecordingYear = pDoc.find('div', {'class': 'recording-date'})
            lstTitles = [pDoc.findAll('td', {'class': 'performer'}), pDoc.findAll('div', {'class': 'title'})]
            pGenres = pDoc.find('div', {'class': 'genre'})
            lstStyles = pDoc.find('div', {'class': 'styles'})
            pAlbumArtist = pDoc.find('h2', {'class': 'album-artist'}) or pDoc.find('h3', {'class': 'album-artist'}) or pDoc.find('h3', {'class': 'release-artist'}) or pDoc.find('h2', {'class': 'release-artist'})
            pAlbum = pDoc.find('h2', {'class': 'album-title'}) or pDoc.find('h2', {'class': 'release-title'}) or pDoc.find('h1', {'class': 'album-title'}) or pDoc.find('a', {'class': 'album-title'})
            strAlbum = pAlbum.contents[0].replace('[', '(').replace(']', ')').replace('&amp;', '&').strip()

            if pGenres is not None:

                for pGenre in pGenres.div.findAll('a'):
                    strGenre += ', ' + pGenre.string.strip(';')

            if lstStyles is not None:

                strGenre += ' - '

                for pStyle in lstStyles.findAll('a'):
                    strGenre += pStyle.string.strip(';') + ', '

            if pReleaseYear is not None:

                lstReleaseYear = pReleaseYear.span.string.strip().replace('-', ' ').replace(',', '').split(' ')

                for strYear in lstReleaseYear:

                    if strYear.isdigit():
                        nYear = strYear

            if pRecordingYear is not None:

                strRecordingYear = pRecordingYear.div.string

                if strRecordingYear is not None:

                    lstRecordingYear = pRecordingYear.div.string.strip().replace('-', ' ').replace(',', '').split(' ')

                    for strYear in lstRecordingYear:

                        if strYear.isdigit():
                            nYear = strYear

            if pAlbumArtist.a != None:
                pAlbumArtist = pAlbumArtist.a

            pAlbumArtist = ''.join(pAlbumArtist.strings).replace('&amp;', '&').strip()

            for nIndex in self.m_lstSelection:

                self.pListstore[nIndex][2] = pAlbumArtist
                self.pListstore[nIndex][1] = pAlbumArtist
                self.pListstore[nIndex][4] = strAlbum

                if nYear != 0:
                    self.pListstore[nIndex][10] = nYear

                if len(strGenre) != 0:
                    self.pListstore[nIndex][3] = strGenre.strip(', ')

                if lstTitles[0] != None and len(lstTitles[1]) and nTitleOffset < len(lstTitles[1]):

                    if pAlbumArtist == 'Various Artists' and lstTitles[0] != None and len(lstTitles[0]) == len(lstTitles[1]):

                        self.pListstore[nIndex][1] = ''.join(lstTitles[0][nTitleOffset].findAll(text=True))
                        self.pListstore[nIndex][1] = self.pListstore[nIndex][1].replace('&amp;', '&')
                        self.pListstore[nIndex][1] = self.pListstore[nIndex][1].replace(' / ', '/')
                        self.pListstore[nIndex][1] = self.pListstore[nIndex][1].strip()

                    sTitle = lstTitles[1][nTitleOffset].a.string

                    if g_pSettings.get_boolean('titlecase'):

                        sTitle = self.ConvertToTitleCase(None, None, sTitle)

                    self.pListstore[nIndex][7] = sTitle

                if int(self.pListstore[nIndex][8]) > 0 and int(self.pListstore[nIndex][9]) > 1:
                    self.pListstore[nIndex][13] = os.path.join(TagDialog.ReplaceChars(self.pListstore[nIndex][2]), TagDialog.ReplaceChars(self.pListstore[nIndex][4]), 'Disc ' + self.pListstore[nIndex][8])
                else:
                    self.pListstore[nIndex][13] = os.path.join(TagDialog.ReplaceChars(self.pListstore[nIndex][2]), TagDialog.ReplaceChars(self.pListstore[nIndex][4]))

                nTitleOffset += 1

            if lstTitles[1] == None or nTitleOffset > len(lstTitles[1]):

                pDlg = Gtk.MessageDialog(self.pDialog, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, _('Not all tracks got tracknames'))
                pDlg.run()
                pDlg.destroy()

            self.displayFileTag()

        except Exception as e:

            print(e)

            pDlg = Gtk.MessageDialog(self.pDialog, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, _('Error parsing web page'))
            pDlg.run()
            pDlg.destroy()

    def onButtonImageClicked(self, pButton):

        dlg = Gtk.FileChooserDialog(_('Select an image file'), self.pDialog, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dlg.set_filter(self.pFilefilterImages)
        dlg.set_current_folder(g_pSettings.get_string('image-folder'))

        if dlg.run() == Gtk.ResponseType.OK:

            pRow = self.pListstore[self.m_lstSelection[self.m_nCurrentFile]]
            pRow[12] = dlg.get_filename()
            pPixBuf = GdkPixbuf.Pixbuf().new_from_file(self.pListstore[self.m_lstSelection[self.m_nCurrentFile]][12])
            pRow[15] = pPixBuf.scale_simple((pPixBuf.get_width() * 24) / pPixBuf.get_height(), 24, GdkPixbuf.InterpType.HYPER)
            pPixBuf = pPixBuf.scale_simple((pPixBuf.get_width() * 100) / pPixBuf.get_height(), 100, GdkPixbuf.InterpType.HYPER)
            self.pImageCover.set_from_pixbuf(pPixBuf)
            g_pSettings.set_string('image-folder', os.path.dirname(pRow[12]))
            self.pCheckbuttonCover.set_active(self.checkSharedField(12, pRow[12]))

        dlg.destroy()

    def onButtonRenumberClicked(self, pButton):

        for nIndex in range(len(self.m_lstSelection)):

            if nIndex == self.m_nCurrentFile:
                self.pComboboxTrackNum.set_active(nIndex)

            self.pListstore[self.m_lstSelection[nIndex]][5] = '%.2i' %(nIndex + 1)

    def onEntryAlbumChanged(self, pEditable):

        self.stripPastedSpaces(pEditable)
        strText = self.pEntryAlbum.get_text()

        if self.pComboboxDiscNum.get_active() > -1 and self.pComboboxDiscTotal.get_active() > 0:
            self.pEntryFolder.set_text(os.path.join(TagDialog.ReplaceChars(self.pEntryAlbumArtist.get_text()), TagDialog.ReplaceChars(strText), 'Disc ' + self.pComboboxDiscNum.get_child().get_text()))
        else:
            self.pEntryFolder.set_text(os.path.join(TagDialog.ReplaceChars(self.pEntryAlbumArtist.get_text()), TagDialog.ReplaceChars(strText)))

        self.pCheckbuttonAlbum.set_active(self.checkSharedField(4, strText))
        self.pCheckbuttonFolder.set_active(self.checkSharedField(13, self.pEntryFolder.get_text()))

    def stripPastedSpaces(self, pEditable):

        if self.bClipboardPaste:

            sText = pEditable.get_text().strip(' ')
            sText = re.sub(r' +', ' ', sText)
            pEditable.set_text(sText)
            self.bClipboardPaste = False

    def onEntryGenreChanged(self, pEditable):

        self.stripPastedSpaces(pEditable)

    def onEntryTitleChanged(self, pEditable):

        if self.bClipboardPaste:

            self.stripPastedSpaces(pEditable)

            if g_pSettings.get_boolean('titlecase'):

                self.ConvertToTitleCase(None, pEditable)

        strText = self.pEntryTitle.get_text()
        self.pListstore[self.m_lstSelection[self.m_nCurrentFile]][7] = strText

    def onEntryPasteClipboard(self, pEditable):

        self.bClipboardPaste = True

    def onEntryAlbumArtistChanged(self, pEditable):

        self.stripPastedSpaces(pEditable)

        if self.pComboboxDiscNum.get_active() > -1 and self.pComboboxDiscTotal.get_active() > 0:
            self.pEntryFolder.set_text(os.path.join(TagDialog.ReplaceChars(self.pEntryAlbumArtist.get_text()), TagDialog.ReplaceChars(self.pEntryAlbum.get_text()), 'Disc ' + self.pComboboxDiscNum.get_child().get_text()))
        else:
            self.pEntryFolder.set_text(os.path.join(TagDialog.ReplaceChars(self.pEntryAlbumArtist.get_text()), TagDialog.ReplaceChars(self.pEntryAlbum.get_text())))

        self.pCheckbuttonAlbumArtist.set_active(self.checkSharedField(2, self.pEntryAlbumArtist.get_text()))
        self.pCheckbuttonFolder.set_active(self.checkSharedField(13, self.pEntryFolder.get_text()))

    def onEntryArtistChanged(self, pEditable):

        self.stripPastedSpaces(pEditable)
        self.pCheckbuttonArtist.set_active(self.checkSharedField(1, self.pEntryArtist.get_text()))

    def onComboboxTrackNumChanged(self, pCombobox):

        self.pListstore[self.m_lstSelection[self.m_nCurrentFile]][5] = self.pComboboxTrackNum.get_child().get_text()

    def onComboboxTrackTotalChanged(self, pCombobox):

        self.pCheckbuttonTracksTotal.set_active(self.checkSharedField(6, self.pComboboxTrackTotal.get_child().get_text()))

    def onComboboxDiscNumChanged(self, pCombobox):

        if self.pComboboxDiscNum.get_active() > -1 and self.pComboboxDiscTotal.get_active() > 0:
            self.pEntryFolder.set_text(os.path.join(TagDialog.ReplaceChars(self.pEntryAlbumArtist.get_text()), TagDialog.ReplaceChars(self.pEntryAlbum.get_text()), 'Disc ' + self.pComboboxDiscNum.get_child().get_text()))
        else:
            self.pEntryFolder.set_text(os.path.join(TagDialog.ReplaceChars(self.pEntryAlbumArtist.get_text()), TagDialog.ReplaceChars(self.pEntryAlbum.get_text())))

        self.pCheckbuttonDisc.set_active(self.checkSharedField(8, self.pComboboxDiscNum.get_child().get_text()))
        self.pCheckbuttonFolder.set_active(self.checkSharedField(13, self.pEntryFolder.get_text()))

    def onComboboxDiscTotalChanged(self, pCombobox):

        if self.pComboboxDiscNum.get_active() > -1 and self.pComboboxDiscTotal.get_active() > 0:
            self.pEntryFolder.set_text(os.path.join(TagDialog.ReplaceChars(self.pEntryAlbumArtist.get_text()), TagDialog.ReplaceChars(self.pEntryAlbum.get_text()), 'Disc ' + self.pComboboxDiscNum.get_child().get_text()))
        else:
            self.pEntryFolder.set_text(os.path.join(TagDialog.ReplaceChars(self.pEntryAlbumArtist.get_text()), TagDialog.ReplaceChars(self.pEntryAlbum.get_text())))

        self.pCheckbuttonDiscsTotal.set_active(self.checkSharedField(9, self.pComboboxDiscTotal.get_child().get_text()))
        self.pCheckbuttonFolder.set_active(self.checkSharedField(13, self.pEntryFolder.get_text()))

    def onEntryYearChanged(self, pEditable):

        self.stripPastedSpaces(pEditable)
        self.pCheckbuttonYear.set_active(self.checkSharedField(10, self.pEntryYear.get_text()))

    def onComboboxGenreChanged(self, pCombobox):

        strText = self.pComboboxGenre.get_child().get_text()
        self.pCheckbuttonGenre.set_active(self.checkSharedField(3, strText))

    def onEntryCommentChanged(self, pEditable):

        self.stripPastedSpaces(pEditable)
        self.pCheckbuttonComment.set_active(self.checkSharedField(11, pEditable.get_text()))

    def onEntryFolderChanged(self, pEditable):

        self.stripPastedSpaces(pEditable)
        self.pCheckbuttonFolder.set_active(self.checkSharedField(13, pEditable.get_text()))

    def onCheckbuttonAlbumArtistClicked(self, pButton, pEvent):

        pButton.set_active(True)

        for nIndex in self.m_lstSelection:
            self.pListstore[nIndex][2] = self.pEntryAlbumArtist.get_text()

        return True

    def onCheckbuttonArtistClicked(self, pButton, pEvent):

        pButton.set_active(True)

        for nIndex in self.m_lstSelection:
            self.pListstore[nIndex][1] = self.pEntryArtist.get_text()

        return True

    def onCheckbuttonTracksTotalClicked(self, pButton, pEvent):

        pButton.set_active(True)

        for nIndex in self.m_lstSelection:
            self.pListstore[nIndex][6] = self.pComboboxTrackTotal.get_child().get_text()

        return True

    def onCheckbuttonDiscsTotalClicked(self, pButton, pEvent):

        pButton.set_active(True)

        for nIndex in self.m_lstSelection:
            self.pListstore[nIndex][9] = self.pComboboxDiscTotal.get_child().get_text()

        return True

    def onCheckbuttonDiscClicked(self, pButton, pEvent):

        pButton.set_active(True)

        for nIndex in self.m_lstSelection:
            self.pListstore[nIndex][8] = self.pComboboxDiscNum.get_child().get_text()

        return True

    def onCheckbuttonGenreClicked(self, pButton, pEvent):

        pButton.set_active(True)

        for nIndex in self.m_lstSelection:
            self.pListstore[nIndex][3] = self.pComboboxGenre.get_child().get_text()

        return True

    def onCheckbuttonYearClicked(self, pButton, pEvent):

        pButton.set_active(True)

        for nIndex in self.m_lstSelection:
            self.pListstore[nIndex][10] = self.pEntryYear.get_text()

        return True

    def onCheckbuttonAlbumClicked(self, pButton, pEvent):

        pButton.set_active(True)

        for nIndex in self.m_lstSelection:
            self.pListstore[nIndex][4] = self.pEntryAlbum.get_text()

        return True

    def onCheckbuttonCommentClicked(self, pButton, pEvent):

        pButton.set_active(True)

        for nIndex in self.m_lstSelection:
            self.pListstore[nIndex][11] = self.pEntryComment.get_text()

        return True

    def onCheckbuttonCoverClicked(self, pButton, pEvent):

        pButton.set_active(True)

        for nIndex in self.m_lstSelection:

            self.pListstore[nIndex][12] = self.pListstore[self.m_lstSelection[self.m_nCurrentFile]][12]
            self.pListstore[nIndex][15] = self.pListstore[self.m_lstSelection[self.m_nCurrentFile]][15]

        return True

    def onCheckbuttonFolderClicked(self, pButton, pEvent):

        pButton.set_active(True)

        for nIndex in self.m_lstSelection:
            self.pListstore[nIndex][13] = self.pEntryFolder.get_text()

        return True

    def checkSharedField(self, nField, strText):

        bSame = True

        for nIndex in range(len(self.m_lstSelection)):

            if nIndex == self.m_nCurrentFile:

                self.pListstore[self.m_lstSelection[nIndex]][nField] = strText
                continue

            if self.pListstore[self.m_lstSelection[nIndex]][nField] != strText:
                bSame = False

        return bSame

    def onEntryPopulatePopup(self, pEntry, pMenu):

        pMenuItemCase = Gtk.ImageMenuItem(_('Convert to title case'))

        img = Gtk.Image()
        img.set_from_stock(Gtk.STOCK_SELECT_FONT, 1)

        pMenuItemCase.set_image(img)
        pMenuItemCase.connect("activate", self.ConvertToTitleCase, pEntry)
        pMenuItemCase.show()

        pMenu.insert(pMenuItemCase, 0)

        pMenuItemFromFile = Gtk.ImageMenuItem(_('Insert filename'))

        img = Gtk.Image()
        img.set_from_stock(Gtk.STOCK_FILE, 1)

        pMenuItemFromFile.set_image(img)
        pMenuItemFromFile.connect("activate", self.InsertFileName, pEntry)
        pMenuItemFromFile.show()

        pMenu.insert(pMenuItemFromFile, 1)

        pMenuItemSeparator = Gtk.SeparatorMenuItem()
        pMenuItemSeparator.show()

        pMenu.insert(pMenuItemSeparator, 2)

    def ConvertToTitleCase(self, pMenuItem, pEntry, strText=None):

        if pEntry != None:
            strText = pEntry.get_text()

        strText = re.sub(r'^\d+\. ', '', strText)
        strText = re.sub(r'^\d+ - ', '', strText)
        strText = re.sub(r'^\d+-', '', strText)
        strText = titlecase(strText)
        strText = strText.replace('’', '\'')
        strText = strText.replace('´', '\'')
        strText = strText.replace('[', '(')
        strText = strText.replace('&amp;', '&')
        strText = strText.replace(']', ')')
        strText = strText.replace('/*', '')
        strText = strText.replace('/#', '')
        strText = strText.replace('(#)', '')
        strText = strText.replace('(*)', '')
        strText = strText.replace('(#/*)', '')
        strText = strText.replace('()', '')
        strText = strText.replace("''", '"')
        strText = strText.replace(' (Alternate Take', ' (alternate take')
        strText = strText.replace(' (Alternative Take', ' (alternate take')
        strText = strText.replace(' (Master Take', ' (master take')
        strText = strText.replace(' (Complete Take', ' (complete take')
        strText = strText.replace(' (Retake ', ' (retake ')
        strText = strText.replace(' (Take ', ' (take ')
        strText = strText.replace(' (Vocal', ' (vocal')
        strText = strText.replace(' (False Start', ' (false start')
        strText = strText.replace(' (Insert', ' (insert')
        strText = strText.replace(' (Instr.', ' (instrumental')
        strText = strText.replace(' Version)', ' version)')
        strText = strText.strip()

        if pEntry != None:
            pEntry.set_text(strText)
        else:
            return strText

    def InsertFileName(self, pMenuItem, pEntry):

        strText = os.path.splitext(os.path.basename(self.pListstore[self.m_lstSelection[self.m_nCurrentFile]][0]))[0]

        pEntry.set_text(strText)

        if g_pSettings.get_boolean('titlecase'):

            self.ConvertToTitleCase(None, pEntry)

    def displayFileTag(self):

        nRow = self.pListstore[self.m_lstSelection[self.m_nCurrentFile]]
        self.pEntryAlbumArtist.set_text(nRow[2])
        self.pEntryArtist.set_text(nRow[1])
        self.pEntryTitle.set_text(nRow[7])
        self.pComboboxGenre.get_child().set_text(nRow[3])
        self.pEntryAlbum.set_text(nRow[4])
        self.pComboboxTrackNum.set_active(int(nRow[5]) - 1)
        self.pComboboxTrackTotal.set_active(int(nRow[6]) - 1)
        self.pComboboxDiscNum.set_active(int(nRow[8]) - 1)
        self.pComboboxDiscTotal.set_active(int(nRow[9]) - 1)
        self.pEntryYear.set_text(nRow[10])
        self.pEntryComment.set_text(nRow[11])

        pPixBuf = None

        if len(nRow[12]):

            pPixBuf = GdkPixbuf.Pixbuf().new_from_file(nRow[12])
            pPixBuf = pPixBuf.scale_simple((pPixBuf.get_width() * 100) / pPixBuf.get_height(), 100, GdkPixbuf.InterpType.HYPER)

        else:

            pPixBuf = Gtk.IconTheme().get_default().load_icon('gtk-missing-image', 100, Gtk.IconLookupFlags.FORCE_SVG | Gtk.IconLookupFlags.FORCE_SIZE)

        self.pImageCover.set_from_pixbuf(pPixBuf)
        self.pCheckbuttonCover.set_active(self.checkSharedField(12, nRow[12]))
