#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ctypes
import threading
import time

class SACD:

    lSacdProgress = [0.0]
    pThread = None
    pOnProgress = None
    lErrors = [False, False]
    sFilePath = ''
    sOutDir = ''
    oLibOdioSacd = ctypes.cdll.LoadLibrary('/usr/lib/libodiosacd.so')
    nSacdTracks = 0
    sWarning = ''

    def convert(self, lErrors):

        lErrors[1] = self.oLibOdioSacd.odiolibsacd_Convert(str.encode(self.sOutDir), 88200, self.pOnProgress, None)

    def onProgress(self, fProgress, sFilePath, nTrack, pUserData = None):

        if sFilePath:

            sFilePath = sFilePath.decode()

        self.lSacdProgress[0] = fProgress / 100
        bContinue = self.pProgress(self.lSacdProgress[0], sFilePath, nTrack, self.nSacdTracks)

        return bContinue

    def __init__(self, sFilePath, sOutDir, pProgress):

        AREA_TWOCH = 1
        AREA_MULCH = 2
        AREA_AUTO = 3
        self.sFilePath = sFilePath
        self.sOutDir = sOutDir
        self.pProgress = pProgress
        OnProgress = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_float, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
        self.pOnProgress = OnProgress(self.onProgress)
        self.lErrors[0] = self.oLibOdioSacd.odiolibsacd_Open(str.encode(sFilePath), AREA_AUTO)

        if not self.lErrors[0]:

            self.nSacdTracks = self.oLibOdioSacd.odiolibsacd_GetTrackCount(AREA_AUTO)
            nTwoCh = self.oLibOdioSacd.odiolibsacd_GetTrackCount(AREA_TWOCH)
            nMulCh = self.oLibOdioSacd.odiolibsacd_GetTrackCount(AREA_MULCH)

            if nTwoCh > 0 and nMulCh > 0 and nTwoCh != nMulCh:

                self.sWarning = _('The SACD multichannel and stereo areas had a different track count: extracted both.')

            self.pThread = threading.Thread(target=self.convert, args=(self.lErrors,))

    def start(self):

        self.pThread.start()

    def getWarning(self):

        return self.sWarning

    def isOpen(self):

        return not self.lErrors[0]

    def working(self):

        return self.lSacdProgress[0] < 0.99

    def poll(self):

        time.sleep(0.04)

    def close(self):

        sResult = _('Ready')

        if not self.lErrors[0]:

            self.pThread.join()

            if (self.lErrors[1]):

                sResult = _('Failed to decode {filepath}').format(filepath=self.sFilePath)

            else:

                self.oLibOdioSacd.odiolibsacd_Close()

        return sResult
