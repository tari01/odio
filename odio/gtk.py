#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gio, Gtk, GdkPixbuf
import logging
#import types
import psutil
import os
import sys
import gettext
import pipes
from .appdata import *

def idle():

    while Gtk.events_pending():

        Gtk.main_iteration()

def getClassVar(sId):

    return 'p' + sId[0:1].upper() + sId[1:]

def quote(sText):

    if len(sText) == 0:

        return "''"

    else:

        return pipes.quote(sText)

def getDataPath(sPath):

    try:

        sExecPath = os.path.split(APPEXECUTABLE)[0]
        sDataPath = os.getcwd().replace(sExecPath, '')
        sRelativePath = os.path.join(sDataPath, sPath.lstrip('/'))

        if os.path.exists(sRelativePath):

            return sRelativePath

    except:

        pass

    return sPath

try:
    g_pTranslation = gettext.translation(APPNAME)
except IOError:
    g_pTranslation = gettext.NullTranslations()

class Formatter(logging.Formatter):

    def __init__(self):

        logging.Formatter.__init__(self, '[%(asctime)s] %(levelname)s: %(message)s')
        self.default_msec_format = '%s.%03d'

    def format(self, record):

        dColours = {'WARNING': '33', 'INFO': '32', 'DEBUG': '37', 'CRITICAL': '35', 'ERROR': '31'}
        record.levelname = '\033[1;' + dColours[record.levelname] + 'm' + record.levelname + '\033[0m'

        return logging.Formatter.format(self, record)

logger = logging.getLogger(APPNAME)
logger.setLevel(logging.DEBUG)
pStreamHandler = logging.StreamHandler()
pStreamHandler.setFormatter(Formatter())
logger.addHandler(pStreamHandler)

g_pTranslation.install()
g_pSettings = Gio.Settings.new('in.tari.' + APPNAME)
g_pWindow = None

class Application:

    pStatusBarLabel = None

    def __init__(self, bMinimiseToTray):

        global g_pWindow

        self.bMinimiseToTray = bMinimiseToTray

        for pProc in psutil.process_iter():

            sName = pProc.name

            if not isinstance(sName, str):

               sName = pProc.name()

            if sName == 'python3' or sName == 'python':

                lCmdLine = pProc.cmdline

                if not isinstance(lCmdLine, list):

                   lCmdLine = pProc.cmdline()

                for sCmd in lCmdLine:

                    if sCmd.endswith(APPNAME) and pProc.pid != os.getpid():

                        sys.exit(1)

            elif sName.endswith(APPNAME) and pProc.pid != os.getpid():

                sys.exit(1)

        if hasattr(self, 'preinit'):

            self.preinit()

        pBuilder = Gtk.Builder()
        pBuilder.set_translation_domain(APPNAME)
        pBuilder.add_from_file(getDataPath('/usr/share/' + APPNAME + '/' + APPNAME + '.glade'))
        pBuilder.connect_signals(self)

        for pObject in pBuilder.get_objects():

            try:

                self.__dict__[getClassVar(Gtk.Buildable.get_name(pObject))] = pObject

            except:

                pass

        if hasattr(self, 'pWindow'):

            self.pToolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
            self.pWindow.set_icon_from_file(getDataPath('/usr/share/icons/hicolor/scalable/apps/' + APPNAME + '.svg'))

            sTitle = APPTITLE

            if APPDEBUG:

                sTitle += ' - DEBUGGING MODE'

            self.pWindow.set_title(sTitle)
            g_pWindow = self.pWindow
            self.pStatusBarLabel = self.pStatusBar.get_message_area().get_children()[0]

            if '--hide' in sys.argv and self.bMinimiseToTray:

                self.pWindow.hide()

            else:

                self.pWindow.show_all()

        if hasattr(self, 'postinit'):

            self.postinit()

        Gtk.main()

    def onWindowDestroy(self, pWidget, pData = None):

        Gtk.main_quit()

    def onAboutClicked(self, pWidget, pData = None):

        pAboutdialog = Gtk.AboutDialog()
        pAboutdialog.set_transient_for(g_pWindow)
        pAboutdialog.set_title(_('About {application}').format(application=APPTITLE))
        pAboutdialog.set_license_type(Gtk.License.GPL_3_0)
        pAboutdialog.set_program_name(APPTITLE)
        pAboutdialog.set_copyright(APPAUTHOR + ' ' + (APPYEAR if APPYEAR[-2:] == APPVERSION[:2] else APPYEAR + '-20' + APPVERSION[:2]))
        pAboutdialog.set_comments(_(APPDESCRIPTION))
        pAboutdialog.set_authors([APPAUTHOR + ' &lt;' + APPMAIL + '&gt;'])
        pAboutdialog.set_translator_credits(_('translator-credits'))
        pAboutdialog.set_version(APPVERSION)
        pAboutdialog.set_website(APPURL)
        pAboutdialog.set_website_label(APPURL)
        pAboutdialog.set_logo(GdkPixbuf.Pixbuf().new_from_file(getDataPath('/usr/share/icons/hicolor/scalable/apps/' + APPNAME + '.svg')))
        pAboutdialog.run()
        pAboutdialog.destroy()

    def onWindowDeleteEvent(self, pWidget, pEvent, pData = None):

        return False

class Indicator(Application):

    def __init__(self):

        gi.require_version('AppIndicator3', '0.1')

        from gi.repository import AppIndicator3

        if APPDEBUG:

            self.pIndicator = AppIndicator3.Indicator.new_with_path(APPNAME, APPNAME + '-active', AppIndicator3.IndicatorCategory.APPLICATION_STATUS, getDataPath('/usr/share/icons/ubuntu-mono-dark/status/24'))

        else:

            self.pIndicator = AppIndicator3.Indicator.new(APPNAME, APPNAME + '-active', AppIndicator3.IndicatorCategory.APPLICATION_STATUS)

        Application.__init__(self, False, False)

    def postinit(self):

        self.pIndicator.set_attention_icon(APPNAME + '-attention')
        self.pIndicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.pIndicator.set_menu(self.pMenu)

class Dialog():

    nResponseId = Gtk.ResponseType.CANCEL

    def __init__(self, pParent, pData):

        global g_pWindow

        if hasattr(self, 'preinit'):

            self.preinit(pData)

        strFile = getDataPath('/usr/share/' + APPNAME + '/' + self.__class__.__module__.split('.')[-1].split('/')[-1] + '.glade')

        pBuilder = Gtk.Builder()
        pBuilder.set_translation_domain(APPNAME)
        pBuilder.add_from_file(strFile)
        pBuilder.connect_signals(self)

        for pObject in pBuilder.get_objects():

            if isinstance(pObject, Gtk.Buildable):

                self.__dict__[getClassVar(Gtk.Buildable.get_name(pObject))] = pObject

                """
                if isinstance(pObject, Gtk.Notebook):

                    def getPageSensitive(pWidget, nPage):

                         return pWidget.get_tab_label(pWidget.get_nth_page(nPage)).get_sensitive()

                    def setPageSensitive(pWidget, nPage, bSensitive):

                         return pWidget.get_tab_label(pWidget.get_nth_page(nPage)).set_sensitive(bSensitive)

                    def onNotebookPageSelected(pWidget, pEvent):

                        nMouseX, nMouseY = pEvent.get_coords()

                        for nPage in range(0, pWidget.get_n_pages()):

                            pLabel = pWidget.get_tab_label(pWidget.get_nth_page(nPage))
                            nX, nY = pLabel.translate_coordinates(pWidget, 0, 0)
                            rcSize = pLabel.get_allocation()

                            if nMouseX >= nX and nMouseY >= nY and nMouseX <= nX + rcSize.width and nMouseY <= nY + rcSize.height and pWidget.getPageSensitive(nPage):

                                return False

                        return True

                    pObject.connect('button-press-event', onNotebookPageSelected)
                    pObject.getPageSensitive = types.MethodType(getPageSensitive, pObject)
                    pObject.setPageSensitive = types.MethodType(setPageSensitive, pObject)
                """

        self.pDialog.set_transient_for(pParent if pParent else g_pWindow)
        self.pDialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.pDialog.set_skip_pager_hint(True)
        self.pDialog.set_skip_taskbar_hint(True)
        self.pDialog.set_destroy_with_parent(True)

        if hasattr(self, 'postinit'):

            self.postinit(pData)

        if self.pDialog.run() != -1:

            self.pDialog.destroy()
