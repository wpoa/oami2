#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen, urlparse, Request, HTTPError
from xml.etree.cElementTree import dump, ElementTree

def _get_file_from_url(url):
    req = Request(url, None, {'User-Agent' : 'oa-put/2012-08-15'})
    try:
        remote_file = urlopen(req)
        return remote_file
    except HTTPError as e:
        stderr.write('When trying to download <%s>, the following error occured: “%s”.\n' % \
            (url, str(e)))
        exit(255)

def get_pmcid_from_doi(doi):
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=%s' % doi
    xml_file = _get_file_from_url(url)
    tree = ElementTree()
    tree.parse(xml_file)
    return tree.find('IdList/Id').text

def get_pmid_from_doi(doi):
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s' % doi
    xml_file = _get_file_from_url(url)
    tree = ElementTree()
    tree.parse(xml_file)
    return tree.find('IdList/Id').text

def _postprocess_category(category):
    if ',' in category:
       category_parts = category.split(',')
       category_parts.reverse()
       category = ' '.join(category_parts)
    category = category.strip().lower().capitalize()
    return category

def get_categories_from_pmid(pmid):
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=%s&retmode=xml' % pmid
    xml_file = _get_file_from_url(url)
    tree = ElementTree()
    tree.parse(xml_file)
    categories = []
    for e in tree.iterfind('PubmedArticle/MedlineCitation/MeshHeadingList/MeshHeading/DescriptorName'):
        category = _postprocess_category(e.text)
        categories.append(category)
    return categories

def get_major_category_from_pmid(pmid):
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=%s&retmode=xml' % pmid
    xml_file = _get_file_from_url(url)
    tree = ElementTree()
    tree.parse(xml_file)
    for e in tree.iterfind('PubmedArticle/MedlineCitation/MeshHeadingList/MeshHeading/DescriptorName'):
        if e.attrib['MajorTopicYN'] == 'Y':
            return _postprocess_category(e.text)
