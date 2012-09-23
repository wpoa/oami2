#!/usr/bin/env python
# -*- coding: utf-8 -*-

def page(article_doi, article_pmid, article_pmcid, authors, article_title, journal_title, date, article_url, \
    license_url, rights_holder, label, caption, categories):
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
    pmid = article_pmid
    if pmid:
        text += "| pmid = %s\n" % pmid
    pmcid = article_pmcid
    if pmcid:
        text += "| pmc = %s\n" % pmcid
    text += "}}\n"
    text += "|Author= %s\n" % authors
    text += "|Permission= %s Copyright owner: %s\n" % \
        (license_template, rights_holder)
    text += "|Other_fields={{Information field|name=Provenance|value= {{Open Access Media Importer}} }}\n"
    text += "}}\n\n"

    def _postprocess_category(category):
        if '(' in category:
            category = category.split('(')[0]
        if ',' in category:
            category_parts = category.split(',')
            category_parts.reverse()
            category = ' '.join(category_parts)
        category = category.strip().lower().capitalize()
        return category

    for category in categories:
        text += "[[Category:%s]]\n" % _postprocess_category(category)
    text += "[[Category:Media from %s]]\n" % journal_title
    text += "[[Category:Uploaded with Open Access Media Importer]]\n"
    text += '[[Category:Uploaded with Open Access Media Importer and needing category review]]\n'
    return text
