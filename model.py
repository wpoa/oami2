from elixir import *
from os import path

import config

def set_source(source):
    metadata.bind = 'sqlite:///%s' % config.database_path(source)

class Journal(Entity):
    title = Field(UnicodeText, primary_key=True)
    articles = OneToMany('Article')

class Article(Entity):
    name = Field(UnicodeText)
    title = Field(UnicodeText, primary_key=True)
    contrib_authors = Field(UnicodeText, primary_key=True)
    abstract = Field(UnicodeText)
    date = Field(UnicodeText)
    url = Field(UnicodeText)
    license_url = Field(UnicodeText)
    copyright_holder = Field(UnicodeText)
    journal = ManyToOne('Journal')
    supplementary_materials = OneToMany('SupplementaryMaterial')

class SupplementaryMaterial(Entity):
    label = Field(UnicodeText)
    caption = Field(UnicodeText)
    mimetype = Field(UnicodeText)
    mime_subtype = Field(UnicodeText)
    url = Field(UnicodeText, primary_key=True)
    article = ManyToOne('Article')
    
    def __repr__(self):
        return '<SupplementaryMaterial "%s" (%d)>' % (self.title, self.year)
