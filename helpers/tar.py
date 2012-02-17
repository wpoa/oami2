#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import tarfile

from os import path
from sys import stderr

from pubmed import find_supplementary_materials

def find_media(filename, results_directory):
    """
    This function iterates over a PubMed tar archive, finding
    publications having supplementary materials.
    """
    fail_cache_path = path.join(results_directory, 'fail_cache')
    try:
        with open(fail_cache_path, 'r') as fail_cache:
            fail_filenames = fail_cache.read().split()
    except IOError:  # file does not exist on first run
        fail_filenames = []

    success_cache_path = path.join(results_directory, 'success_cache')
    try:
        with open(success_cache_path, 'r') as success_cache:
            reader = csv.reader(success_cache)
            success_filenames = [row[0] for row in reader]
            print success_filenames
    except IOError:  # file does not exist on first run
        success_filenames = []

    with tarfile.open(filename) as archive:
        stderr.write('Looking for supplementary materials in in “%s“ …\n' % filename.encode('utf-8'))
        stderr.write('\nLegend:\n')
        stderr.write('\t“_” : skipped due to cached result\n\t“.” : no supplementary materials\n\t“#” : supplementary materials found\n')

        with open(fail_cache_path, 'a') as fail_cache:
            with open(success_cache_path, 'a') as success_cache:
                success_writer = csv.writer(success_cache)
                for item in archive:
                    if item.name not in fail_filenames and \
                        item.name not in success_filenames:
                        if path.splitext(item.name)[1] == '.nxml':
                            content = archive.extractfile(item)
                            urllist = find_supplementary_materials(content)
                            if urllist:
                                stderr.write('#')  # denotes file with supplementary materials
                                stderr.flush()
                                for url in urllist:
                                    stderr.write(url)
                                    success_writer.writerow([item.name, url])
                            else:
                                stderr.write('.')  # denotes file without supplementary materials
                                stderr.flush()
                                fail_cache.write(item.name + '\n')
                    else:
                        stderr.write('_')  # denotes skipped file
    
