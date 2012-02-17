#!/usr/bin/env python
# -*- coding: utf-8 -*-

import progressbar, sys

from os import makedirs, path, stat
from ftplib import FTP

def get(server, filenames, local_directory):
    """
    Downloads multiple files from a given FTP server into a directory.
    """
    local_filenames = [
        path.join(local_directory, path.split(remote_filename)[-1])
        for remote_filename in filenames
    ]

    ftp = FTP(server)
    ftp.login()

    for i, remote_filename in enumerate(filenames):
        local_filename = local_filenames[i]

        ftp.sendcmd('TYPE i')  # switch to binary mode,
        remote_filesize = ftp.size(remote_filename)
        try:
            local_filesize = stat(local_filename).st_size
        except OSError:  # File does not exist
            local_filesize = 0

        if remote_filesize == local_filesize:
            sys.stderr.write("%s is up to date, skipping.\n" % local_filename)
        else:
            sys.stderr.write("Downloading %s from %s, saving to %s .\n" % \
                (remote_filename, server, local_filename))

            with open(local_filename, 'wb') as f:
                p = progressbar.ProgressBar(maxval=remote_filesize)

                def callback(chunk):
                    f.write(chunk)
                    p.update(p.currval + len(chunk))

                ftp.retrbinary("RETR %s" % remote_filename, callback)

    ftp.quit()
