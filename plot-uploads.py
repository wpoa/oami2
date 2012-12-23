#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pylab

from datetime import date
from helpers import mediawiki

uploads = mediawiki.get_uploads()

uploads_per_month = {}
uploads_per_day = {}
uploads_total = {}

total = 0

for (timestamp, title) in uploads:
    day = timestamp.date()
    total += 1
    uploads_total[timestamp] = total
    try:
        uploads_per_day[day] += 1
    except KeyError:
        uploads_per_day[day] = 1
    month = date(timestamp.year, timestamp.month, 15)
    try:
        uploads_per_month[month] += 1
    except KeyError:
        uploads_per_month[month] = 1

# FIXME: this is wrong
timestamps, totalcount = zip(*sorted(uploads_total.items()))
pylab.plot(timestamps, totalcount)

months, monthcount = zip(*sorted(uploads_per_month.items()))
pylab.plot(months, monthcount)

days, daycount = zip(*sorted(uploads_per_day.items()))
pylab.scatter(days, daycount)

pylab.title("Open Access Media Importer contributions")
pylab.xlabel("Time (UTC)")
pylab.ylabel("Uploads")


pylab.show()
