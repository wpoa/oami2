#!/usr/local/bin/python
# -*- coding: utf-8 -*

try:
    from colorama import Fore, Style
    color = True
    red = Fore.RED
    yellow = Fore.YELLOW
    bright = Style.BRIGHT
    reset = Style.RESET_ALL
except:
    color = False
    red = ""
    yellow = ""
    bright = ""
    reset = ""

from sys import stderr

def emit_error(title, text):
    error = "%s%s%s %s%s\n" % (
        red,
        bright,
        title,
        reset,
        text
    )
    stderr.write(error)

def emit_warning(text):
    warning = "%s%s%s%s\n" % (
        yellow,
        bright,
        text,
        reset
    )
    stderr.write(warning)

def make_datestring(year, month, day):
    datestring = "%04d" % year  # YYYY
    if month is not None:
        datestring += "-%02d" % month  # YYYY-MM
    if day is not None:
        datestring += "-%02d" % day  # YYYY-MM-DD
    return datestring

