#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers import media
from sys import argv, stderr
from urllib2 import urlopen, Request

url = argv[1]
input_filename = 'oami-gstreamer-test-input'
output_filename = 'oami-gstreamer-test-output'

stderr.write("Getting file from <%s>, writing to “%s” … " % \
    (
        url,
        input_filename
    )
)
with open(input_filename, 'w') as input_file:
    request = Request(url, None, {'User-Agent' : 'oami-gstreamer-converter-check/2012-12-03'})
    input_file.write(
        urlopen(request).read()
    )
stderr.write("done.\n")

stderr.write("Setting up Media helper for “%s”… " % input_filename)
m = media.Media(input_filename)
stderr.write("done.\n")

stderr.write("Attempting finding streams of “%s” … " % input_filename)
m.find_streams()
stderr.write("done.\n")

stderr.write("Attempting conversion of “%s”, writing into “%s” … " % \
    (
        input_filename,
        output_filename
    )
)
m.convert(output_filename)
stderr.write("done.\n")
