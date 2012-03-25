#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from urllib2 import urlopen, urlparse

# According to <ftp://ftp.ncbi.nlm.nih.gov/README.ftp>, this should be
# 33554432 (32MiB) for best performance. Note that on slow connections,
# however, huge buffers size leads to notable interface lag.
BUFSIZE = 33554432
#BUFSIZE = 1024000  # (1024KB)

def download_metadata(target_directory):
    """
    Downloads files from PubMed FTP server into given directory.
    """
    urls = [
        'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/articles.A-B.tar.gz',
        'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/articles.C-H.tar.gz',
        'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/articles.I-N.tar.gz',
        'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/articles.O-Z.tar.gz'
    ]

    for url in urls:
        remote_file = urlopen(url)
        total = int(remote_file.headers['content-length'])
        completed = 0

        url_path = urlparse.urlsplit(url).path
        local_filename = path.join(target_directory, \
            url_path.split('/')[-1])

        # if local file has same size as remote file, skip download
        try:
            if (path.getsize(local_filename) == total):
                continue
        except OSError:  # local file does not exist
            pass

        with open(local_filename,'wb') as local_file:
            while True:
                chunk = remote_file.read(BUFSIZE)
                if chunk != '':
                    local_file.write(chunk)
                    completed += len(chunk)
                    yield {
                        'url': url,
                        'completed': completed,
                        'total': total
                    }
                else:
                    break
