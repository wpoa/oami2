#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gobject, pygst
pygst.require("0.10")

import gst
import progressbar

from sys import exit, stderr

class Media():
    def __init__(self, filename):
        self.filename = filename
        self.has_audio = False
        self.has_video = False
        self.position = 0
        self.lastposition = 0

    def find_streams(self):
        """
        Determines if media file has audio and / or video streams.
        """
        loop = gobject.MainLoop()
        pipeline = gst.parse_launch("filesrc name=source ! decodebin2 ! fakesink")

        source = pipeline.get_by_name("source")
        source.set_property("location", self.filename)

        bus = pipeline.get_bus()
        def on_message(bus, message):
            t = message.type
            if t == gst.MESSAGE_TAG:
                pipeline.set_state(gst.STATE_PAUSED)
                keys = message.structure.keys()
                if 'audio-codec' in keys:
                    self.has_audio = True
                if 'video-codec' in keys:
                    self.has_video = True
            if t == gst.MESSAGE_ASYNC_DONE:
                pipeline.set_state(gst.STATE_NULL)
                loop.quit()
            elif t == gst.MESSAGE_ERROR:  # error
                err, debug = message.parse_error()
                pipeline.set_state(gst.STATE_NULL)
                loop.quit()
                if str(err) in [
                    'Your GStreamer installation is missing a plug-in.',
                    'Could not demultiplex stream.'
                ]:
                    raise RuntimeError, str(err)
                else:
                    stderr.write('ERROR: %s\n' %str(err))

        bus.add_signal_watch()
        bus.connect('message', on_message)

        pipeline.set_state(gst.STATE_PLAYING)
        pipeline.get_state()

        loop.run()

    def convert(self, outfile):
        """
        Converts media file to Ogg Theora or Ogg Theora+Vorbis.
        """
        loop = gobject.MainLoop()

        if self.has_video and self.has_audio:
            pipeline = gst.parse_launch("""
                filesrc name=source ! decodebin2 name=decoder
                decoder. ! queue ! theoraenc ! queue ! oggmux name=muxer
                decoder. ! queue ! audioconvert ! audioresample ! vorbisenc ! progressreport name=report ! muxer.
                muxer. ! filesink name=sink
            """)
        elif self.has_video and not self.has_audio:
            pipeline = gst.parse_launch("""
                filesrc name=source ! decodebin2 name=decoder
                decoder. ! queue ! ffmpegcolorspace ! theoraenc ! progressreport name=report ! oggmux name=muxer
                muxer. ! filesink name=sink
            """)
        elif not self.has_video and self.has_audio:
            pipeline = gst.parse_launch("""
                filesrc name=source ! decodebin2 name=decoder
                decoder. ! queue ! audioconvert ! audioresample ! vorbisenc ! progressreport name=report ! oggmux name=muxer
                muxer. ! filesink name=sink
            """)
        else:
            raise RuntimeError, 'Unknown audio/video stream combination.'

        source = pipeline.get_by_name('source')
        source.set_property('location', self.filename)

        sink = pipeline.get_by_name('sink')
        sink.set_property('location', outfile)

        report = pipeline.get_by_name('report')
        report.set_property('silent', True)

        bus = pipeline.get_bus()
        def on_message(bus, message):
            t = message.type
            if t == gst.MESSAGE_EOS:  # end of stream
                pipeline.set_state(gst.STATE_NULL)
                loop.quit()
            elif t == gst.MESSAGE_ERROR:  # error
                err, debug = message.parse_error()
                stderr.write('ERROR: %s\n' %str(err))
                pipeline.set_state(gst.STATE_NULL)
                loop.quit()

        bus.add_signal_watch()
        bus.connect("message", on_message)

        pipeline.set_state(gst.STATE_PLAYING)
        pipeline.get_state()

        try:
            duration = pipeline.query_duration(gst.FORMAT_TIME, None)[0]
            progress = progressbar.ProgressBar(maxval=duration)
        except gst.QueryError:
            pass

        def update_progress():
            try:
                self.position = pipeline.query_position(gst.FORMAT_TIME, \
                    None)[0]
            except:
                return False  # stop loop
            try:
                progress.update(self.position)
            except:
                # progressbar fails on >100% progress
                # fall back to pipeline reporting
                report.set_property('silent', False)
            return True  # continue loop

        def abort_on_stall():
            if self.position == self.lastposition:
                stderr.write('Conversion of <%s> stalled, aborting …\n' % \
                    self.filename.encode('utf-8'))
                exit(1)
            self.lastposition = self.position
            return True

        gobject.timeout_add(100, update_progress)
        gobject.timeout_add(60000, abort_on_stall)
        loop.run()
