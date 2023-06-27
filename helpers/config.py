#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from sys import stderr, exit
from xdg import xdg_cache_home, xdg_config_home, xdg_data_home
from configparser import RawConfigParser, NoSectionError, NoOptionError

APPLICATION_NAME = "OpenAccessMediaImporterBot"
cache_path = os.path.join(xdg_cache_home(), APPLICATION_NAME)
print(cache_path)
config_path = (
    r"../OpenAccessMediaImporterBot"  # Update the path to the config directory
)
# config_path = os.path.join(xdg_config_home(), APPLICATION_NAME)
data_path = os.path.join(xdg_data_home(), APPLICATION_NAME)


def database_path(source):
    return os.path.join(data_path, f"{source}.sqlite")


def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


for p in (cache_path, config_path, data_path):
    ensure_directory_exists(p)

_metadata_path = os.path.join(cache_path, "metadata")

_metadata_raw_path = os.path.join(_metadata_path, "raw")


def get_metadata_raw_source_path(source_name):
    p = os.path.join(_metadata_raw_path, source_name)
    ensure_directory_exists(p)
    return p


_metadata_refined_path = os.path.join(_metadata_path, "refined")


def get_metadata_refined_source_path(source_name):
    p = os.path.join(_metadata_refined_path, source_name)
    ensure_directory_exists(p)
    return p


_media_path = os.path.join(cache_path, "media")

_media_raw_path = os.path.join(_media_path, "raw")


def get_media_raw_source_path(source_name):
    p = os.path.join(_media_raw_path, source_name)
    ensure_directory_exists(p)
    return p


_media_refined_path = os.path.join(_media_path, "refined")


def get_media_refined_source_path(source_name):
    p = os.path.join(_media_refined_path, source_name)
    ensure_directory_exists(p)
    return p


free_license_urls = [
    "http://creativecommons.org/licenses/by/2.0/",
    "http://creativecommons.org/licenses/by-sa/2.0/",
    "http://creativecommons.org/licenses/by/2.5/",
    "http://creativecommons.org/licenses/by-sa/2.5/",
    "http://creativecommons.org/licenses/by/3.0/",
    "http://creativecommons.org/licenses/by-sa/3.0/",
    "http://creativecommons.org/licenses/by/4.0/",
    "http://creativecommons.org/licenses/by-sa/4.0/",
    "http://creativecommons.org/publicdomain/zero/1.0/",
]

USERCONFIG_FILENAME = "userconfig"
userconfig_file = os.path.join(config_path, USERCONFIG_FILENAME)
userconfig = RawConfigParser()
userconfig.optionxform = str  # case sensitivity
userconfig.read(userconfig_file)


def get_userconfig(section, option):
    try:
        return userconfig.get(section, option)
    except NoSectionError:
        print(f"“{userconfig_file}” does not contain a “{section}” section.\n")
        exit(127)
    except NoOptionError:
        print(
            f"“{userconfig_file}” does not contain a “{option}” option in the “{section}” section.\n"
        )
        exit(127)


api_url = get_userconfig("wiki", "api_url")
username = get_userconfig("wiki", "username")
password = get_userconfig("wiki", "password")
whitelist_doi = get_userconfig("whitelist", "doi").split()
