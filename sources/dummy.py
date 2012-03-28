#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep

def download_metadata(target_directory):
    for fake_file in [
        'http://example.org/file1',
        'http://example.org/file2',
        'http://example.org/file3'
    ]:
        fake_filesize = 1234
        for i in range(0, fake_filesize, 123):
            yield {
                'url': '' + fake_file,
                'completed': i,
                'total': fake_filesize
            }
            sleep(0.5)

def list_articles(target_directory):
    for fake_article in [
        {
            'article-contrib-authors': 'Alisson A, Bobsen B',
            'article-title': 'An Article regarding a specific Subject',
            'article-abstract': 'Lorem Ipsum Dolor Sit Amet.',
            'journal-title': 'Subject Research and Therapy',
            'article-date': '1997',
            'article-url': 'http://example.org/article-regarding-subject',
            'article-license-url': 'http://creativecommons.org/licenses/by/2.0',
            'article-copyright-holder': 'FakeMed Ltd.'

        },
        {
            'article-contrib-authors': 'Charleson C',
            'article-title': 'Another Article regarding that Subject',
            'article-abstract': 'Place abstract here, something about subject.',
            'journal-title': 'New England Journal of Subject',
            'article-date': '2003',
            'article-url': 'http://example.org/another-article-regarding-subject',
            'article-license-url': 'http://creativecommons.org/licenses/by-sa/2.0',
            'article-copyright-holder': 'EvilPub MegaCorp.'

        }
    ]:
        yield fake_article

def find_media(target_directory):
    for fake_media in [
        {
            'author': 'Kastberger G, Schmelzer E, Kranner I',
            'date': 'September 10, 2008',
            'description': 'This video shows two 130 cm-wide nests of the Asian Giant Honeybee Apis dorsata attached to a thick branch of a tree in Assam. The nest in the foreground displays shimmering: a Mexican-wave-like, spiral or circular, pattern. The ‘mouth’ zone of the nest is at the left bottom rim, where forager bees depart, arrive and dance. In contrast, the bees in the periphery are quiescent, but in response to hornet attacks, they produce shimmering.',
            'license': 'http://creativecommons.org/licenses/by/2.5/deed.en',
            'url': 'http://www.plosone.org/article/fetchSingleRepresentation.action?uri=info:doi/10.1371/journal.pone.0003141.s002',
            'source': 'http://dx.doi.org/10.1371/journal.pone.0003141'
        },
        {
            'author': 'Kastberger G, Schmelzer E, Kranner I',
            'date': 'September 10, 2008',
            'description': 'This video shows a nest attached to the ceiling of a water tower in Chitwan, Nepal. A typical, unsuccessful, hunting episode is shown in which a hornet chases a flying bee, but the bee escapes and lands on the nest. The landing of the bee and the manoeuvre of the hornet provokes shimmering, which makes the hornet turn off the nest. The film documents this in original speed.',
            'license': 'http://creativecommons.org/licenses/by/2.5/deed.en',
            'url': 'http://www.plosone.org/article/fetchSingleRepresentation.action?uri=info:doi/10.1371/journal.pone.0003141.s003',
            'source': 'http://dx.doi.org/10.1371/journal.pone.0003141'
        },
        {
            'author': 'Kastberger G, Schmelzer E, Kranner I',
            'date': 'September 10, 2008',
            'description': 'T',
            'license': 'http://creativecommons.org/licenses/by/2.5/deed.en',
            'url': '',
            'source': 'http://dx.doi.org/10.1371/journal.pone.0003141'
        }
    ]:
        yield fake_media
        sleep(1)
