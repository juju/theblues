from collections import namedtuple
import datetime

from theblues.errors import (
    log,
    ServerError,
)
from theblues.utils import (
    ensure_trailing_slash,
    make_request,
)

Term = namedtuple('Term',
                  ['name', 'title', 'revision', 'created_on', 'content'])
TERMS_VERSION = 'v1'


class Terms(object):

    def __init__(self, url):
        """Initializer.

        @param url The url to the Terms Service API.
        """
        self.url = ensure_trailing_slash(url) + TERMS_VERSION + '/'

    def get_terms(self, name, revision=None):
        """ Retrieve a specific term and condition.

        @param name of the terms.
        @param revision of the terms,
               if none provided it will return the latest.
        @return The list of terms.
        @raise ServerError
        """
        url = '{}terms/{}'.format(self.url, name)
        if revision:
            url = '{}?revision={}'.format(url, revision)
        json = make_request(url)
        try:
            # This is always a list of one element.
            data = json[0]
            return Term(name=data['name'],
                        title=data.get('title'),
                        revision=data['revision'],
                        created_on=datetime.datetime.strptime(
                            data['created-on'],
                            "%Y-%m-%dT%H:%M:%SZ"
                            ),
                        content=data['content'])
        except (KeyError, TypeError, ValueError) as err:
            log.info(
                'cannot process terms: invalid JSON response: {!r}'.format(
                    json))
            raise ServerError(
                'unable to get terms for {}: {}'.format(name, err))
