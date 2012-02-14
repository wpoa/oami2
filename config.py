#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from sys import stderr, exit
from xdg import BaseDirectory

APPLICATION_NAME="open-access-importer"
cache_path = path.join(BaseDirectory.xdg_cache_home, APPLICATION_NAME)
config_path = path.join(BaseDirectory.xdg_config_home, APPLICATION_NAME)
data_path = path.join(BaseDirectory.xdg_data_home, APPLICATION_NAME)

metadata_path = path.join(cache_path, 'metadata')
metadata_raw_path = path.join(metadata_path, 'raw')

import json

SOURCES_FILENAME = "sources.json"
config_sources = path.join(config_path, SOURCES_FILENAME)

try:
    with open(config_sources) as f:
        try:
            sources = json.load(f)
        except ValueError:
            stderr.write("“%s” is not a valid JSON file. Aborting …\n" %
                config_sources)
            exit(1)
except IOError:
    stderr.write("No file named “%s” in “%s”. Aborting …\n" %
        (SOURCES_FILENAME, config_path))
    exit(1)
