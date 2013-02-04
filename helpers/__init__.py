#!/usr/local/bin/python
# -*- coding: utf-8 -*

from sys import stderr

def make_datestring(year, month, day):
    datestring = "%04d" % year  # YYYY
    if month is not None:
        datestring += "-%02d" % month  # YYYY-MM
    if day is not None:
        datestring += "-%02d" % day  # YYYY-MM-DD
    return datestring

