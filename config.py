#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import makedirs, path
from sys import stderr, exit
from xdg import BaseDirectory

APPLICATION_NAME="open-access-media-importer"
cache_path = path.join(BaseDirectory.xdg_cache_home, APPLICATION_NAME)
config_path = path.join(BaseDirectory.xdg_config_home, APPLICATION_NAME)
data_path = path.join(BaseDirectory.xdg_data_home, APPLICATION_NAME)

def ensure_directory_exists(directory):
    if not path.exists(directory):
        makedirs(directory)

for p in (cache_path, config_path, data_path):
    ensure_directory_exists(p)

_metadata_path = path.join(cache_path, 'metadata')

_metadata_raw_path = path.join(_metadata_path, 'raw')
def get_metadata_raw_source_path(source_name):
    p = path.join(_metadata_raw_path, source_name)
    ensure_directory_exists(p)
    return p

_metadata_refined_path = path.join(_metadata_path, 'refined')
def get_metadata_refined_source_path(source_name):
    p = path.join(_metadata_refined_path, source_name)
    ensure_directory_exists(p)
    return p

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
