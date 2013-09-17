from autovividict import autovividict
from urllib2 import quote

def make_datestring(year, month, day):
    datestring = "%04d" % year  # YYYY
    if month is not None:
        datestring += "-%02d" % month  # YYYY-MM
    if day is not None:
        datestring += "-%02d" % day  # YYYY-MM-DD
    return datestring

def filename_from_url(url):
    return quote(url, safe='')
