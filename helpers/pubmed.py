#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xml.etree.ElementTree import ElementTree

def find_supplementary_materials(content):
    """
    Parses PubMed XML and returns URLs of supplementary materials.
    """
    urllist = []

    tree = ElementTree()
    tree.parse(content)
    for xref in tree.iter('xref'):
        try:
            if xref.attrib['ref-type'] == 'supplementary-material':
                rid = xref.attrib['rid']
                for sup in tree.iter('supplementary-material'):
                    if sup.attrib['id'] == rid:
                        media = ElementTree(sup).find('media')
                        if media.attrib['mimetype'] in ('audio', 'video'):
                            href = media.attrib['{http://www.w3.org/1999/xlink}href']
                            for aid in tree.iter('article-id'):
                                if aid.attrib['pub-id-type'] == 'pmc':
                                    PMCID = aid.text
                                    url = PubMed_absolute_URL(PMCID, href)
                                    urllist.append(url)
        except KeyError:
            pass
        except AttributeError:
            pass
    return urllist


def PubMed_absolute_URL(PMCID, href):
    """
    This function creates absolute URIs for supplementary materials,
    using a PubMed Central ID and a relative URI.
    """
    PREFIX = 'http://www.ncbi.nlm.nih.gov/pmc/articles/PMC'
    SUFFIX = '/bin/'

    return str(PREFIX + PMCID + SUFFIX + href)
