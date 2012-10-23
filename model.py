#!/usr/bin/env python
# -*- coding: utf-8 -*-

from elixir import *
from os import path

import config

def set_source(source):
    metadata.bind = 'sqlite:///%s' % config.database_path(source)

class Journal(Entity):
    title = Field(UnicodeText, primary_key=True)
    articles = OneToMany('Article')

class Category(Entity):
    name = Field(UnicodeText, primary_key=True)
    articles = ManyToMany('Article')

class Article(Entity):
    name = Field(UnicodeText)
    doi = Field(UnicodeText)
    title = Field(UnicodeText, primary_key=True)
    contrib_authors = Field(UnicodeText, primary_key=True)
    abstract = Field(UnicodeText)
    year = Field(Integer)  # should always be there
    month = Field(Integer)  # or None
    day = Field(Integer)  # or None
    url = Field(UnicodeText)
    license_url = Field(UnicodeText)
    license_text = Field(UnicodeText)
    copyright_statement = Field(UnicodeText)
    copyright_holder = Field(UnicodeText)
    journal = ManyToOne('Journal')
    supplementary_materials = OneToMany('SupplementaryMaterial')
    categories = ManyToMany('Category')

    def __repr__(self):
        return '<Article "%s">' % self.title.encode('utf-8')

class SupplementaryMaterial(Entity):
    label = Field(UnicodeText)
    title = Field(UnicodeText)
    caption = Field(UnicodeText)
    mimetype = Field(UnicodeText)
    mime_subtype = Field(UnicodeText)
    mimetype_reported = Field(UnicodeText)
    mime_subtype_reported = Field(UnicodeText)
    url = Field(UnicodeText, primary_key=True)
    article = ManyToOne('Article')
    downloaded = Field(Boolean, default=False)
    converted = Field(Boolean, default=False)
    uploaded = Field(Boolean, default=False)

    def __repr__(self):
        return '<SupplementaryMaterial “%s” of Article “%s”>' % \
            (self.label.encode('utf-8'), self.article.title.encode('utf-8'))
