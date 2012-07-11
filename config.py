#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import makedirs, path
from sys import stderr, exit
from xdg import BaseDirectory
from ConfigParser import RawConfigParser, NoSectionError, NoOptionError

APPLICATION_NAME="open-access-media-importer"
cache_path = path.join(BaseDirectory.xdg_cache_home, APPLICATION_NAME)
config_path = path.join(BaseDirectory.xdg_config_home, APPLICATION_NAME)
data_path = path.join(BaseDirectory.xdg_data_home, APPLICATION_NAME)

def database_path(source):
    return path.join(data_path, '%s.sqlite' % source)

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

_media_path = path.join(cache_path, 'media')

_media_raw_path = path.join(_media_path, 'raw')
def get_media_raw_source_path(source_name):
    p = path.join(_media_raw_path, source_name)
    ensure_directory_exists(p)
    return p

_media_refined_path = path.join(_media_path, 'refined')
def get_media_refined_source_path(source_name):
    p = path.join(_media_refined_path, source_name)
    ensure_directory_exists(p)
    return p

free_license_urls = [
    'http://creativecommons.org/licenses/by/2.0/',
    'http://creativecommons.org/licenses/by-sa/2.0/',
    'http://creativecommons.org/licenses/by/2.5/',
    'http://creativecommons.org/licenses/by-sa/2.5/',
    'http://creativecommons.org/licenses/by/3.0/',
    'http://creativecommons.org/licenses/by-sa/3.0/'
]

USERCONFIG_FILENAME = "userconfig"
userconfig_file = path.join(config_path, USERCONFIG_FILENAME)
userconfig = RawConfigParser()
userconfig.optionsxform = str  # case sensitivity
userconfig.read(userconfig_file)

def get_userconfig(section, option):
    try:
        return userconfig.get(section, option)
    except NoSectionError:
        stderr.write("“%s” does not contain a “%s” section.\n" % \
                         (userconfig_file, section))
        exit(127)
    except NoOptionError:
        stderr.write("“%s” does not contain a “%s” option.\n" % \
                         (userconfig_file, option))
        exit(127)

api_url = get_userconfig('wiki', 'api_url')
username = get_userconfig('wiki', 'username')
password = get_userconfig('wiki', 'password')
