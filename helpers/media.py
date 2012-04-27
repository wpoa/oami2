#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gobject, pygst
pygst.require("0.10")

import gst
import progressbar

class Media():
    def __init__(self, filename):
        self.filename = filename
        self.has_audio = False
        self.has_video = False

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
            if message.type == gst.MESSAGE_TAG:
                pipeline.set_state(gst.STATE_PAUSED)
                keys = message.structure.keys()
                if 'audio-codec' in keys:
                    self.has_audio = True
                if 'video-codec' in keys:
                    self.has_video = True
            if message.type == gst.MESSAGE_ASYNC_DONE:
                pipeline.set_state(gst.STATE_NULL)
                loop.quit()
    
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
                filesrc name=source ! decodebin2 name=decoder !
                theoraenc ! oggmux name=muxer ! filesink name=sink
                decoder. ! vorbisenc ! muxer.
            """)
        elif self.has_video and not self.has_audio:
            pipeline = gst.parse_launch("""
                filesrc name=source ! decodebin2 name=decoder !
                theoraenc ! oggmux name=muxer ! filesink name=sink
            """)
        else:
            raise RuntimeError, 'Unknown audio/video stream combination.'

        source = pipeline.get_by_name('source')
        source.set_property('location', self.filename)

        sink = pipeline.get_by_name('sink')
        sink.set_property('location', outfile)

        bus = pipeline.get_bus()
        def on_message(bus, message):
            t = message.type
            if t == gst.MESSAGE_EOS:  # end of stream
                pipeline.set_state(gst.STATE_NULL)
                loop.quit()
            elif t == gst.MESSAGE_ERROR:  # error
                err, debug = message.parse_error()
                pipeline.set_state(gst.STATE_NULL)
                loop.quit()

        bus.add_signal_watch()
        bus.connect("message", on_message)

        pipeline.set_state(gst.STATE_PLAYING)
        pipeline.get_state()

        try:
            duration = pipeline.query_duration(gst.FORMAT_TIME, None)[0]
            progress = progressbar.ProgressBar(maxval=duration)
        except:
            pass

        def update_progress():
            try:
                position = pipeline.query_position(gst.FORMAT_TIME, \
                    None)[0]
                progress.update(position)
                return True  # continue loop
            except:
                return False  # stop loop

        gobject.timeout_add(100, update_progress)
        loop.run()
