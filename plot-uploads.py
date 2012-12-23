#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pylab

from datetime import date
from math import sqrt
from helpers import mediawiki

uploads = mediawiki.get_uploads()

uploads_per_month = {}
uploads_per_day = {}

for (timestamp, title) in uploads:
    day = timestamp.date()
    try:
        uploads_per_day[day] += 1
    except KeyError:
        uploads_per_day[day] = 1

uploads_total = {}
totalcount = 0

days, daycount = zip(*sorted(uploads_per_day.items()))

uploads_total_per_day = {}
totalcount = 0

for day, count in zip(days, daycount):
    totalcount += count
    uploads_total_per_day[day] = totalcount

timestamps, totalcount = zip(*sorted(uploads_total_per_day.items()))
pylab.plot(
    timestamps,
    totalcount,
    c='black',
    linewidth=1,
    zorder=-1
)

dayarea = [sqrt(d)*100 for d in daycount]
pylab.scatter(
    x=days,
    y=totalcount,
    s=dayarea,
   c=daycount,
   cmap=pylab.cm.summer_r,
   linewidths=1,
   edgecolor='black'
)

pylab.title("Contributions using Open Access Media Importer")
pylab.xlabel("Time (UTC)")
pylab.ylabel("Edits")

pylab.colorbar().set_ticks(range(0, max(daycount), 5))
pylab.show()
