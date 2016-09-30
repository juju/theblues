import json

import requests

from theblues.errors import log
from theblues.utils import (
    ensure_trailing_slash,
    make_request,
    DEFAULT_TIMEOUT,
)


class JIMM(object):

    def __init__(self, url, timeout=DEFAULT_TIMEOUT):
        """Initializer.

        @param url The url to the JIMM API.
        @param timeout How long to wait before timing out a request in seconds;
            a value of None means no timeout.
        """
        self.url = ensure_trailing_slash(url)
        self.timeout = timeout

    def fetch_macaroon(self):
        """ Fetches the macaroon from the JIMM controller.

        @return The base64 encoded macaroon.
        """
        try:
            # We don't use make_request b/c we don't want the request to be
            # fully handled. This lets us get the macaroon out of the request
            # and keep it.
            url = "{}model".format(self.url)
            response = requests.get(url, timeout=self.timeout)
        except requests.exceptions.Timeout:
            message = 'Request timed out: {url} timeout: {timeout}'
            message = message.format(url=url, timeout=self.timeout)
            log.error(message)
            return None
        except Exception as e:
            log.info('Unable to contact JIMM due to: {}'.format(e))
            return None

        try:
            json_response = response.json()
        except ValueError:
            log.info(
                'cannot process macaroon: '
                'cannot unmarshal response: {!r}'.format(response.content))
            return None

        try:
            raw_macaroon = json_response['Info']['Macaroon']
        except (KeyError, TypeError):
            log.info(
                'cannot process macaroon: invalid JSON response: {!r}'.format(
                    json_response))
            return None

        return json.dumps(raw_macaroon)

    def list_models(self, macaroons):
        """ Get the logged in user's models from the JIMM controller.

        @param macaroons The discharged JIMM macaroons.
        @return The json decoded list of environments.
        """
        return make_request("{}model".format(self.url), macaroons=macaroons,
                            timeout=self.timeout)
