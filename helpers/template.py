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

def _get_pmcid_from_doi(doi):
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=%s' % doi
    xml_file = _get_file_from_url(url)
    tree = ElementTree()
    tree.parse(xml_file)
    return tree.find('IdList/Id').text

def _get_pmid_from_doi(doi):
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s' % doi
    xml_file = _get_file_from_url(url)
    tree = ElementTree()
    tree.parse(xml_file)
    return tree.find('IdList/Id').text

def _get_categories_from_pmid(pmid):
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=%s&retmode=xml' % pmid
    xml_file = _get_file_from_url(url)
    tree = ElementTree()
    tree.parse(xml_file)
    categories = []
    for e in tree.iterfind('PubmedArticle/MedlineCitation/MeshHeadingList/MeshHeading/DescriptorName'):
        category = e.text
        if ',' in category:
            category_parts = category.split(',')
            category_parts.reverse()
            category = ' '.join(category_parts)
        category = category.lower().capitalize()
        categories.append(category)
    return categories

def page(article_doi, authors, article_title, journal_title, date, article_url, \
    license_url, rights_holder, label, caption):
    license_templates = {
        u'http://creativecommons.org/licenses/by/2.0/': '{{cc-by-2.0}}',
        u'http://creativecommons.org/licenses/by-sa/2.0/': '{{cc-by-sa-2.0}}',
        u'http://creativecommons.org/licenses/by/2.5/': '{{cc-by-2.5}}',
        u'http://creativecommons.org/licenses/by-sa/2.5/': '{{cc-by-sa-2.5}}',
        u'http://creativecommons.org/licenses/by/3.0/': '{{cc-by-3.0}}',
        u'http://creativecommons.org/licenses/by-sa/3.0/': '{{cc-by-sa-3.0}}'
    }
    license_template = license_templates[license_url]

    text = "=={{int:filedesc}}==\n\n"
    text += "{{Information\n"
    text += "|Description=\n{{en|%s}}\n" % caption
    text += "|Date= %s\n" % date
    if label:
        text += "|Source= %s from " % label
    else:
        text += "|Source= "
    text += "{{Cite journal\n"
    text += "| author = %s\n" % authors
    text += "| title = %s\n" % article_title
    text += "| doi = %s\n" % article_doi
    text += "| journal = %s\n" % journal_title
    pmid = _get_pmid_from_doi(article_doi)
    if pmid:
        text += "| pmid = %s\n" % pmid
    pmcid = _get_pmcid_from_doi(article_doi)
    if pmcid:
        text += "| pmc = %s\n" % pmcid
    text += "}}\n"
    text += "|Author= %s\n" % authors
    text += "|Permission= %s Copyright owner: %s\n" % \
        (license_template, rights_holder)
    text += "|Other_fields={{Information field|name=Provenance|value= {{Open Access Media Importer}} }}\n"
    text += "}}\n\n"
    if pmid:
        for category in _get_categories_from_pmid(pmid):
            text += "[[Category:%s]]\n" % category
    text += "[[Category:Media from %s]]\n" % journal_title
    text += "[[Category:Uploaded with Open Access Media Importer]]"
    return text
