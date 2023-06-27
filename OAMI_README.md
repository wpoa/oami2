The aim of this project is to write a tool that would:
* regularly spider PubMed Central to locate audio and video files published in the supplementary materials of CC BY-licensed articles in the Open subset
* convert these files to OGG
* upload them to Wikimedia Commons, along with the respective metadata
* provide for easy extension to other CC-BY sources, beyond PubMed Central
* (possibly) suggest Wikipedia articles for which the video might be relevant

Wiki page:
    http://en.wikiversity.org/wiki/User:OpenScientist/Open_grant_writing/Wissenswert_2011

Commands:
    oa-get [download-metadata|download-media] [dummy|pmc|pmc_doi]
    oa-cache [browse-database|clear-database|clear-media|convert-media|find-media|list-articles|stats] [dummy|pmc|pmc_doi]
    oa-put upload-media [dummy|pmc|pmc_doi]

Dependencies:
    python-dateutil <http://pypi.python.org/pypi/python-dateutil>
    python-elixir <http://elixir.ematia.de/trac/wiki>
    python-gst0.10 <http://gstreamer.freedesktop.org/modules/gst-python.html>
    python-magic <http://www.darwinsys.com/file/>
    python-mutagen <http://code.google.com/p/mutagen/>
    python-progressbar <http://pypi.python.org/pypi/progressbar/2.2>
    python-xdg <http://freedesktop.org/wiki/Software/pyxdg>
    python-werkzeug <http://werkzeug.pocoo.org/>
    python-wikitools <http://code.google.com/p/python-wikitools/> (python-wikitools was imported into our tree and patched to ease deployment)

Recommendations:
    sqlitebrowser <http://sqlitebrowser.sourceforge.net/>

To use the upload feature of oa-put, copy the userconfig.example file to
“$HOME/config/open-access-media-importer/userconfig”.

A screencast showing usage can be played back with “ttyplay screencast”.

To plot mimetypes occurring in sources, install python-matplotlib and pipe the output of “oa-cache stats [source]” to the included plot-helper script.

License:
The Open Access Media Importer is free software: 
you can redistribute it and/or modify it 
under the terms of the GNU General Public License 
as published by the Free Software Foundation, 
either version 3 of the License, 
or (at your option) any later version.
