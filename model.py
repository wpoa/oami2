from sqlalchemy import Column, Integer, UnicodeText, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import relationship
import sys
import importlib

def set_source(source):
    source_module = importlib.import_module(f'sources.{source}')

# Define the database engine
engine = create_engine('sqlite:///mydata.sqlite')

# Create a session factory
Session = sessionmaker(bind=engine)

# Create a session object
session = Session()

Base = declarative_base()
Base.metadata.create_all(engine)

class Journal(Base):
    __tablename__ = 'journal'

    title = Column(UnicodeText, primary_key=True)
    articles = relationship("Article", back_populates="journal")

article_category = Table(
    'article_category', Base.metadata,
    Column('article_title', UnicodeText, ForeignKey('article.title')),
    Column('category_name', UnicodeText, ForeignKey('category.name'))
)

class Category(Base):
    __tablename__ = 'category'

    name = Column(UnicodeText, primary_key=True)
    articles = relationship('Article', secondary=article_category, back_populates='categories')

class Article(Base):
    __tablename__ = 'article'

    name = Column(UnicodeText)
    doi = Column(UnicodeText)
    title = Column(UnicodeText, primary_key=True)
    contrib_authors = Column(UnicodeText, primary_key=True)
    abstract = Column(UnicodeText)
    year = Column(Integer)
    month = Column(Integer, nullable=True)
    day = Column(Integer, nullable=True)
    url = Column(UnicodeText)
    license_url = Column(UnicodeText)
    license_text = Column(UnicodeText)
    copyright_statement = Column(UnicodeText)
    copyright_holder = Column(UnicodeText)
    journal_title = Column(UnicodeText, ForeignKey('journal.title'))
    journal = relationship("Journal", back_populates="articles")
    supplementary_materials = relationship('SupplementaryMaterial', back_populates='article')
    categories = relationship('Category', secondary=article_category, back_populates='articles')

    def __repr__(self):
        return '<Article "%s">' % self.title.encode('utf-8')

class SupplementaryMaterial(Base):
    __tablename__ = 'supplementary_material'
    #id = Column(Integer, primary_key=True)
    label = Column(UnicodeText)
    title = Column(UnicodeText)
    caption = Column(UnicodeText)
    mimetype = Column(UnicodeText)
    mime_subtype = Column(UnicodeText)
    mimetype_reported = Column(UnicodeText)
    mime_subtype_reported = Column(UnicodeText)
    url = Column(UnicodeText, primary_key=True)
    article_title = Column(UnicodeText, ForeignKey('article.title'))
    article = relationship('Article', back_populates='supplementary_materials')
    downloaded = Column(Boolean, default=False)
    converting = Column(Boolean, default=False)
    converted = Column(Boolean, default=False)
    uploaded = Column(Boolean, default=False)

    def __repr__(self):
        return '<SupplementaryMaterial "%s" of Article "%s">' % \
            (self.label.encode('utf-8'), self.article.title.encode('utf-8'))
