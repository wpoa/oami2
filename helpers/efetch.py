#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.parse import urlparse #Request, HTTPError #urlopen
from xml.etree.cElementTree import dump, ElementTree
from sys import stderr
import requests
import urlopen
from urllib.error import HTTPError

def _get_file_from_url(url):
    req = requests(url, None, {'User-Agent' : 'oa-put/2012-08-15'})
    try:
        remote_file = urlopen(req)
        return remote_file
    except HTTPError as e:
        print('When trying to download <%s>, the following error occured: “%s”.\n' % \
            (url, str(e)))
        exit(255)

def get_pmcid_from_doi(doi):
    if not isinstance(doi, str):
        raise TypeError("Cannot get PMCID for DOI %s of type %s." % (doi, type(doi)))
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=%s' % doi
    xml_file = _get_file_from_url(url)
    tree = ElementTree()
    tree.parse(xml_file)
    try:
        return int(tree.find('IdList/Id').text)
    except AttributeError:
        return None

def get_pmid_from_doi(doi):
    if not isinstance(doi, str):
        raise TypeError("Cannot get PMID for DOI %s of type %s." % (doi, type(doi)))
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s' % doi
    xml_file = _get_file_from_url(url)
    tree = ElementTree()
    tree.parse(xml_file)
    try:
        return int(tree.find('IdList/Id').text)
    except AttributeError:
        return None

def get_categories_from_pmid(pmid):
    """
    Gets MeSH headings, returns those not deemed too broad.
    """
    if not type(pmid) == int:
        raise TypeError("Cannot get Categories for PMID %s of type %s." % (pmid, type(pmid)))
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=%s&retmode=xml' % pmid
    xml_file = _get_file_from_url(url)
    tree = ElementTree()
    tree.parse(xml_file)
    categories = []
    for heading in tree.iterfind('PubmedArticle/MedlineCitation/MeshHeadingList/MeshHeading'):
        htree = ElementTree(heading)
        descriptor_text = htree.find('DescriptorName').text
        if (htree.find('QualifierName') is not None) or \
            (' ' in descriptor_text and not 'and' in descriptor_text):
            categories.append(descriptor_text)
    return categories