from autovividict import autovividict
from base64 import b64encode
from urllib2 import urlparse
from os import path

def make_datestring(year, month, day):
    datestring = "%04d" % year  # YYYY
    if month is not None:
        datestring += "-%02d" % month  # YYYY-MM
    if day is not None:
        datestring += "-%02d" % day  # YYYY-MM-DD
    return datestring

def filename_from_url(url):
    url_path = urlparse.urlsplit(url).path
    extension = path.splitext(url_path)[1]
    return b64encode(url) + extension
