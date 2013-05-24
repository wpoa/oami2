import config
import wikitools

from dateutil import parser
from sys import stderr
from werkzeug.contrib.cache import SimpleCache
is_uploaded_cache = SimpleCache()

stderr.write('Authenticating with <%s>.\n' % config.api_url)
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
    """
    Determines if supplementary material is already uploaded.

    First, queries MediaWiki API by article DOI, then filters results.
    """
    result = is_uploaded_cache.get(material.article.doi)
    if result is None:
        params = {
            'action': 'query',
            'list': 'search',
            'srwhat': 'text',
            'srlimit': '50',
            'srredirects': '1',
            # TODO: redirect listing for search results does not work.
            # <https://bugzilla.wikimedia.org/show_bug.cgi?id=18017>
            'srnamespace': '6',  # media files
            'srsearch': material.article.doi
            }
        result = query(params)  # TODO: cache results for DOI
        is_uploaded_cache.set(material.article.doi, result)
    try:
        # If the MediaWiki API gives no search results for the article
        # DOI, the material has not been uploaded.
        if result[u'query'][u'searchinfo'][u'totalhits'] == 0:
            return False
    except KeyError:
        if len(result[u'query'][u'search']) == 0:
            return False
    # If none of the filenames do include a part of the original
    # filename, assume the file was not uploaded.
    filename_fragment = \
        '.'.join(material.url.split('/')[-1].split('.')[:-1])
    for page in result[u'query'][u'search']:
        if filename_fragment in page[u'title']:
            return True
    return False  # Caveat: This is almost certainly wrong if
                  # redirects do not show up in search results.

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
