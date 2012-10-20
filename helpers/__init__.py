#!/usr/local/bin/python
# -*- coding: utf-8 -*

from colorama import Fore, Style
from sys import stderr

def emit_error(title, text):
    error = "%s%s%s %s%s\n" % (
        Fore.RED,
        Style.BRIGHT,
        title,
        Style.RESET_ALL,
        text
    )
    stderr.write(error)

def emit_warning(text):
    warning = "%s%s%s%s\n" % (
        Fore.YELLOW,
        Style.BRIGHT,
        text,
        Style.RESET_ALL
    )
    stderr.write(warning)

def make_datestring(year, month, day):
    datestring = "%04d" % year  # YYYY
    if month is not None:
        datestring += "-%02d" % month  # YYYY-MM
    if day is not None:
        datestring += "-%02d" % day  # YYYY-MM-DD
    return datestring
