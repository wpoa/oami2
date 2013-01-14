import config
import wikitools

from dateutil import parser
from sys import stderr

wiki = wikitools.wiki.Wiki(config.api_url)
wiki.login(username=config.username, password=config.password)

def query(params):
    request = wikitools.api.APIRequest(wiki, params)
    try:
        return request.query()
    except wikitools.api.APIError:
        stderr.write('Mediawiki API request failed, retrying.\n')
        return query(request)

def get_uploads():
    params = {
        'action': 'query',
        'list': 'usercontribs',
        'ucuser': config.username
        }
    result = query(params)
    return [
        (parser.parse(uc[u'timestamp']), uc[u'title']) \
            for uc in result[u'query'][u'usercontribs'] \
            if uc[u'ns'] == 6 and u'new' in uc.keys()
    ]

def get_wiki_name():
    params = {
        'action': 'query',
        'meta': 'siteinfo',
        'siprop': 'general'
    }
    request = query(params)
    return request[u'query'][u'general'][u'sitename']

def is_uploaded(material):
    params = {
        'action': 'query',
        'list': 'search',
        'srwhat': 'text',
        'srnamespace': '6',  # media files
        'srsearch': '"%s"+"%s"+"%s"' % (
            material.article.title,
            material.label,
            # Mediawiki does not always find text containing parentheses
            material.caption.split('.')[0].split('(')[0]
        )
    }
    result = query(params)
    try:
        if result[u'query'][u'searchinfo'][u'totalhits'] > 0:
            return True
    except KeyError:
        if len(result[u'query'][u'search']) > 0:
            return True
    return False

def upload(filename, wiki_filename, page_template):
    """
    Uploades a file to a mediawiki site.
    """
    wiki_file = wikitools.wikifile.File(wiki=wiki, title=wiki_filename)
    wiki_file.upload(
        fileobj = open(filename, 'r'),
        text=page_template.encode('utf-8'),
        comment = 'Automatically uploaded media file from [[:en:Open access|Open Access]] source. Please report problems or suggestions [[User talk:Open Access Media Importer Bot|here]].'
    )
