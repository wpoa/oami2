#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    text += "}}\n"
    text += "|Author= %s\n" % authors
    text += "|Permission= %s Copyright owner: %s\n" % \
        (license_template, rights_holder)
    text += "}}\n\n"
    text += "[[Category:Uploaded with Open Access Media Importer]]"
    return text
