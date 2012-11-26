import config
import wikitools

from sys import stderr

wiki = wikitools.wiki.Wiki(config.api_url)
wiki.login(username=config.username, password=config.password)

def _query(request):
    try:
        return request.query()
    except wikitools.api.APIError:
        stderr.write('Mediawiki API request failed, retrying.\n')
        return _query(request)

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
    request = wikitools.api.APIRequest(wiki, params)
    result = _query(request)
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
