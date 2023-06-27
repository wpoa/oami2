#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers import media
from sys import argv, stderr
from urllib2 import urlopen, Request

url = argv[1]
input_filename = 'oami-gstreamer-test-input'
output_filename = 'oami-gstreamer-test-output'

print("Getting file from <%s>, writing to “%s” … " % \
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
print("done.\n")

print("Setting up Media helper for “%s”… " % input_filename)
m = media.Media(input_filename)
print("done.\n")

print("Attempting finding streams of “%s” … " % input_filename)
m.find_streams()
print("done.\n")

print("Attempting conversion of “%s”, writing into “%s” … " % \
    (
        input_filename,
        output_filename
    )
)
m.convert(output_filename)
print("done.\n")
