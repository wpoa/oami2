#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xml.etree.ElementTree import ElementTree

def find_supplementary_materials(content):
    """
    Parses PubMed XML and returns supplementary materials.
    """
    result = {}
    result['materials'] = []

    tree = ElementTree()
    tree.parse(content)
    for xref in tree.iter('xref'):
        try:
            if xref.attrib['ref-type'] == 'supplementary-material':
                rid = xref.attrib['rid']
                sup = get_supplementary_material(tree, rid)
                if sup is not None:
                    result['materials'].append(sup)
        except KeyError:  # xref has no ref-type
            pass

    if (result['materials'] == []):
        return None

    if get_article_license_url(tree) is None:
        return None

    result['title'] = get_article_title(tree)
    result['abstract'] = get_article_abstract(tree)

    result['license-holder'] = get_article_license_holder(tree)
    result['license-url'] = get_article_license_url(tree)
    result['license-year'] = get_article_license_year(tree)

    result['journal-id'] = get_journal_id(tree)
    result['journal-issn'] = get_journal_issn(tree)
    result['journal-publisher'] = get_journal_publisher(tree)
    result['journal-title'] = get_journal_title(tree)

    if ('Malaria' in result['abstract'] or
        'Malaria' in result['title']):
        print result


def get_supplementary_material(tree, rid):
    """
    Given an ElementTree and an rid, returns supplementary material.
    """
    for sup in tree.iter('supplementary-material'):
        try:
            if sup.attrib['id'] == rid:
                media = ElementTree(sup).find('media')
                if media is not None:
                    result = {}
                    result['mimetype'] = media.attrib['mimetype']
                    result['url'] = get_supplementary_material_url(
                        get_pmcid(tree),
                        media.attrib['{http://www.w3.org/1999/xlink}href']
                    )
                    return result
        except KeyError:  # supplementary material has no ID
            return None
    return None


def get_article_title(tree):
    """
    Given an ElementTree, returns article title.
    """
    front = ElementTree(tree).find('front')
    for title in front.iter('article-title'):
        return title.text


def get_article_abstract(tree):
    """
    Given an ElementTree, returns article abstract.
    """
    result = []
    front = ElementTree(tree).find('front')
    for abstract in front.iter('abstract'):
        for element in abstract.iter():
            if element.text is not None:
                result.append(element.text)
    return result


def get_article_license_url(tree):
    """
    Given an ElementTree, returns article license URL.
    """
    front = ElementTree(tree).find('front')
    for permissions in front.iter('permissions'):
        for license in permissions.iter('license'):
            try:
                return license.attrib['{http://www.w3.org/1999/xlink}href']
            except KeyError:  # license in plain text
                return None


def get_article_license_holder(tree):
    """
    Given an ElementTree, returns article license holder.
    """
    front = ElementTree(tree).find('front')
    for permissions in front.iter('permissions'):
        for copyright_holder in permissions.iter('copyright-holder'):
            return copyright_holder.text


def get_article_license_year(tree):
    """
    Given an ElementTree, returns article copyright year
    """
    front = ElementTree(tree).find('front')
    for permissions in front.iter('permissions'):
        for copyright_year in permissions.iter('copyright-year'):
            return copyright_year.text


def get_article_copyright_holder(tree):
    """
    Given an ElementTree, return article copyright holder.
    """
    front = ElementTree(tree).find('front')
    for permissions in front.iter('permissions'):
        for copyright_holder in permissions.iter('copyright-holder'):
            return copyright_holder.text


def get_journal_id(tree):
    """
    Given an ElementTree, return journal ID.
    """
    front = ElementTree(tree).find('front')
    for journal_meta in front.iter('journal-meta'):
        for journal_id in journal_meta.iter('journal-id'):
            return journal_id.text


def get_journal_title(tree):
    """
    Given an ElementTree, return journal title.
    """
    front = ElementTree(tree).find('front')
    for journal_meta in front.iter('journal-meta'):
        for journal_title in journal_meta.iter('journal-title'):
            return journal_title.text


def get_journal_issn(tree):
    """
    Given an ElementTree, return journal ISSN.
    """
    front = ElementTree(tree).find('front')
    for journal_meta in front.iter('journal-meta'):
        for issn in journal_meta.iter('issn'):
            return issn.text


def get_journal_publisher(tree):
    """
    Given an ElementTree, return journal publisher.
    """
    front = ElementTree(tree).find('front')
    for journal_meta in front.iter('journal-meta'):
        for publisher_name in journal_meta.iter('publisher-name'):
            return publisher_name.text


def get_pmcid(tree):
    """
    Given an ElementTree, returns PubMed Central ID.
    """
    front = ElementTree(tree).find('front')
    for aid in front.iter('article-id'):
        if aid.attrib['pub-id-type'] == 'pmc':
            return aid.text


def get_supplementary_material_url(pmcid, href):
    """
    This function creates absolute URIs for supplementary materials,
    using a PubMed Central ID and a relative URI.
    """
    return str('http://www.ncbi.nlm.nih.gov/pmc/articles/PMC' + pmcid +
        '/bin/' + href)
