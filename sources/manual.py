#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen, urlparse, Request, HTTPError
from os import path
from sys import stderr
from uuid import uuid4

import csv

def download_metadata(target_directory):
    """
    Collects metadata for a single file.
    """
    result = {
        'name': uuid4(),
        'article-contrib-authors': raw_input('Authors: '),
        'article-title': raw_input('Article Title: '),
        'article-abstract': raw_input('Article Abstract: '),
        'journal-title': raw_input('Journal Title: '),
        'article-date': raw_input('Article Date: '),
        'article-url': raw_input('Article URL: '),
        'article-license-url': raw_input('Article License URL: '),
        'article-copyright-holder': raw_input('Article Copyright Holder: '),
        'supplementary-material-label': raw_input('Supplementary Material Label: '),
        'supplementary-material-caption': raw_input('Supplementary Material Caption: '),
        'supplementary-material-mimetype': raw_input('Supplementary Material MIME type: '),
        'supplementary-material-mime-subtype': raw_input('Supplementary Material MIME subtype: '),
        'supplementary-material-url': raw_input('Supplementary Material URL: ')
    }
    url = result['supplementary-material-url']
    yield { 'url': url, 'completed': 0, 'total': 1 }
    with open(path.join(target_directory, 'metadata.csv'), 'w') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                'name',
                'article-contrib-authors',
                'article-title',
                'article-abstract',
                'journal-title',
                'article-date',
                'article-url',
                'article-license-url',
                'article-copyright-holder',
                'supplementary-material-label',
                'supplementary-material-caption',
                'supplementary-material-mimetype',
                'supplementary-material-mime-subtype',
                'supplementary-material-url'
            ],
            quoting=csv.QUOTE_ALL
        )
        writer.writerow(result)
    yield { 'url': url, 'completed': 1, 'total': 1 }

def list_articles(target_directory, supplementary_materials=False, skip=[]):
    with open(path.join(target_directory, 'metadata.csv')) as f:
        reader = csv.DictReader(
            f,
            fieldnames=[
                'name',
                'article-contrib-authors',
                'article-title',
                'article-abstract',
                'journal-title',
                'article-date',
                'article-url',
                'article-license-url',
                'article-copyright-holder',
                'supplementary-material-label',
                'supplementary-material-caption',
                'supplementary-material-mimetype',
                'supplementary-material-mime-subtype',
                'supplementary-material-url'
            ],
            quoting=csv.QUOTE_ALL
        )
        for row in reader:
            result = {}
            result['name'] = row['name'].decode('utf-8')
            result['article-contrib-authors'] = row['article-contrib-authors'].decode('utf-8')
            result['article-title'] = row['article-title'].decode('utf-8')
            result['article-abstract'] = row['article-abstract'].decode('utf-8')
            result['journal-title'] = row['journal-title'].decode('utf-8')
            result['article-date'] = row['article-date'].decode('utf-8')
            result['article-url'] = row['article-url'].decode('utf-8')
            result['article-license-url'] = row['article-license-url'].decode('utf-8')
            result['article-copyright-holder'] = row['article-copyright-holder'].decode('utf-8')
        
            if supplementary_materials:
                result['supplementary-materials'] = [{
                    'label': row['supplementary-material-label'].decode('utf-8'),
                    'caption': row['supplementary-material-caption'].decode('utf-8'),
                    'mimetype': row['supplementary-material-mimetype'].decode('utf-8'),
                    'mime-subtype': row['supplementary-material-mime-subtype'].decode('utf-8'),
                    'url': row['supplementary-material-url'].decode('utf-8')
                }]
            yield result
