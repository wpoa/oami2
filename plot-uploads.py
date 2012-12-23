#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pylab

from datetime import date
from math import sqrt
from sys import stderr

from helpers import mediawiki

uploads = mediawiki.get_uploads()

pylab.figure(figsize=(20.0, 12.0))

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

pylab.suptitle(
    'Timeline of Open Access Media Importer Contributions ' + \
    'for %s between %s and %s' % (
            mediawiki.get_wiki_name(),
            min(days),
            max(days)
    )
)

pylab.xlabel("Time (UTC)")
pylab.ylabel("Edits")

pylab.colorbar()
pylab.grid(True)

filename = 'plot-uploads.png'
with open(filename, 'w') as f:
    pylab.savefig(f, format='png', bb_inches='tight', pad_inches=0)
    stderr.write('Wrote figure to “%s”.\n' % filename)
