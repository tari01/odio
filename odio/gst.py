#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstAudio', '1.0')
gi.require_version('GstTag', '1.0')
gi.require_version('Gtk', '3.0')

from gi.repository import Gst, GstAudio, GstTag, GLib, GObject, Gtk
from odio.gtk import logger, idle
from enum import IntEnum
from mutagen.mp4 import MP4
import filecmp
import os
import os.path
import time
import uuid
import shutil
import subprocess
import re

Gst.init(None)

def escape(sFileName):

    return sFileName.replace('"', '\\"')

class GstState(IntEnum):

    IDLE = 0
    RUNNING = 1
    DONE = 2

LAYOUTS = {}
LAYOUTS['1.0'] = [GstAudio.AudioChannelPosition.FRONT_CENTER]
LAYOUTS['2.0'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT]
LAYOUTS['2.1'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.LFE1]
LAYOUTS['3.0'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER]
LAYOUTS['3.0(back)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.REAR_CENTER]
LAYOUTS['4.0'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.REAR_CENTER]
LAYOUTS['quad'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT]
LAYOUTS['quad(side)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]
LAYOUTS['3.1'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1]
LAYOUTS['3.1(back)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.REAR_CENTER]
LAYOUTS['5.0'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT]
LAYOUTS['5.0(alsa)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER]
LAYOUTS['5.0(side)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]
LAYOUTS['4.1'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.REAR_CENTER]
LAYOUTS['4.1(alsa)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.LFE1]
LAYOUTS['5.1'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT]
LAYOUTS['5.1(alsa)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1]
LAYOUTS['5.1(side)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]
LAYOUTS['6.0'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.REAR_CENTER, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]
LAYOUTS['6.0(front)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_LEFT_OF_CENTER, GstAudio.AudioChannelPosition.FRONT_RIGHT_OF_CENTER, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]
LAYOUTS['hexagonal'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.REAR_CENTER]
LAYOUTS['6.1'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.REAR_CENTER, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]
LAYOUTS['6.1(back)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.REAR_CENTER]
LAYOUTS['6.1(top)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.TOP_CENTER]
LAYOUTS['6.1(front)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.FRONT_LEFT_OF_CENTER, GstAudio.AudioChannelPosition.FRONT_RIGHT_OF_CENTER, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]
LAYOUTS['7.0'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]
LAYOUTS['7.0(front)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.FRONT_LEFT_OF_CENTER, GstAudio.AudioChannelPosition.FRONT_RIGHT_OF_CENTER, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]
LAYOUTS['7.0(rear)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.SURROUND_LEFT, GstAudio.AudioChannelPosition.SURROUND_RIGHT]
LAYOUTS['7.1'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]
LAYOUTS['7.1(alsa)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]
LAYOUTS['7.1(wide)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.FRONT_LEFT_OF_CENTER, GstAudio.AudioChannelPosition.FRONT_RIGHT_OF_CENTER]
LAYOUTS['7.1(wide-side)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.FRONT_LEFT_OF_CENTER, GstAudio.AudioChannelPosition.FRONT_RIGHT_OF_CENTER, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]
LAYOUTS['7.1(rear)'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.LFE1, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.SURROUND_LEFT, GstAudio.AudioChannelPosition.SURROUND_RIGHT]
LAYOUTS['octagonal'] = [GstAudio.AudioChannelPosition.FRONT_LEFT, GstAudio.AudioChannelPosition.FRONT_RIGHT, GstAudio.AudioChannelPosition.FRONT_CENTER, GstAudio.AudioChannelPosition.REAR_LEFT, GstAudio.AudioChannelPosition.REAR_RIGHT, GstAudio.AudioChannelPosition.REAR_CENTER, GstAudio.AudioChannelPosition.SIDE_LEFT, GstAudio.AudioChannelPosition.SIDE_RIGHT]

class GstBase:

    def __init__(self):

        self.pPipeline = None
        self.lSignals = []
        self.lSignalsConnected = []
        self.nOperations = 0
        self.nState = GstState.IDLE
        self.sOperation = ''

    def init(self, sCommand, dTags):

        if self.pPipeline is None:

            self.pPipeline = Gst.parse_launch(sCommand)
            pBus = self.pPipeline.get_bus()
            pBus.add_signal_watch();

            for sName, sSignal, pCallback in self.lSignals:

                pElement = pBus

                if sName:

                    pElement = self.pPipeline.get_by_name(sName)

                nId = pElement.connect(sSignal, pCallback)
                self.lSignalsConnected.append([pElement, nId])

            nId = pBus.connect('message::error', self.onError)
            self.lSignalsConnected.append([pBus, nId])
            nId = pBus.connect('message::eos', self.onEos)
            self.lSignalsConnected.append([pBus, nId])

            if dTags:

                pEnc = self.pPipeline.get_by_name('enc')

                for sName, pValue in dTags.items():

                    pEnc.add_tag_value(Gst.TagMergeMode.REPLACE_ALL, sName, pValue)

        self.pPipeline.set_state(Gst.State.PAUSED)
        self.pPipeline.get_state(Gst.CLOCK_TIME_NONE)

    def play(self):

        self.pPipeline.set_state(Gst.State.PLAYING)

    def onError(self, pBus, pMessage):

        pError = pMessage.parse_error()
        logger.error(pError.gerror.message + ' ' + pError.debug)

        return True

    def onEos(self, pElement, pMessage):

        self.close()

    def seek(self, nStart, nEnd, bAccurate):

        nFlags = Gst.SeekFlags.KEY_UNIT

        if bAccurate:

            nFlags = Gst.SeekFlags.ACCURATE

        self.pPipeline.seek(1.0, Gst.Format.TIME, nFlags | Gst.SeekFlags.FLUSH, Gst.SeekType.SET, nStart, Gst.SeekType.SET, nEnd or self.nDuration)
        self.pPipeline.get_state(Gst.CLOCK_TIME_NONE)

    def getPosition(self):

        fProgress = 0.0

        if self.nState == GstState.DONE:

            fProgress = 1.0

        elif self.pPipeline:

            fProgress = (self.nOperation / self.nOperations) + (self.pPipeline.query_position(Gst.Format.TIME)[1] / self.nDuration / self.nOperations)

            if fProgress > (self.nOperation + 1) / self.nOperations:

                fProgress = (self.nOperation + 1) / self.nOperations

            elif fProgress < (self.nOperation / self.nOperations):

                fProgress = self.nOperation / self.nOperations

        return fProgress

    def close(self):

        if self.pPipeline:

            self.pPipeline.set_state(Gst.State.NULL)
            self.pPipeline.get_state(Gst.CLOCK_TIME_NONE)

            for pElement, nId in self.lSignalsConnected:

                pElement.disconnect(nId)

            pBus = self.pPipeline.get_bus()
            pBus.remove_signal_watch()
            self.lSignalsConnected = []
            self.lSignals = []
            self.pPipeline = None

class GstReader(GstBase):

    def __init__(self):

        super().__init__()

    def run(self, sPath, bRemoveSilent, bRemoveLfe, bSaturate, bCheckStereo, sTempDir, pCallback, pParam):

        self.nState = GstState.RUNNING
        self.pOrigCaps = None
        self.pAudioInfo = None
        self.lMapping = []
        self.pCallback = pCallback
        self.pParam = pParam
        self.sPath = sPath
        self.bRemoveSilent = bRemoveSilent
        self.bRemoveLfe = bRemoveLfe
        self.bSaturate = bSaturate
        self.bCheckStereo = bCheckStereo
        self.sTempDir = sTempDir
        self.dAudioInfo = {}
        self.dAudioInfo['start'] = None
        self.dAudioInfo['end'] = None
        self.dAudioInfo['file'] = self.sPath
        self.dAudioInfo['changed'] = False

        self.lSignals.append([None, 'message::element', self.onElement])

        sRemoveSilent = ''

        if self.bRemoveSilent:

            sRemoveSilent = ' ! level interval=1000000000 '

        self.nOperation = 0
        self.sOperation = 'check-silence'
        self.init('filesrc location="' + escape(self.sPath) + '" ! decodebin ! audioconvert name=aconv ! cutter threshold-dB=-60 pre-length=100000000 run-length=100000000' + sRemoveSilent + ' ! audio/x-raw ! fakesink', None)
        pAudioConvert = self.pPipeline.get_by_name('aconv')
        pPad = pAudioConvert.get_static_pad('sink')
        self.pOrigCaps = pPad.get_current_caps()
        self.pAudioInfo = GstAudio.AudioInfo.new_from_caps(self.pOrigCaps)
        self.pAudioInfo.layout = GstAudio.AudioLayout.INTERLEAVED
        self.lMapping = [not self.bRemoveSilent] * self.pAudioInfo.channels
        self.nDuration = self.pPipeline.query_duration(Gst.Format.TIME)[1]
        self.nOperations = 2 + int(self.bCheckStereo and self.pAudioInfo.channels == 2)
        self.dAudioInfo['duration'] = self.nDuration
        self.play()

    def onEos(self, pElement, pMessage):

        super().onEos(pElement, pMessage)

        if self.sOperation == 'check-silence':

            self.nChannelsNew = self.pAudioInfo.channels
            self.sLayout = ''
            self.dAudioInfo['matrix'] = [list] * self.pAudioInfo.channels

            for nChannel in range(self.pAudioInfo.channels):

                self.dAudioInfo['matrix'][nChannel] = [0.0] * self.pAudioInfo.channels
                self.dAudioInfo['matrix'][nChannel][nChannel] = 1.0

            self.lOrigMatrix = list(self.dAudioInfo['matrix'])

            try:

                self.sLayout = list(LAYOUTS.keys())[list(LAYOUTS.values()).index(self.pAudioInfo.position[0 : self.pAudioInfo.channels])]

            except:

                self.sLayout = ['1.0', '2.0', '3.0', 'quad', '5.0', '5.1', '6.1', '7.1'][self.pAudioInfo.channels - 1]

            if self.sLayout == '2.1':

                self.sLayout = '2.0'
                self.nChannelsNew = 2
                self.removeChannel(2)

            elif self.sLayout == '3.0(back)':

                self.sLayout = '3.0'

            elif self.sLayout == '4.0':

                self.sLayout = 'quad'

            elif self.sLayout == 'quad(side)':

                self.sLayout = 'quad'

            elif self.sLayout == '3.1':

                self.sLayout = '3.0'
                self.nChannelsNew = 3
                self.removeChannel(3)

            elif self.sLayout == '3.1(back)':

                self.sLayout = '3.0'
                self.nChannelsNew = 3
                self.removeChannel(2)

            elif self.sLayout == '5.0(alsa)':

                self.sLayout = '5.0'
                self.reorderChannels(0, 1, 4, 2, 3)

            elif self.sLayout == '5.0(side)':

                self.sLayout = '5.0'

            elif self.sLayout == '4.1':

                self.sLayout = 'quad'
                self.nChannelsNew = 4
                self.removeChannel(3)

            elif self.sLayout == '4.1(alsa)':

                self.sLayout = 'quad'
                self.nChannelsNew = 4
                self.removeChannel(4)

            elif self.sLayout == '5.1(alsa)':

                self.sLayout = '5.1'
                self.reorderChannels(0, 1, 4, 5, 2, 3)

            elif self.sLayout == '5.1(side)':

                self.sLayout = '5.1'

            elif self.sLayout == '6.0':

                self.sLayout = '5.0'
                self.nChannelsNew = 5
                self.removeChannel(3)

            elif self.sLayout == '6.0(front)':

                self.sLayout = '5.0'
                self.nChannelsNew = 5
                self.removeChannel(3)

            elif self.sLayout == 'hexagonal':

                self.sLayout = '5.0'
                self.nChannelsNew = 5
                self.removeChannel(5)

            elif self.sLayout == '6.1(back)':

                self.sLayout = '6.1'
                self.reorderChannels(0, 1, 2, 3, 6, 4, 5)

            elif self.sLayout == '6.1(top)':

                self.sLayout = '6.1'
                self.reorderChannels(0, 1, 2, 3, 6, 4, 5)

            elif self.sLayout == '6.1(front)':

                self.sLayout = '6.1'
                self.reorderChannels(0, 1, 3, 2, 4, 5, 6)

            elif self.sLayout == '7.0(front)':

                self.sLayout = '7.0'

            elif self.sLayout == '7.0(rear)':

                self.sLayout = '7.0'

            elif self.sLayout == '7.1(alsa)':

                self.sLayout = '7.1'
                self.reorderChannels(0, 1, 4, 5, 2, 3, 6, 7)

            elif self.sLayout == '7.1(wide)':

                self.sLayout = '7.1'

            elif self.sLayout == '7.1(wide-side)':

                self.sLayout = '7.1'

            elif self.sLayout == '7.1(rear)':

                self.sLayout = '7.1'

            elif self.sLayout == 'octagonal':

                self.sLayout = '7.0'
                self.removeChannel(5)

            if not all(self.lMapping):

                for nIndex, bHasSound in reversed(list(enumerate(self.lMapping))):

                    if not bHasSound:

                        if self.sLayout == '2.0':

                            self.sLayout = '1.0'

                        elif self.sLayout == '3.0':

                            self.sLayout = '2.0'

                        elif self.sLayout == 'quad':

                            self.sLayout = '3.0'

                        elif self.sLayout == '5.0':

                            self.sLayout = 'quad'

                        elif self.sLayout == '5.1' and nIndex == 3:

                            self.sLayout = '5.0'

                        elif self.sLayout == '6.1' and nIndex == 3:

                            self.sLayout = '5.1'

                        elif self.sLayout == '7.1' and nIndex == 3:

                            continue

                        else:

                            continue

                        self.removeChannel(nIndex)
                        self.nChannelsNew -= 1

            if self.bRemoveLfe and self.sLayout in ['5.1', '6.1', '7.1']:

                if self.sLayout == '5.1':

                    self.sLayout = '5.0'
                    self.removeChannel(3)
                    self.nChannelsNew -= 1

                elif self.sLayout == '6.1':

                    self.silenceChannel(3)

                elif self.sLayout == '7.1':

                    self.silenceChannel(3)

            if self.bSaturate:

                if self.sLayout == '3.0':

                    self.insertChannel(3, None)
                    self.insertChannel(4, 0)
                    self.insertChannel(5, 1)
                    self.sLayout = '5.1'
                    self.nChannelsNew = 6

                elif self.sLayout == '5.0':

                    self.insertChannel(3, None)
                    self.sLayout = '5.1'
                    self.nChannelsNew = 6

                elif self.sLayout == '6.1':

                    self.insertChannel(5, 4)
                    self.sLayout = '7.1'
                    self.nChannelsNew = 8

            if self.bCheckStereo and self.sLayout == '2.0':

                self.sLeft = os.path.join(self.sTempDir, str(uuid.uuid4().hex))
                self.sRight = os.path.join(self.sTempDir, str(uuid.uuid4().hex))
                self.nOperation = 1
                self.sOperation = 'check-stereo'
                self.init('filesrc location="' + escape(self.sPath) + '" ! decodebin ! audioconvert ! audio/x-raw ! deinterleave name=d d.src_0 ! queue ! filesink location="' + escape(self.sLeft) + '" d.src_1 ! queue ! filesink location="' + escape(self.sRight) + '"', None)
                self.play()

            else:

                self.decode()

        elif self.sOperation == 'check-stereo':

            if filecmp.cmp(self.sLeft, self.sRight, shallow=False):

                self.removeChannel(1)
                self.sLayout = '1.0'
                self.nChannelsNew = 1

            os.remove(self.sLeft)
            os.remove(self.sRight)
            self.decode()

        elif self.sOperation == 'decode':

            if self.sMoveDecoded:

                shutil.move(self.sMoveDecoded + '.tmp.wav', self.sMoveDecoded + '.wav')

            # Fix the AudioFormat to PCM

            if self.sLayout in ['quad', '5.0', '7.1']:

                with open(self.dAudioInfo['file'], 'r+b') as pFile:

                    pFile.seek(20)
                    pFile.write(b'\x01\x00')

            self.nState = GstState.DONE

            GLib.idle_add(self.pCallback, self.pParam, self.dAudioInfo)

    def reorderChannels(self, *lOrder):

        self.dAudioInfo['matrix'] = [list] * len(lOrder)

        for nChannel, nPosition in enumerate(lOrder):

            self.dAudioInfo['matrix'][nChannel] = [0.0] * len(lOrder)
            self.dAudioInfo['matrix'][nChannel][nPosition] = 1.0

    def removeChannel(self, nChannel):

        del self.dAudioInfo['matrix'][nChannel]

    def silenceChannel(self, nChannel):

        self.dAudioInfo['matrix'][nChannel] = [0.0] * self.pAudioInfo.channels

    def insertChannel(self, nPositon, nSource):

        self.dAudioInfo['matrix'].insert(nPositon, [0.0] * self.pAudioInfo.channels)

        if nSource is not None:

            self.dAudioInfo['matrix'][nPositon][nSource] = 1.0

    def decode(self):

        nAudioFormat = self.pAudioInfo.finfo.format
        nRate = self.pAudioInfo.rate

        if self.pAudioInfo.finfo.format in [GstAudio.AudioFormat.UNKNOWN, GstAudio.AudioFormat.ENCODED, GstAudio.AudioFormat.S16BE, GstAudio.AudioFormat.U16LE, GstAudio.AudioFormat.U16BE, GstAudio.AudioFormat.S16]:

            nAudioFormat = GstAudio.AudioFormat.S16LE

        elif self.pAudioInfo.finfo.format in [GstAudio.AudioFormat.F64LE, GstAudio.AudioFormat.F64BE, GstAudio.AudioFormat.F32BE, GstAudio.AudioFormat.F32, GstAudio.AudioFormat.S32BE, GstAudio.AudioFormat.U32LE, GstAudio.AudioFormat.U32BE, GstAudio.AudioFormat.S32]:

            if self.pAudioInfo.finfo.format == GstAudio.AudioFormat.F32LE:

                if self.pAudioInfo.rate == 352800:

                    nAudioFormat = GstAudio.AudioFormat.S24LE
                    nRate = 88200

                elif self.pAudioInfo.rate == 44100:

                    nAudioFormat = GstAudio.AudioFormat.S16LE

                else:

                    nAudioFormat = GstAudio.AudioFormat.S24LE

            else:

                nAudioFormat = GstAudio.AudioFormat.S32LE

        elif self.pAudioInfo.finfo.format in [GstAudio.AudioFormat.S24_32LE, GstAudio.AudioFormat.S24_32BE, GstAudio.AudioFormat.U24_32LE, GstAudio.AudioFormat.U24_32BE, GstAudio.AudioFormat.S24BE, GstAudio.AudioFormat.U24LE, GstAudio.AudioFormat.U24BE, GstAudio.AudioFormat.S20LE, GstAudio.AudioFormat.S20BE, GstAudio.AudioFormat.U20LE, GstAudio.AudioFormat.U20BE, GstAudio.AudioFormat.S18LE, GstAudio.AudioFormat.S18BE, GstAudio.AudioFormat.U18LE, GstAudio.AudioFormat.U18BE, GstAudio.AudioFormat.S24]:

            nAudioFormat = GstAudio.AudioFormat.S24LE

        lAudioChannelPositionNew = LAYOUTS[self.sLayout] + [GstAudio.AudioChannelPosition.INVALID] * (64 - self.nChannelsNew)

        if nAudioFormat != self.pAudioInfo.finfo.format or lAudioChannelPositionNew != self.pAudioInfo.position or self.nChannelsNew != self.pAudioInfo.channels:

            self.pAudioInfo.set_format(nAudioFormat, nRate, self.nChannelsNew, lAudioChannelPositionNew)

        self.dAudioInfo['bps'] = self.pAudioInfo.finfo.width
        self.dAudioInfo['channels'] = self.pAudioInfo.channels
        self.dAudioInfo['rate'] = self.pAudioInfo.rate
        self.dAudioInfo['caps'] = self.pAudioInfo.to_caps().to_string()

        if (self.dAudioInfo['start'] is not None) or (self.dAudioInfo['end'] is not None) or (self.lOrigMatrix != self.dAudioInfo['matrix']) or (not all(self.lMapping)) or (not self.pOrigCaps.is_equal(self.pAudioInfo.to_caps())):

            self.dAudioInfo['changed'] = True

        self.dAudioInfo['duration'] = (self.dAudioInfo['end'] or self.dAudioInfo['duration']) - (self.dAudioInfo['start'] or 0)
        sPathIn = self.dAudioInfo['file']
        sPathOut = ''
        self.sMoveDecoded = ''

        if self.dAudioInfo['changed'] or (not self.dAudioInfo['file'].startswith('/tmp/odio/')) or ('odio-tmp' not in self.dAudioInfo['file']):

            self.sTempDir = self.sTempDir or os.path.dirname(self.sPath)
            strPathBase, sExt = os.path.splitext(self.sPath)
            strDestPathBase = os.path.join(self.sTempDir, os.path.basename(strPathBase))

            os.makedirs(self.sTempDir, exist_ok=True)

            if self.dAudioInfo['file'] == strDestPathBase + '.wav':

                if self.dAudioInfo['changed']:

                    sPathOut = strDestPathBase + '.tmp.wav'
                    self.sMoveDecoded = strDestPathBase

            else:

                self.dAudioInfo['file'] = strDestPathBase + '.wav'

                if self.dAudioInfo['changed'] or sExt != '.wav':

                    sPathOut = strDestPathBase + '.wav'

        if sPathOut:

            sMatrix = ''

            for lChannel in self.dAudioInfo['matrix']:

                if sMatrix:

                    sMatrix += ', '

                sMatrix += '<(float)' + ', (float)'.join(map(str, lChannel)) + '>'

            self.nOperation = self.nOperations - 1
            self.sOperation = 'decode'
            self.init('filesrc location="' + escape(sPathIn) + '" ! decodebin ! audioconvert mix-matrix="<' + sMatrix + '>" ! ' + self.dAudioInfo['caps'] + ' ! wavenc ! filesink location="' + escape(sPathOut) + '"', None)
            self.seek(self.dAudioInfo['start'] or 0, self.dAudioInfo['end'] or self.dAudioInfo['duration'], True)
            self.play()

        else:

            self.nState = GstState.DONE

            GLib.idle_add(self.pCallback, self.pParam, self.dAudioInfo)

    def onElement(self, pElement, pMessage):

        pStructure = pMessage.get_structure()

        if pStructure.get_name() == 'cutter':

            nTime = pStructure.get_value('timestamp')
            bEnd = pStructure.get_value('above')

            if bEnd:

                self.dAudioInfo['end'] = None

                if self.dAudioInfo['start'] is None:

                    self.dAudioInfo['start'] = nTime

            else:

                self.dAudioInfo['end'] = nTime

        elif pStructure.get_name() == 'level':

            lRms = pStructure.get_value('rms')

            for nChannel, fRms in enumerate(lRms):

                if fRms >= -60:

                    self.lMapping[nChannel] = True

class GstPlayer(GstBase):

    def __init__(self, sUri, pOnEos, nDuration):

        super().__init__()

        self.nDuration = nDuration
        self.pOnEos = pOnEos
        self.init('playbin uri="' + escape(sUri) + '" volume=1.0', None)
        self.play()

    def onEos(self, pElement, pMessage):

        super().onEos(pElement, pMessage)

        self.pOnEos(True)

    def getPosition(self):

        if not self.pPipeline:

            return 0

        return max(-1, self.pPipeline.query_position(Gst.Format.TIME)[1])

class GstEncoder(GstBase):

    def __init__(self):

        super().__init__()

    def run(self, sEncoder, sPathIn, sPathTmp, sPathOut, nBps, nRate, nChannels, nDuration, dTags, pCallback, pParam):

        self.nState = GstState.RUNNING
        self.pCallback = pCallback
        self.pParam = pParam
        self.sOperation = 'replay-gain'
        self.nOperations = 2
        self.nOperation = 0
        self.dTags = dTags
        self.dTags['replaygain-track-peak'] = None
        self.dTags['replaygain-track-gain'] = None
        self.sPathIn = sPathIn
        self.sPathTmp = sPathTmp
        self.sPathOut = sPathOut
        self.nDuration = nDuration
        self.sEncoder = sEncoder
        self.sChannels = str(nChannels)
        self.pProc = None
        self.lSignals.append([None, 'message::tag', self.onTag])
        sDeinterleave = ''

        for nChannel in range(nChannels):

            sDeinterleave += ' d.src_' + str(nChannel) + ' ! queue ! rganalysis ! fakesink'

        sResample = ''

        if nBps not in [16, 32]:

            sResample += ', format=F32LE'

        if nRate in [88200, 176400, 352800]:

            sResample += ', rate=44100'

        elif nRate in [96000, 192000]:

            sResample += ', rate=48000'

        self.init('filesrc location="' + escape(sPathIn) + '" ! decodebin ! audioconvert ! audioresample ! audio/x-raw' + sResample + ', channels=' + self.sChannels + ' ! deinterleave name=d' + sDeinterleave, None)
        self.play()

    def onTag(self, pElement, pMessage):

        pTagList = pMessage.parse_tag()
        lPeak = pTagList.get_double('replaygain-track-peak')
        lGain = pTagList.get_double('replaygain-track-gain')

        if lPeak[0] and (self.dTags['replaygain-track-peak'] is None or lPeak.value > self.dTags['replaygain-track-peak']):

            self.dTags['replaygain-track-peak'] = lPeak.value

        if lGain[0] and (self.dTags['replaygain-track-gain'] is None or lGain.value < self.dTags['replaygain-track-gain']):

            self.dTags['replaygain-track-gain'] = lGain.value

    def onEos(self, pElement, pMessage):

        super().onEos(pElement, pMessage)

        if self.sOperation == 'replay-gain':

            self.nOperation = 1
            self.sOperation = 'encode'

            for sKey in ['track-number', 'track-count', 'album-disc-number', 'album-disc-count', 'date', 'image']:

                if sKey in self.dTags:

                    if self.dTags[sKey]:

                        if sKey == 'track-number':

                            self.dTags[sKey] = GObject.Value(GObject.TYPE_UINT, int(self.dTags[sKey]))

                        elif sKey == 'track-count':

                            self.dTags[sKey] = GObject.Value(GObject.TYPE_UINT, int(self.dTags[sKey]))

                        elif sKey == 'album-disc-number':

                            self.dTags[sKey] = GObject.Value(GObject.TYPE_UINT, int(self.dTags[sKey]))

                        elif sKey == 'album-disc-count':

                            self.dTags[sKey] = GObject.Value(GObject.TYPE_UINT, int(self.dTags[sKey]))

                        elif sKey == 'date':

                            self.dTags['extended-comment'] = 'DATE=' + self.dTags[sKey]
                            self.dTags[sKey] = GLib.Date.new_dmy(1, 1, int(self.dTags[sKey]))

                        elif sKey == 'image':

                            with open(self.dTags[sKey], 'rb') as pFile:

                                self.dTags[sKey] = pFile.read()

                            self.dTags[sKey] = GstTag.tag_image_data_to_image_sample(self.dTags[sKey], GstTag.TagImageType.FRONT_COVER)

                    else:

                        del self.dTags[sKey]

            self.dTags['replaygain-reference-level'] = 89.0

            if self.sEncoder == 'flac':

                self.init('filesrc location="' + escape(self.sPathIn) + '" ! decodebin ! audioconvert ! audio/x-raw, channels=(int)' + self.sChannels + ' ! flacenc name=enc quality=8 ! filesink location="' + escape(self.sPathTmp) + '"', self.dTags)
                self.play()

            else:

                self.pProc = subprocess.Popen('neroAacEnc -if "' + escape(self.sPathIn) + '" -of "' + escape(self.sPathTmp) + '" -q 1.0 ', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines = True)
                self.sOperation = 'nero-encode'

        elif self.sOperation == 'encode' or self.sOperation == 'nero-tag':

            if self.sOperation == 'nero-tag':

                shutil.move(self.sPathTmp.replace('m4a', 'tmp.m4a'), self.sPathTmp)

                pMp4 = MP4(self.sPathTmp)
                pMp4['----:com.apple.iTunes:replaygain_track_gain'] = str(round(self.dTags['replaygain-track-gain'], 2)).encode()
                pMp4['----:com.apple.iTunes:replaygain_track_peak'] = str(round(self.dTags['replaygain-track-peak'], 6)).encode()
                pMp4.save()

            shutil.move(self.sPathTmp, self.sPathOut)

            self.nState = GstState.DONE

            GLib.idle_add(self.pCallback, self.pParam)

    def getPosition(self):

        if self.sOperation == 'replay-gain' and self.sEncoder == 'aac':

            return super().getPosition() / 5

        elif self.sOperation == 'nero-encode':

            if self.pProc:

                idle()

                strLine = self.pProc.stderr.readline()

                if not self.pProc.poll() is None and len(strLine) == 0:

                    self.sOperation = 'nero-tag'
                    self.pProc = None
                    self.init('filesrc location="' + escape(self.sPathTmp) + '" ! qtdemux ! mp4mux name=enc ! filesink location="' + escape(self.sPathTmp.replace('m4a', 'tmp.m4a')) + '"', self.dTags)
                    self.play()

                    return 1.0

                pMatch = re.match('(Processed )(\d+)( seconds\.\.\.\n)', strLine)

                if pMatch:

                    return 0.1 + min(float(pMatch.group(2)) / (self.nDuration / 1000000000) * 0.9, 0.9)

            return 0.1

        elif self.sOperation == 'nero-tag':

            return 1.0

        return super().getPosition()

    def close(self):

        if self.pProc:

            self.pProc.terminate()

        else:

            super().close()

class GstSplitter(GstBase):

    def __init__(self):

        super().__init__()

    def run(self, strFilePath, sOutPath, nStart, nEnd, pCallback, *lParams):

        self.nState = GstState.RUNNING
        self.pCallback = pCallback
        self.lParams = lParams
        self.nStart = nStart
        self.init('filesrc location="' + escape(strFilePath) + '" ! decodebin ! audioconvert ! audio/x-raw ! fakesink', None)
        self.nDuration = self.pPipeline.query_duration(Gst.Format.TIME)[1]
        self.close()

        if nEnd is None:

            nEnd = self.nDuration

        self.nDuration = nEnd - nStart
        self.init('filesrc location="' + escape(strFilePath) + '" ! decodebin ! audioconvert ! wavenc ! filesink location="' + escape(sOutPath) + '"', None)
        self.seek(nStart, nEnd, True)
        self.play()

    def getPosition(self):

        fProgress = 0.0

        if self.nState == GstState.DONE:

            fProgress = 1.0

        elif self.pPipeline:

            fProgress = (self.pPipeline.query_position(Gst.Format.TIME)[1] - self.nStart) / self.nDuration

            if fProgress > 1.0:

                fProgress = 1.0

            elif fProgress < 0.0:

                fProgress = 0.0

        return fProgress

    def onEos(self, pElement, pMessage):

        super().onEos(pElement, pMessage)

        self.nState = GstState.DONE

        GLib.idle_add(self.pCallback, *self.lParams)

    @staticmethod
    def parseCueSheet(sCuePath):

        dCue = {'file': '', 'tracks': []}

        with open(sCuePath, 'r', errors='backslashreplace') as pFile:

            for sLine in pFile:

                sLine = sLine.strip().replace('\\x92', '\'').replace('\\x85', '')

                pMatch = re.match('^FILE "(.*)" .*$', sLine)

                if pMatch:

                    sDirPath = os.path.dirname(sCuePath)
                    dCue['file'] = os.path.join(sDirPath, pMatch.group(1))

                    continue

                pMatch = re.match('^TRACK \d\d .*$', sLine)

                if pMatch:

                    dCue['tracks'].append({'performer': '', 'title': '', 'start': 0, 'end': None})

                    continue

                pMatch = re.match('^TITLE "(.*)"$', sLine)

                if dCue['tracks'] and pMatch:

                    dCue['tracks'][-1]['title'] = pMatch.group(1).replace('/', '-')

                    continue

                pMatch = re.match('^PERFORMER "(.*)"$', sLine)

                if dCue['tracks'] and pMatch:

                    dCue['tracks'][-1]['performer'] = pMatch.group(1).replace('/', '-')

                    continue

                pMatch = re.match('^INDEX 01 (\d\d):(\d\d):(\d\d)$', sLine)

                if dCue['tracks'] and pMatch:

                    if len(dCue['tracks']) >= 2:

                        dCue['tracks'][-2]['end'] = round((int(pMatch.group(1)) * 60 + int(pMatch.group(2)) + int(pMatch.group(3)) / 75) * Gst.SECOND)

                    dCue['tracks'][-1]['start'] = round((int(pMatch.group(1)) * 60 + int(pMatch.group(2)) + int(pMatch.group(3)) / 75) * Gst.SECOND)

                    continue

        return dCue

class GstDvd(GstBase):

    def __init__(self):

        super().__init__()

        self.bEos = False

    def getPosition(self):

        fProgress = 0.0

        if self.nState == GstState.DONE or self.bEos:

            fProgress = 1.0

        elif self.pPipeline:

            fProgress = self.pPipeline.query_position(Gst.Format.TIME)[1] / self.nDuration

            if fProgress > 1.0:

                self.bEos = True
                self.pPipeline.set_state(Gst.State.PAUSED)
                self.pPipeline.get_state(Gst.CLOCK_TIME_NONE)
                pBus = self.pPipeline.get_bus()
                pDvdReadSrc = self.pPipeline.get_by_name('dvdsrc')
                pMessage = Gst.Message.new_eos(pDvdReadSrc)
                pBus.post(pMessage)
                self.pPipeline.get_state(Gst.CLOCK_TIME_NONE)

                fProgress = 1.0

            elif fProgress < 0.0:

                fProgress = 0.0

        return fProgress

    def onEos(self, pElement, pMessage):

        super().onEos(pElement, pMessage)
        shutil.move(self.sOutPath + '00', self.sOutPath)

        if os.path.exists(self.sOutPath + '01'):

            os.remove(self.sOutPath + '01')

        self.nState = GstState.DONE

        GLib.idle_add(self.pCallback, *self.lParams)

    def run(self, sPath, sOutPath, nTitle, nChapter, fLength, pCallback, *lParams):

        self.nState = GstState.RUNNING
        self.pCallback = pCallback
        self.lParams = lParams
        self.sOutPath = sOutPath
        self.nOperations = 1
        self.nOperation = 0
        sPath = os.path.dirname(sPath)
        #pFormatChapter = Gst.format_register('chapter', 'DVD chapter')
        self.nDuration = int(fLength * Gst.SECOND)
        self.init('dvdreadsrc name=dvdsrc device="{}" title={} chapter={} ! decodebin ! audio/x-raw,format=S16BE ! audioconvert ! audio/x-raw,format=S16LE ! splitmuxsink max-size-time={} muxer=wavenc location="{}%02d"'.format(escape(sPath), nTitle, nChapter, self.nDuration, sOutPath), None)
        #self.init('dvdreadsrc name=dvdsrc device="{}" title={} chapter={} ! decodebin ! audio/x-raw,format=S16BE ! audioconvert ! audio/x-raw,format=S16LE ! wavenc ! filesink location="{}"'.format(escape(sPath), nTitle, nChapter, sOutPath), None)
        #self.pPipeline.get_by_name('dvdsrc').seek(1.0, pFormatChapter, Gst.SeekFlags.FLUSH, Gst.SeekType.SET, nChapter, Gst.SeekType.SET, nChapter + 1)
        #self.pPipeline.get_state(Gst.CLOCK_TIME_NONE)
        self.play()
