#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen, urlparse, Request, HTTPError
from xml.etree.cElementTree import dump, ElementTree
from os import listdir, path
from sys import stdin, stderr

from pmc import _get_article_contrib_authors, _get_article_title, _get_article_abstract, \
    _get_journal_title, _get_article_date, _get_article_url, _get_article_license_url, \
    _get_article_copyright_holder, _get_supplementary_materials, _get_pmcid, _get_article_doi, \
    _get_article_categories

def _get_file_from_url(url):
    req = Request(url, None, {'User-Agent' : 'pmc_doi/2012-07-14'})
    try:
        remote_file = urlopen(req)
        return remote_file
    except HTTPError as e:
        stderr.write('When trying to download <%s>, the following error occured: “%s”.\n' % \
            (url, str(e)))
        exit(255)

def _get_pmcids_from_dois(dois):
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=%s' % \
        '%20OR%20'.join([doi+'[doi]' for doi in dois])
    xml_file = _get_file_from_url(url)
    tree = ElementTree()
    tree.parse(xml_file)
    pmcids = []
    for e in tree.iterfind('IdList/Id'):
        pmcids.append(e.text)
    return pmcids

def _get_query_url_from_pmcids(pmcids):
    return 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=%s' % \
        '&id='.join(pmcids)

def _get_file_from_pmcids(pmcids):
    url = _get_query_url_from_pmcids(pmcids)
    xml_file = _get_file_from_url(url)
    return xml_file

def download_metadata(target_directory):
    """
    Downloads XML files for  into given directory.
    """
    stderr.write('Input DOIs, delimited by whitespace: ')
    dois = stdin.read().split()

    stderr.write('Getting PubMed Central IDs for given DOIs … ')
    pmcids = _get_pmcids_from_dois(dois)
    stderr.write('found: %s\n' % ', '.join(pmcids))

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
            result['article-license-url'] = _get_article_license_url(tree)
            result['article-copyright-holder'] = _get_article_copyright_holder(tree)

            if supplementary_materials:
                result['supplementary-materials'] = _get_supplementary_materials(tree)
            yield result
