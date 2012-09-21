#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xml.etree.cElementTree import dump, ElementTree
from os import path
from sys import stdin, stderr

from pmc import _get_article_contrib_authors, _get_article_title, _get_article_abstract, \
    _get_journal_title, _get_article_date, _get_article_url, _get_article_license_url, \
    _get_article_copyright_holder, _get_supplementary_materials, _get_pmcid, _get_article_doi

def download_metadata(target_directory):
    """
    Writes XML into a directory.
    """
    stderr.write('Input XML: ')
    xml = stdin.read()

    yield { 'url': '', 'completed': 0, 'total': 1 }
    local_filename = path.join(target_directory, 'file.xml')
    with open(local_filename, 'wb') as local_file:
        local_file.write(xml)
        yield { 'url': '', 'completed': 1, 'total': 1 }


def list_articles(target_directory, supplementary_materials=False, skip=[]):
    result_tree = ElementTree()
    result_tree.parse(path.join(target_directory, 'file.xml'))
    for tree in [result_tree]:
        result = {}
        result['name'] = _get_article_doi(tree)
        result['doi'] = _get_article_doi(tree)
        result['article-contrib-authors'] = _get_article_contrib_authors(tree)
        result['article-title'] = _get_article_title(tree)
        result['article-abstract'] = _get_article_abstract(tree)
        result['journal-title'] = _get_journal_title(tree)
        result['article-date'] = _get_article_date(tree)
        result['article-url'] = _get_article_url(tree)
        result['article-license-url'] = _get_article_license_url(tree)
        result['article-copyright-holder'] = _get_article_copyright_holder(tree)

        if supplementary_materials:
            result['supplementary-materials'] = _get_supplementary_materials(tree)
        yield result
