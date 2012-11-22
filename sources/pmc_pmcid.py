#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen, urlparse, Request, HTTPError
from xml.etree.cElementTree import dump, ElementTree
from os import listdir, path
from sys import stdin, stderr

from pmc import _get_article_contrib_authors, _get_article_title, _get_article_abstract, \
    _get_journal_title, _get_article_date, _get_article_url, _get_article_licensing, \
    _get_article_copyright_holder, _get_supplementary_materials, _get_pmcid, _get_article_doi, \
    _get_article_categories

from pmc_doi import _get_file_from_url, _get_query_url_from_pmcids, _get_file_from_pmcids

def download_metadata(target_directory):
    """
    Downloads XML files for PMCIDs on stdin into given directory.
    """
    stderr.write('Input PMCIDs, delimited by whitespace: ')
    pmcids = stdin.read().split()
    if len(pmcids) == 0:
        raise RuntimeError, 'No PMCIDs found.'

    url = _get_query_url_from_pmcids(pmcids)
    yield { 'url': url, 'completed': 0, 'total': 1 }

    url_path = urlparse.urlsplit(url).path
    local_filename = path.join(target_directory, \
        url_path.split('/')[-1])
    with open(local_filename, 'wb') as local_file:
        content = _get_file_from_pmcids(pmcids)
        local_file.write(content.read())
        yield { 'url': url, 'completed': 1, 'total': 1 }


def list_articles(target_directory, supplementary_materials=False, skip=[]):
    listing = listdir(target_directory)
    for filename in listing:
        result_tree = ElementTree()
        result_tree.parse(path.join(target_directory, filename))
        for tree in result_tree.iterfind('article'):
            pmcid = _get_pmcid(tree)
            if pmcid in skip:
                continue

            result = {}
            result['name'] = pmcid
            result['doi'] = _get_article_doi(tree)
            result['article-categories'] = _get_article_categories(tree)
            result['article-contrib-authors'] = _get_article_contrib_authors(tree)
            result['article-title'] = _get_article_title(tree)
            result['article-abstract'] = _get_article_abstract(tree)
            result['journal-title'] = _get_journal_title(tree)
            result['article-year'], \
                result['article-month'], \
                result['article-day'] = _get_article_date(tree)
            result['article-url'] = _get_article_url(tree)
            result['article-license-url'], \
                result['article-license-text'], \
                result['article-copyright-statement'] = _get_article_licensing(tree)
            result['article-copyright-holder'] = _get_article_copyright_holder(tree)

            if supplementary_materials:
                result['supplementary-materials'] = _get_supplementary_materials(tree)
            yield result
