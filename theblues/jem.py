import json

import requests

from private_blues.errors import log
from private_blues.utils import (
    ensure_trailing_slash,
    make_request,
)


class JEM(object):

    def __init__(self, url):
        self.url = ensure_trailing_slash(url)

    def fetch_macaroon(self):
        """ Fetches the macaroon from the JEM service.

        Return the base64 encoded macaroon.
        """
        try:
            # We don't use make_request b/c we don't want the request to be
            # fully handled. This lets us get the macaroon out of the request
            # and keep it.
            response = requests.get("{}env".format(self.url))
        except Exception as e:
            log.info('Unable to contact jem due to: {}'.format(e))
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

    def get_users_models(self, macaroons):
        """ Get the user's models from the JEM service.

        @param macaroons The discharged JEM macaroons.

        Return the json decoded list of environments.
        """
        return make_request("{}env".format(self.url), macaroons=macaroons)

    def get_model(self, macaroons, user, name):
        """ Get a specified model.

        @param macaroons The discharged JEM macaroons.
        @param user The username.
        @param name The name of the model.

        Return the json decoded model.
        """
        return make_request('{}env/{}/{}'.format(self.url, user, name),
                            macaroons=macaroons)
