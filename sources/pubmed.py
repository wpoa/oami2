#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date
from os import listdir, path
from urllib2 import urlopen, urlparse
from xml.etree.cElementTree import dump, ElementTree
# the C implementation of ElementTree is 5 to 20 times faster than the Python one

from hashlib import md5

import tarfile

# According to <ftp://ftp.ncbi.nlm.nih.gov/README.ftp>, this should be
# 33554432 (32MiB) for best performance. Note that on slow connections,
# however, huge buffers size leads to notable interface lag.
BUFSIZE = 33554432
#BUFSIZE = 1024000  # (1024KB)

def download_metadata(target_directory):
    """
    Downloads files from PubMed FTP server into given directory.
    """
    urls = [
        'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/articles.A-B.tar.gz',
        'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/articles.C-H.tar.gz',
        'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/articles.I-N.tar.gz',
        'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/articles.O-Z.tar.gz'
    ]

    for url in urls:
        remote_file = urlopen(url)
        total = int(remote_file.headers['content-length'])
        completed = 0

        url_path = urlparse.urlsplit(url).path
        local_filename = path.join(target_directory, \
            url_path.split('/')[-1])

        # if local file has same size as remote file, skip download
        try:
            if (path.getsize(local_filename) == total):
                continue
        except OSError:  # local file does not exist
            pass

        with open(local_filename,'wb') as local_file:
            while True:
                chunk = remote_file.read(BUFSIZE)
                if chunk != '':
                    local_file.write(chunk)
                    completed += len(chunk)
                    yield {
                        'url': url,
                        'completed': completed,
                        'total': total
                    }
                else:
                    break

def list_articles(target_directory, supplementary_materials=False, skip=[]):
    """
    Iterates over archive files in target_directory, yielding article information.
    """
    listing = listdir(target_directory)
    for filename in listing:
        with tarfile.open(path.join(target_directory, filename)) as archive:
            for item in archive:
                if item.name in skip:
                    continue
                if path.splitext(item.name)[1] == '.nxml':
                    content = archive.extractfile(item)
                    tree = ElementTree()
                    tree.parse(content)

                    result = {}
                    result['name'] = item.name
                    skip.append(item.name)  # guard against duplicate input
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

def _get_article_contrib_authors(tree):
    from sys import stderr
    """
    Given an ElementTree, returns article authors in a format suitable for citation.
    """
    authors = []
    front = ElementTree(tree).find('front')
    for contrib in front.iter('contrib'):
        contribTree = ElementTree(contrib)
        try:
            surname = contribTree.find('name/surname').text
        except AttributeError:  # author is not a natural person
            try:
                citation_name = contribTree.find('collab').text
                if citation_name is not None:
                    authors.append(citation_name)
                continue
            except AttributeError:  # name has no immediate text node
                continue

        try:
            given_names = contribTree.find('name/given-names').text
            citation_name = ' '.join([surname, given_names[0]])
        except AttributeError:  # no given names
            citation_name = surname
        except TypeError:  # also no given names
            citation_name = surname
        if citation_name is not None:
            authors.append(citation_name)

    return ', '.join(authors)

def _get_article_title(tree):
    """
    Given an ElementTree, returns article title.
    """
    title = ElementTree(tree).find('front/article-meta/title-group/article-title')
    if title is None:
        title = ElementTree(tree).find('front/article-meta/article-categories/subj-group/subject')
    return ' '.join(title.itertext())

def _get_article_abstract(tree):
    """
    Given an ElementTree, returns article abstract.
    """
    abstract = ElementTree(tree).find('front/article-meta/abstract')
    if abstract is not None:
        return ' '.join(abstract.itertext())
    else:
        return None

def _get_journal_title(tree):
    """
    Given an ElementTree, returns journal title.
    """
    front = ElementTree(tree).find('front')
    for journal_meta in front.iter('journal-meta'):
        for journal_title in journal_meta.iter('journal-title'):
            return journal_title.text.replace('PLoS', 'PLOS').replace('PloS', 'PLOS')

def _get_article_date(tree):
    """
    Given an ElementTree, returns article date.
    """
    article_meta = ElementTree(tree).find('front/article-meta')
    for pub_date in article_meta.iter('pub-date'):
        if pub_date.attrib['pub-type'] == 'epub':
            pub_date_tree = ElementTree(pub_date)
            year = int(pub_date_tree.find('year').text)
            try:
                month = int(pub_date_tree.find('month').text)
            except AttributeError:
                month = 1 # TODO: is this correct?
            try:
                day = int(pub_date_tree.find('day').text)
            except AttributeError:
                day = 1  # TODO: is this correct?
            return str(date(year, month, day))
    return None

def _get_article_url(tree):
    """
    Given an ElementTree, returns article URL.
    """
    doi = _get_article_doi(tree)
    if doi:
        return 'http://dx.doi.org/' + doi

license_url_equivalents = {
    '>This work is licensed under a Creative Commons Attribution NonCommercial 3.0 License (CC BY-NC 3.0). Licensee PAGEPress, Italy': 'http://creativecommons.org/licenses/by-nc/3.0',
     'Available freely online through the author-supported open access option.': None,
     'Distributed under the Hogrefe OpenMind License [ http://dx.doi.org/10.1027/a000001]': 'http://dx.doi.org/10.1027/a000001',
     'Freely available online through the American Journal of Tropical Medicine and Hygiene Open Access option.': None,
     'License information: This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0',
     'Open Access': None,
     'Readers may use this article as long as the work is properly cited, the use is educational and not for profit, and the work is not altered. See http://creativecommons.org/licenses/by -nc-nd/3.0/ for details.': 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
     'Readers may use this article as long as the work is properly cited, the use is educational and not for profit, and the work is not altered. See http://creativecommons.org/licenses/by-nc-nd/3.0/ for details.': 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
     'Readers may use this article as long as the work is properly cited, the use is educational and not for profit,and the work is not altered. See http://creativecommons.org/licenses/by-nc-nd/3.0/ for details.': 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
     'Readers may use this article aslong as long as the work is properly cited, the use is educational and not for profit, and the work is not altered. See http://creativecommons.org/licenses/by-nc-nd/3.0/ for details.': 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
     'The authors have paid a fee to allow immediate free access to this article.': None,
     'The online version of this article has been published under an open access model, users are entitle to use, reproduce, disseminate, or display the open access version of this article for non-commercial purposes provided that: the original authorship is properly and fully attributed; the Journal and the European Society for Medical Oncology are attributed as the original place of publication with the correct citation details given; if an article is subsequently reproduced or disseminated not in its entirety but only in part or as a derivative work this must be clearly indicated. For commercial re-use, please contact journals.permissions@oxfordjournals.org': 'mailto:journals.permissions@oxfordjournals.org',
     'The online version of this article has been published under an open access model. Users are entitled to use, reproduce, disseminate, or display the open access version of this article for non-commercial purposes provided that: the original authorship is properly and fully attributed; the Journal and Oxford University Press are attributed as the original place of publication with the correct citation details given; if an article is subsequently reproduced or disseminated not in its entirety but only in part or as a derivative work this must be clearly indicated. For commercial re-use, please contact journals.permissions@oxfordjournals.org': 'mailto:journals.permissions@oxfordjournals.org',
     'The online version of this article has been published under an open access model. Users are entitled to use, reproduce, disseminate, or display the open access version of this article for non-commercial purposes provided that: the original authorship is properly and fully attributed; the Journal and Oxford University Press are attributed as the original place of publication with the correct citation details given; if an article is subsequently reproduced or disseminated not in its entirety but only in part or as a derivative work this must be clearly indicated. For commercial re-use, please contact journals.permissions@oxfordjournals.org.': 'mailto:journals.permissions@oxfordjournals.org',
     'The online version of this article has been published under an open access model. users are entitle to use, reproduce, disseminate, or display the open access version of this article for non-commercial purposes provided that: the original authorship is properly and fully attributed; the Journal and the European Society for Medical Oncology are attributed as the original place of publication with the correct citation details given; if an article is subsequently reproduced or disseminated not in its entirety but only in part or as a derivative work this must be clearly indicated. For commercial re-use, please contact journals.permissions@oxfordjournals.org': 'mailto:journals.permissions@oxfordjournals.org',
     'The online version of this article is published within an Open Access environment subject to the conditions of the Creative Commons Attribution-NonCommercial-ShareAlike licence < http://creativecommons.org/licenses/by-nc-sa/2.5/>. The written permission of Cambridge University Press must be obtained for commercial re-use': 'http://creativecommons.org/licenses/by-nc-sa/2.5/',
     'The online version of this article is published within an Open Access environment subject to the conditions of the Creative Commons Attribution-NonCommercial-ShareAlike licence < http://creativecommons.org/licenses/by-nc-sa/2.5/>. The written permission of Cambridge University Press must be obtained for commercial re-use.': 'http://creativecommons.org/licenses/by-nc-sa/2.5/',
     'Thi is an open access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This article is an open-access article distributed under the terms and conditions of the Creative Commons Attribution license ( http://creativecommons.org/licenses/by/3.0/ ).': 'http://creativecommons.org/licenses/by/3.0/',
     'This article is in the public domain.': 'http://creativecommons.org/licenses/publicdomain/',
     'This article, manuscript, or document is copyrighted by the American Psychological Association (APA). For non-commercial, education and research purposes, users may access, download, copy, display, and redistribute this article or manuscript as well as adapt, translate, or data and text mine the content contained in this document. For any such use of this document, appropriate attribution or bibliographic citation must be given. Users should not delete any copyright notices or disclaimers. For more information or to obtain permission beyond that granted here, visit http://www.apa.org/about/copyright.html.': 'http://www.apa.org/about/copyright.html',
     'This document may be redistributed and reused, subject to certain conditions .': None,
     'This document may be redistributed and reused, subject to www.the-aps.org/publications/journals/funding_addendum_policy.htm .': 'http://www.the-aps.org/publications/journals/funding_addendum_policy.htm',
     'This is a free access article, distributed under terms ( http://www.nutrition.org/publications/guidelines-and-policies/license/ ) which permit unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://www.nutrition.org/publications/guidelines-and-policies/license/',
     'This is a free access article, distributed under terms that permit unrestricted noncommercial use, distribution, and reproduction in any medium, provided the original work is properly cited. http://www.nutrition.org/publications/guidelines-and-policies/license/ .': 'http://www.nutrition.org/publications/guidelines-and-policies/license/',
     "This is an Open Access article distributed under the terms and of the American Society of Tropical Medicine and Hygiene's Re-use License which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.": None,
     "This is an Open Access article distributed under the terms of the American Society of Tropical Medicine and Hygiene's Re-use License which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.": None,
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution License ( http://creativecommons.org/licenses/by/2.0 ), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/2.0',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution License ( http://creativecommons.org/licenses/by/3.0 ), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<url>http://creativecommons.org/licenses/by/2.0</url>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/2.0',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/2.0), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/2.0',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.0 ), which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.0',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.0/ ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.0/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.0/uk/ ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.0/uk/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.0/uk/ ), which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.0/uk/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.5 ), which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.5',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.5/ ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.5/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.5/ ), which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.5/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.5/uk/ ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.5/uk/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.5/uk/ ), which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.5/uk/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/3.0 ), which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/3.0',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/3.0/ ), which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/3.0/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/3.0/us/ ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/3.0/us/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses?by-nc/2.5 ), which permits unrestricted non-commercial use distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses?by-nc/2.5',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial Share Alike License ( http://creativecommons.org/licenses/by-nc-sa/3.0 ), which permits unrestricted non-commercial use, distribution and reproduction in any medium provided that the original work is properly cited and all further distributions of the work or adaptation are subject to the same Creative Commons License terms': 'http://creativecommons.org/licenses/by-nc-sa/3.0',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial Share Alike License ( http://creativecommons.org/licenses/by-nc-sa/3.0 ), which permits unrestricted non-commercial use, distribution and reproduction in any medium provided that the original work is properly cited and all further distributions of the work or adaptation are subject to the same Creative Commons License terms.': 'http://creativecommons.org/licenses/by-nc-sa/3.0',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution licence which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution-Noncommercial License ( http://creativecommons.org/licenses/by-nc/3.0/ ), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited. Information for commercial entities is available online ( http://www.chestpubs.org/site/misc/reprints.xhtml ).': 'http://creativecommons.org/licenses/by-nc/3.0/',
     'This is an Open Access article which permits unrestricted noncommercial use, provided the original work is properly cited.': None,
     'This is an Open Access article which permits unrestricted noncommercial use, provided the original work is properly cited. Clinical Ophthalmology 2011:5 101\xe2\x80\x93108': None,
     'This is an Open Access article: verbatim copying and redistribution of this article are permitted in all media for any purpose': None,
     'This is an open access article distributed under the Creative Commons Attribution License, in which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0',
     'This is an open access article distributed under the Creative Commons Attribution License, which permits unrestricted use, distribution and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This is an open access article distributed under the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This is an open access article distributed under the Creative Commons attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This is an open access article distributed under the terms of the Creative Commons Attribution License ( http://creativecommons.org/licenses/by/2.0 ), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/2.0',
     'This is an open access article distributed under the terms of the Creative Commons Attribution License ( http://www.creativecommons.org/licenses/by/2.0 ) which permits unrestricted use, distribution and reproduction provided the original work is properly cited.': 'http://www.creativecommons.org/licenses/by/2.0',
     'This is an open access article distributed under the terms of the Creative Commons Attribution License (<url>http://creativecommons.org/licenses/by/2.0</url>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/2.0',
     'This is an open access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/2.0), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/2.0',
     'This is an open access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This is an open access article distributed under theCreative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This is an open access article. Unrestricted non-commercial use is permitted provided the original work is properly cited.': None,
     'This is an open access paper distributed under the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0',
     'This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This is an open-access article distributed under the terms of the Creative Commons Attribution Non-commercial License, which permits use, distribution, and reproduction in any medium, provided the original work is properly cited, the use is non commercial and is otherwise in compliance with the license. See: http://creativecommons.org/licenses/by-nc/2.0/ and http://creativecommons.org/licenses/by-nc/2.0/legalcode .': 'http://creativecommons.org/licenses/by-nc/2.0/',
     'This research note is distributed under the Commons Attribution-Noncommercial 3.0 License.': 'http://creativecommons.org/licenses/by-nc/3.0/',
     'This research note is distributed under the Creative Commons Attribution 3.0 License.': 'http://creativecommons.org/licenses/by/3.0',
     'This work is licensed under a Creative Commons Attr0ibution 3.0 License (by-nc 3.0). Licensee PAGE Press, Italy': 'http://creativecommons.org/licenses/by-nc/3.0',
     'This work is licensed under a Creative Commons Attribution 3.0 License (by-nc 3.0) Licensee PAGEPress, Italy': 'http://creativecommons.org/licenses/by-nc/3.0',
     'This work is licensed under a Creative Commons Attribution 3.0 License (by-nc 3.0). Licensee PAGE Press, Italy': 'http://creativecommons.org/licenses/by-nc/3.0',
     'This work is licensed under a Creative Commons Attribution 3.0 License (by-nc 3.0). Licensee PAGEPress, Italy': 'http://creativecommons.org/licenses/by-nc/3.0',
     'This work is licensed under a Creative Commons Attribution NonCommercial 3.0 License (CC BY-NC 3.0). Licensee PAGEPress srl, Italy': 'http://creativecommons.org/licenses/by-nc/3.0',
     'This work is licensed under a Creative Commons Attribution NonCommercial 3.0 License (CC BY-NC 3.0). Licensee PAGEPress, Italy': 'http://creativecommons.org/licenses/by-nc/3.0',
     'This work is subject to copyright. All rights are reserved, whether the whole or part of the material is concerned, specifically the rights of translation, reprinting, reuse of illustrations, recitation, broadcasting, reproduction on microfilm or in any other way, and storage in data banks. Duplication of this publication or parts thereof is permitted only under the provisions of the German Copyright Law of September 9, 1965, in its current version, and permission for use must always be obtained from Springer-Verlag. Violations are liable for prosecution under the German Copyright Law.': None,
     'This work is subject to copyright. All rights are reserved, whether the whole or part of the material is concerned, specifically the rights of translation, reprinting, reuse of illustrations, recitation, broadcasting, reproduction on microfilm or in any other way, and storage in data banks. Duplication of this publication or parts thereof is permitted only under the provisions of the German Copyright Law of September 9, in its current version, and permission for use must always be obtained from Springer-Verlag. Violations are liable for prosecution under the German Copyright Law.': None,
     'Users may view, print, copy, download and text and data- mine the content in such documents, for the purposes of academic research, subject always to the full Conditions of use: http://www.nature.com/authors/editorial_policies/license.html#terms': 'http://www.nature.com/authors/editorial_policies/license.html#terms',
     'creative commons': None,
     '\xc2\xa7 The authors have paid a fee to allow immediate free access to this article.': None,
     '\xe2\x80\x96 The authors have paid a fee to allow immediate free access to this article.': None,
     '\xe2\x80\x96The authors have paid a fee to allow immediate free access to this article.': None,
     '\xe2\x80\xa0 The author has paid a fee to allow immediate free access to this article.': None,
     '\xe2\x80\xa0 The authors have paid a fee to allow immediate free access to this article.': None,
     '\xe2\x80\xa0The authors have paid a fee to allow immediate free access to this article.': None,
     '\xe2\x80\xa1 The authors have paid a fee to allow immediate free access to this article': None,
     '\xe2\x80\xa1 The authors have paid a fee to allow immediate free access to this article.': None,
     '\xe2\x80\xa1The authors have paid a fee to allow immediate free access to this article.': None,
     "You are free to share–to copy, distribute and transmit the work, under the following conditions: Attribution :  You must attribute the work in the manner specified by the author or licensor (but not in any way that suggests that they endorse you or your use of the work). Non-commercial :  You may not use this work for commercial purposes. No derivative works :  You may not alter, transform, or build upon this work. For any reuse or distribution, you must make clear to others the license terms of this work, which can be found at http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode. Any of the above conditions can be waived if you get permission from the copyright holder. Nothing in this license impairs or restricts the author's moral rights.": 'http://creativecommons.org/licenses/by-nc-nd/3.0',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.5/uk/ ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited. This paper is available online free of all access charges (see http://jxb.oxfordjournals.org/open_access.html for further details)': 'http://creativecommons.org/licenses/by-nc/2.5/uk/',
     'Royal College of Psychiatrists, This paper accords with the Wellcome Trust Open Access policy and is governed by the licence available at http://www.rcpsych.ac.uk/pdf/Wellcome%20Trust%20licence.pdf' : 'http://www.rcpsych.ac.uk/pdf/Wellcome%20Trust%20licence.pdf',
     'This is an open access article distributed under the Creative Commons Attribution License,which permits unrestricted use,distribution,and reproduction in any medium,provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This paper is an open-access article distributed under the terms and conditions of the Creative Commons Attribution license ( http://creativecommons.org/licenses/by/3.0/ ).': 'http://creativecommons.org/licenses/by/3.0/',
     'This is an Open Access articlewhich permits unrestricted noncommercial use, provided the original work is properly cited.': None,
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-commercial License ( http://creativecommons.org/licences/by-nc/2.0/uk/ ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited. This paper is available online free of all access charges (see http://jxb.oxfordjournals.org/open_access.html for further details)': 'http://creativecommons.org/licences/by-nc/2.0/uk/',
     'This is an open access article distributed under the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work are properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<url>http://creativecommons.org/licenses/by/2.0</url>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited': 'http://creativecommons.org/licenses/by/2.0',
     'This work is licensed under a Creative Commons Attribution 3.0 License (by-nc 3.0).': 'http://creativecommons.org/licenses/by-nc/3.0',
     'The online version of this article has been published under an open access model. Users are entitled to use, reproduce, disseminate, or display the open access version of this article for non-commercial purposes provided that: the original authorship is properly and fully attributed; the Journal and Oxford University Press are attributed as the original place of publication with the correct citation details given; if an article is subsequently reproduced or disseminated not in its entirety but only in part or as a derivative work this must be clearly indicated. For commercial re-use, please contact journals.permissions@oupjournals.org': None,
     "Author's Choice - Final Version Full Access NIH Funded Research - Final Version Full Access Creative Commons Attribution Non-Commercial License applies to Author Choice Articles": 'http://creativecommons.org/licenses/by-nc/3.0',
     'The online version of this article has been published under an open access model. users are entitled to use, reproduce, disseminate, or display the open access version of this article for non-commerical purposes provided that: the original authorship is properly and fully attributed; the Journal and the Guarantors of Brain are attributed as the original place of publication with the correction citation details given; if an article is subsequently reproduced or disseminated not in its entirety but only in part or as a derivative work this must be clearly indicated. For commercial re-use, please contact journals.permissions@oxfordjournals.org.': 'mailto:journals.permissions@oxfordjournals.org',
     "You are free to share - to copy, distribute and transmit the work, under the following conditions: Attribution: You must attribute the work in the manner specified by the author or licensor (but not in any way that suggests that they endorse you or your use of the work). Non-commercial: You may not use this work for commercial purposes. No derivative works: You may not alter, transform, or build upon this work. For any reuse or distribution, you must make clear to others the license terms of this work, which can be found at http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode . Any of the above conditions can be waived if you get permission from the copyright holder. Nothing in this license impairs or restricts the author's moral rights.": 'http://creativecommons.org/licenses/by-nc-nd/3.0',
     'Open access articles can be viewed online without a subscription.': None,
     '‡ The authors have paid a fee to allow immediate free access to this work.': None,
     'Published under the CreativeCommons Attribution-NonCommercial-NoDerivs 3.0 License .': 'http://creativecommons.org/licenses/by-nc-nd/3.0',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.0/uk/ ) which permits unrestricted non-commercial use distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.0/uk/',
     'This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution license ( http://creativecommons.org/licenses/by/3.0/. )': 'http://creativecommons.org/licenses/by/3.0/',
     'This work is licensed under a Creative Commons Attribution 3.0 License (by-nc 3.0)': 'http://creativecommons.org/licenses/by-nc/3.0',
     "Author's Choice —Final version full access. NIH Funded Research - Final version full access. Creative Commons Attribution Non-Commercial License applies to Author Choice Articles": 'http://creativecommons.org/licenses/by-nc/3.0',
     'This is an open-access article, which permits unrestricted use, distribution, and reproduction in any medium, for non-commercial purposes, provided the original author and source are credited.': None,
     'This article is an open-access article distributed under the terms and conditions of the Creative Commons Attribution license ( http://creativecommons.org/licenses/by/3.0/ )': 'http://creativecommons.org/licenses/by/3.0/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial No Derivatives License ( http://creativecommons.org/licenses/by-nc-nd/3.0/ ), which permits for noncommercial use, distribution, and reproduction in any medium, provided the original work is properly cited and is not altered in any way.': 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
     'This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution license http://creativecommons.org/licenses/by/3.0/ .': 'http://creativecommons.org/licenses/by/3.0/',
     "You are free to share–to copy, distribute and transmit the work, under the following conditions: Attribution :  You must attribute the work in the manner specified by the author or licensor (but not in any way that suggests that they endorse you or your use of the work). Non-commercial :  You may not use this work for commercial purposes. No derivative works :  You may not alter, transform, or build upon this work. For any reuse or distribution, you must make clear to others the license terms of this work, which can be found at http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode . Any of the above conditions can be waived if you get permission from the copyright holder. Nothing in this license impairs or restricts the author's moral rights.": 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/y-nc/2.0/uk/ ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/y-nc/2.0/uk/',
     'This work is licensed under a Creative Commons Attribution Noncommercial 3.0 License (CC BYNC 3.0). Licensee PAGEPress, Italy': 'http://creativecommons.org/licenses/by-nc/3.0',
     'The online version of this article has been published under an open access model. Users are entitled to use, reproduce, disseminate, or display the open access version of this article for non-commercial purposes provided that: the original authorship is properly and fully attributed; the Journal and Oxford University Press are attributed as the original place of publication with the correct citation details given; if an article is subsequently reproduced or disseminated not in its entirety but only in part or as a derivative work this must be clearly indicated. For commercial re-use, please contact journals.permissions@oxfordjournals.org Published by Oxford University Press on behalf of the International Epidemiological Association': 'mailto:journals.permissions@oxfordjournals.org',
     'This is an open access article distributed under the Creative Commons Attribution License which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     "You are free to share - to copy, distribute and transmit the work, under the following conditions: Attribution:   You must attribute the work in the manner specified by the author or licensor (but not in any way that suggests that they endorse you or your use of the work). Non-commercial:   You may not use this work for commercial purposes. No derivative works:   You may not alter, transform, or build upon this work. For any reuse or distribution, you must make clear to others the license terms of this work, which can be found at http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode . Any of the above conditions can be waived if you get permission from the copyright holder. Nothing in this license impairs or restricts the author's moral rights.": 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
     'This article is distributed under the terms of an Attribution–Noncommercial–Share Alike–No Mirror Sites license for the first six months after the publication date (see http://www.jem.org/misc/terms.shtml ). After six months it is available under a Creative Commons License (Attribution–Noncommercial–Share Alike 3.0 Unported license, as described at http://creativecommons.org/licenses/by-nc-sa/3.0/ ).': 'http://www.jem.org/misc/terms.shtml',
     'The online version of this article has been published under an open access model. Users are entitled to use, reproduce, disseminate, or display the open access version of this article for noncommercial purposes provided that: the original authorship is properly and fully attributed; the Journal and Oxford University Press are attributed as the original place of publication with the correct citation details given; if an article is subsequently reproduced or disseminated not in its entirety but only in part or as a derivative work this must be clearly indicated. For commercial re-use, please contact journals.permissions@oxfordjournals.org': 'mailto:journals.permissions@oxfordjournals.org',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/byc/2.5 ), which permits unrestricted nonommercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.5/',
     'The online version of this article has been published under an open access model. Users are entitled to use, reproduce, disseminate, or display the open access version of this article for non-commercial purposes provided that: the original authorship is properly and fully attributed; the Journal and Oxford University Press and The Japanese Society for Immunology are attributed as the original place of publication with the correct citation details given; if an article is subsequently reproduced or disseminated not in its entirety but only in part or as a derivative work this must be clearly indicated. For commercial re-use, please contact journals.permissions@oxfordjournals.org': 'mailto:journals.permissions@oxfordjournals.org',
     '# The authors have paid a fee to allow immediate free access to this paper.': None,
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License (http://creativecommons.org/licenses/by-nc/2.0/uk/) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.0/uk/',
     'This work is licensed under a Creative Commons Attribution NonCommercial 3.0 License (CC BYNC 3.0). LicenseePAGEPress, Italy': 'http://creativecommons.org/licenses/by-nc/3.0',
     'This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution license ( http://creativecommons.org/licenses/by/3.0/ ).': 'http://creativecommons.org/licenses/by/3.0/',
     "Author's Choice - Final Version Full Access Creative Commons Attribution Non-Commercial License applies to Author Choice Articles": 'http://creativecommons.org/licenses/by-nc/3.0',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.0/uk/ ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited. This paper is available online free of all access charges (see http://jxb.oxfordjournals.org/open_access.html for further details)': 'http://creativecommons.org/licenses/by-nc/2.0/uk/',
     'This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution license ( http://creativecommons.org/licenses/by/3.0/ )': 'http://creativecommons.org/licenses/by/3.0/',
     'This is an open access article distributed under the Creative Commons Attribution License, that permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution license ( http://creativecommons.org/licenses/by/3.0/ .)': 'http://creativecommons.org/licenses/by/3.0/',
     "Author's Choice —Final version full access. Creative Commons Attribution Non-Commercial License applies to Author Choice Articles": 'http://creativecommons.org/licenses/by-nc/3.0',
     '¶ The authors have paid a fee to allow immediate free access to this article.': None,
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.5 ), which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited. This paper is available online free of all access charges (see http://jxb.oxfordjournals.org/open_access.html for further details)': 'http://creativecommons.org/licenses/by-nc/2.5',
     'This article is distributed under the terms of an Attribution–Noncommercial–Share Alike–No Mirror Sites license for the first six months after the publication date (see http://www.jcb.org/misc/terms.shtml ). After six months it is available under a Creative Commons License (Attribution–Noncommercial–Share Alike 3.0 Unported license, as described at http://creativecommons.org/licenses/by-nc-sa/3.0/ ).': 'http://creativecommons.org/licenses/by-nc-sa/3.0/',
     '99This is an open access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     "You are free to share–to copy, distribute and transmit the work, under the following conditions: Attribution :  You must attribute the work in the manner specified by the author or licensor (but not in any way that suggests that they endorse you or your use of the work). Non-commercial :  You may not use this work for commercial purposes. No derivative works :  You may not alter, transform, or build upon this work. For any reuse or distribution, you must make clear to others the license terms of this work, which can be found at http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode. Any of the above conditions can be waived if you get permission from the copyright holder. Nothing in this lincense impairs or restricts the author's moral rights.": 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
     'This is an open access article distributed under the terms of the creative commons attribution license, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'Royal College of Psychiatrists, This paper accords with the NIH Public Access policy and is governed by the licence available at http://www.rcpsych.ac.uk/pdf/NIH%20licence%20agreement.pdf Royal College of Psychiatrists, This paper accords with the Wellcome Trust Open Access policy and is governed by the licence available at http://www.rcpsych.ac.uk/pdf/Wellcome%20Trust%20licence.pdf': 'http://www.rcpsych.ac.uk/pdf/NIH%20licence%20agreement.pdf',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.0/uk/> ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.0/uk/',
     'This article is an Open Access article distributed under the terms and conditions of the Creative Commons Attribution license ( http://creativecommons.org/licenses/by/3.0/ ).': 'http://creativecommons.org/licenses/by/3.0/',
     'Available online without subscription through the open access option.': None,
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This article is distributed under the terms of an Attribution–Noncommercial–Share Alike–No Mirror Sites license for the first six months after the publication date (see http://www.jgp.org/misc/terms.shtml ). After six months it is available under a Creative Commons License (Attribution–Noncommercial–Share Alike 3.0 Unported license, as described at http://creativecommons.org/licenses/by-nc-sa/3.0/ ).': 'http://creativecommons.org/licenses/by-nc-sa/3.0/',
     'This is an open access article distributed under the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original paper is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This is an Open Access article distributed under the terms of the Creative Commons Attribution License ( http://creativecommons.org/licenses/by/3.0/ ), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
     'This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution license ( http://creativecommons.org/licenses/by/3.0/': 'http://creativecommons.org/licenses/by/3.0/',
     "You are free to share - to copy, distribute and transmit the work, under the following conditions: Attribution:   You must attribute the work in the manner specified by the author or licensor (but not in any way that suggests that they endorse you or your use of the work). Non-commercial:   You may not use this work for commercial purposes. No derivative works:   You may not alter, transform, or build upon this work. For any reuse or distribution, you must make clear to others the license terms of this work, which can be found at http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode. Any of the above conditions can be waived if you get permission from the copyright holder. Nothing in this license impairs or restricts the author's moral rights.": 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
    "This is an Open Access article: verbatim copying and redistribution of this article are permitted in all media for any purpose, provided this notice is preserved along with the article's original URL.": None,
    'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.5 ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.5',
    'This article is an open-access article distributed under the terms and conditions of the Creative Commons Attribution license http://creativecommons.org/licenses/by/3.0/ .': 'http://creativecommons.org/licenses/by/3.0/',
    'Published under the CreativeCommons Attribution NonCommercial-NoDerivs 3.0 License .': 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
    'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/3.0 ), which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited. This paper is available online free of all access charges (see http://jxb.oxfordjournals.org/open_access.html for further details)': 'http://creativecommons.org/licenses/by-nc/3.0',
    'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-ommercial License ( http://creativecommons.org/licenses/byc/2.5 ), which permits unrestricted nonommercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.5',
    'This paper accords with the Wellcome Trust Open Access policy and is governed by the licence available at http://www.rcpsych.ac.uk/pdf/Wellcome%20Trust%20licence.pdf': 'http://www.rcpsych.ac.uk/pdf/Wellcome%20Trust%20licence.pdf',
    'This paper accords with the NIH Public Access policy and is governed by the licence available at http://www.rcpsych.ac.uk/pdf/NIH%20licence%20agreement.pdf This paper accords with the Wellcome Trust Open Access policy and is governed by the licence available at http://www.rcpsych.ac.uk/pdf/Wellcome%20Trust%20licence.pdf': 'http://www.rcpsych.ac.uk/pdf/Wellcome%20Trust%20licence.pdf',
    'This article is an Open Access article distributed under the terms and conditions of the Creative Commons Attribution license http://creativecommons.org/licenses/by/3.0/ .': 'http://creativecommons.org/licenses/by/3.0/',
    'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses?by-nc/2.0/uk/ ) which permits unrestricted non-commercial use distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses?by-nc/2.0/uk/',
    'This is an Open Access article distributed under the terms of the Creative Commons-Attribution Noncommercial License ( http://creativecommons.org/licenses/by-nc/2.0/ ), which permits unrestricted noncommercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.0/',
    'Creative Commons Attribution Non-Commercial License applies to Author Choice Articles': 'http://creativecommons.org/licenses/by-nc/3.0/',
    'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.5 ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited. This paper is available online free of all access charges (see http://jxb.oxfordjournals.org/open_access.html for further details)': 'http://creativecommons.org/licenses/by-nc/2.5',
    'This is an open access article distributed under the terms of the creative commons attribution license, which permits unrestricteduse, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
    'available online without subscription through the open access option.': None,
    "Author's Choice": None,
    '# The authors have paid a fee to allow immediate free access to this article.': None,
    'Open Access articles can be viewed online without a subscription.': None,
    'This is an open access article distributed under the terms of the Creative Commons Attribution License (<url>http://creativecommons.org/licenses/by/2.0</url>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited': 'http://creativecommons.org/licenses/by/2.0',
    'This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
    "Author's Choice —Final version full access.": None,
    'This is an open-access article distributed under the terms of the Creative Commons Attribution-Noncommercial-Share Alike 3.0 Unported License, which permits unrestricted noncommercial use, distribution, and reproduction in any medium, provided the original author and source are credited.': 'http://creativecommons.org/licenses/by-nc-sa/3.0/',
    'This is an Open Access article distributed under the terms of the Creative Commons Attribution License ( http://creativecommons.org/licenses/by/2.0 ), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited': 'http://creativecommons.org/licenses/by/2.0',
    "Author's Choice - Final version full access. Creative Commons Attribution Non-Commercial License applies to Author Choice Articles": None,
    'The online version of this article has been published under an open access model. Users are entitled to use, reproduce, disseminate, or display the open access version of this article for non-commercial purposes provided that: the original authorship is properly and fully attributed; the Journal and Oxford University Press are attributed as the original place of publication with the correct citation details given; if an article is subsequently reproduced or disseminated not in its entirety but only in part or as a derivative work this must be clearly indicated. For commercial re-use, please contact journals.permissions@oxfordjournals.org Published by Oxford University Press on behalf of the International Epidemiological Association.': 'mailto:journals.permissions@oxfordjournals.org',
    "You are free to share - to copy, distribute and transmit the work, under the following conditions: Attribution :  You must attribute the work in the manner specified by the author or licensor (but not in any way that suggests that they endorse you or your use of the work). Non-commercial :  You may not use this work for commercial purposes. No derivative works :  You may not alter, transform, or build upon this work. For any reuse or distribution, you must make clear to others the license terms of this work, which can be found at http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode . Any of the above conditions can be waived if you get permission from the copyright holder. Nothing in this license impairs or restricts the author's moral rights.": 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
    'The Author(s) This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.0/uk/ ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.0/uk/',
    'This is an Open Access article distributed under the terms of the Creative Commons Attribution-Noncommercial License ( http://creativecommons.org/licenses/by-nc/3.0/ ), which permits unrestricted use, distribution, and reproduction in any noncommercial medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/3.0/',
    "Author's Choice Creative Commons Attribution Non-Commercial License applies to Author Choice Articles": 'http://creativecommons.org/licenses/by-nc/3.0/',
    'The online version of this article has been published under an open access model. Users are entitled to use, reproduce, disseminate, or display the open access version of this article for non-commercial purposes provided that: the original authorship is properly and fully attributed; the Journal and the Japanese Society of Plant Physiologists are attributed as the original place of publication with the correct citation details given; if an article is subsequently reproduced or disseminated not in its entirety but only in part or as a derivative work this must be clearly indicated. For commercial re-use, please contact journals.permissions@oxfordjournals.org': 'mailto:journals.permissions@oxfordjournals.org',
    'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial No Derivatives License, which permits for noncommercial use, distribution, and reproduction in any digital medium, provided the original work is properly cited and is not altered in any way.': 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
    'This paper accords with the NIH Public Access policy and is governed by the licence available at http://www.rcpsych.ac.uk/pdf/NIH%20licence%20agreement.pdf': 'http://www.rcpsych.ac.uk/pdf/NIH%20licence%20agreement.pdf',
    'This work is licensed under a Creative Commons Attribution NonCommercial 3.0 License (CC BYNC 3.0). Licensee PAGEPress, Italy': 'http://creativecommons.org/licenses/by-nc/3.0',
    'This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution license http://creativecommons.org/licenses/by/3.0/.': 'http://creativecommons.org/licenses/by/3.0/',
    'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/3.0/',
    'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License ( http://creativecommons.org/licenses/by-nc/2.5 ), which permits unrestricted non-commercial use, distribution and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.5',
    'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License http://creativecommons.org/licenses/by-nc/2.5/ ) which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by-nc/2.5/',
    'This is an open access article distributed under the Creative Commons Attribution License , which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.': 'http://creativecommons.org/licenses/by/3.0/',
    'This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial No Derivatives License, which permits for noncommercial use, distribution, and reproduction in any digital medium, provided the original work is properly cited and is not altered in any way. For details, please refer to http://creativecommons.org/licenses/by-nc-nd/3.0/': 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
    'This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.': 'http://creativecommons.org/licenses/by/3.0/'
 }

license_url_fixes = {
    'http://creativecommons.org/Licenses/by/2.0': 'http://creativecommons.org/licenses/by/2.0/',
    '(http://creativecommons.org/licenses/by/2.0)': 'http://creativecommons.org/licenses/by/2.0/',
    'http://(http://creativecommons.org/licenses/by/2.0)': 'http://creativecommons.org/licenses/by/2.0/',
    'http://creativecommons.org/licenses/by/2.0': 'http://creativecommons.org/licenses/by/2.0/',
    'http://creativecommons.org/licenses/by/3.0': 'http://creativecommons.org/licenses/by/3.0/',
    'http://creativecommons.org/licenses/by-nc-nd/3.0': 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
    'http://creativecommons.org/licenses/by-nc-sa/3.0': 'http://creativecommons.org/licenses/by-nc-sa/3.0/',
    'http://creativecommons.org/licenses/by-nc/3.0': 'http://creativecommons.org/licenses/by-nc/3.0/'
}

def _get_article_license_url(tree):
    """
    Given an ElementTree, returns article license URL.
    """
    license = ElementTree(tree).find('front/article-meta/permissions/license') or \
              ElementTree(tree).find('front/article-meta/copyright-statement') or \
              ElementTree(tree).find('front/article-meta/permissions/copyright-statement')
    try:
        license_url = license.attrib['{http://www.w3.org/1999/xlink}href']
        if license_url in license_url_fixes:
            return license_url_fixes[license_url]
        return license_url
    except AttributeError:  # license statement is missing
        return None
    except KeyError:  # license statement is in plain text
        license_text = ' '.join(license.itertext()).encode('utf-8')
        license_text = ' '.join(license_text.split())  # whitespace cleanup
        if license_text in license_url_equivalents:
            license_url = license_url_equivalents[license_text]
            if license_url in license_url_fixes:
                return license_url_fixes[license_url]
            return license_url
        else:
            for text in license_url_equivalents.keys():
                if license_text.endswith(text):  # could be dangerous
                    license_url = license_url_equivalents[text]
                    if license_url in license_url_fixes:
                        return license_url_fixes[license_url]
                    return license_url
            # FIXME: revert this to an exception some time in the future
            filename = '/tmp/pubmed-' + md5(license_text).hexdigest()
            with open(filename, 'w') as f:
                f.write(license_text)
                stderr.write("Unknown license statement:\n%s\n" % \
                    str(license_text))

def _get_article_copyright_holder(tree):
    """
    Given an ElementTree, returns article copyright holder.
    """
    copyright_holder = ElementTree(tree).find(
        'front/article-meta/permissions/copyright-holder'
    )
    try:
        copyright_holder = copyright_holder.text
        if copyright_holder is not None:
            return copyright_holder
    except AttributeError:  # no copyright_holder known
        pass

    copyright_statement = \
        ElementTree(tree).find('front/article-meta/copyright-statement') or \
        ElementTree(tree).find('front/article-meta/permissions/copyright-statement')
    try:
        copyright_statement = copyright_statement.text
        if copyright_statement is not None:
            return copyright_statement.split('.')[0] + '.'
    except AttributeError:
        pass

    return None

from sys import stderr

def _get_supplementary_materials(tree):
    """
    Given an ElementTree, returns a list of article supplementary materials.
    """
    materials = []
    for xref in tree.iter('xref'):
        try:
            if xref.attrib['ref-type'] == 'supplementary-material':
                rid = xref.attrib['rid']
                sup = _get_supplementary_material(tree, rid)
                if sup:
                    materials.append(sup)
        except KeyError:  # xref is missing ref-type or rid
            pass
    return materials

def _get_supplementary_material(tree, rid):
    """
    Given an ElementTree and an rid, returns supplementary material as a dictionary
    containing url, mimetype and label and caption.
    """
    for sup in tree.iter('supplementary-material'):
        try:
            if sup.attrib['id'] == rid:  # supplementary material found
                result = {}
                sup_tree = ElementTree(sup)

                label = sup_tree.find('label')
                result['label'] = ''
                if label is not None:
                    result['label'] = label.text

                caption = sup_tree.find('caption')
                result['caption'] = ''
                if caption is not None:
                    result['caption'] = ' '.join(caption.itertext())

                media = sup_tree.find('media')
                if media is not None:
                    result['mimetype'] = media.attrib['mimetype']
                    result['mime-subtype'] = media.attrib['mime-subtype']
                    result['url'] = _get_supplementary_material_url(
                        _get_pmcid(tree),
                        media.attrib['{http://www.w3.org/1999/xlink}href']
                    )
                    return result
        except KeyError:  # supplementary material has no ID
            continue

def _get_pmcid(tree):
    """
    Given an ElementTree, returns PubMed Central ID.
    """
    front = ElementTree(tree).find('front')
    for article_id in front.iter('article-id'):
        if article_id.attrib['pub-id-type'] == 'pmc':
            return article_id.text

def _get_article_doi(tree):
    """
    Given an ElementTree, returns DOI.
    """
    front = ElementTree(tree).find('front')
    for article_id in front.iter('article-id'):
        if article_id.attrib['pub-id-type'] == 'doi':
            return article_id.text

def _get_supplementary_material_url(pmcid, href):
    """
    This function creates absolute URIs for supplementary materials,
    using a PubMed Central ID and a relative URI.
    """
    return str('http://www.ncbi.nlm.nih.gov/pmc/articles/PMC' + pmcid +
        '/bin/' + href)
