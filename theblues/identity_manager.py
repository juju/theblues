import base64
import json
import logging
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

from theblues.errors import (
    InvalidMacaroon,
    ServerError,
)
from theblues.utils import (
    ensure_trailing_slash,
    make_request,
)


class IdentityManager(object):
    """Identity Manager API."""

    def __init__(self, url, idm_user, idm_password, timeout=3.05):
        self.url = ensure_trailing_slash(url)
        self.auth = (idm_user, idm_password)
        self.timeout = timeout

    def get_user(self, username):
        """Fetch user data.

        @param username the user's name.

        Raise a ServerError if an error occurs in the request process.
        """
        url = '{}u/{}'.format(self.url, username)
        return make_request(url, auth=self.auth)

    def debug(self):
        """Retrieve the debug information from the identity manager."""
        url = '{}debug/status'.format(self.url)
        try:
            return make_request(url, timeout=self.timeout)
        except ServerError as err:
            return {"error": str(err)}

    def login(self, username, json_document):
        """Send user identity information to the identity manager.

        @param username -- the logged in user.
        @param json_document -- JSON payload for login.

        Raise a ServerError if an error occurs in the request process.
        """
        url = '{}u/{}'.format(self.url, username)
        make_request(
            url,
            method='PUT',
            body=json_document,
            auth=self.auth,
            timeout=self.timeout)

    def discharge(self, username, macaroon):
        """Discharge the macarooon for the identity.

        @param username -- the logged in user.
        @param macaroon -- the macaroon returned from CharmStore.

        Return the resulting base64 encoded macaroon.
        Raise a ServerError if an error occurs in the request process.
        """
        caveats = macaroon.third_party_caveats()
        if len(caveats) != 1:
            raise InvalidMacaroon(
                'Invalid number of third party caveats (1 != {})'
                ''.format(len(caveats)))
        url = '{}discharger/discharge?discharge-for-user={}&id={}'.format(
            self.url, quote(username), caveats[0][1])
        logging.debug('Sending identity info to {}'.format(url))
        logging.debug('data is {}'.format(caveats[0][1]))
        response = make_request(
            url, method='POST', auth=self.auth, timeout=self.timeout)
        macaroon = response['Macaroon']
        json_macaroon = json.dumps(macaroon)
        return base64.urlsafe_b64encode(json_macaroon.encode('utf-8'))

    def _get_extra_info_url(self, username):
        """Return the base URL for extra-info requests."""
        return '{}u/{}/extra-info'.format(self.url, username)

    def set_extra_info(self, username, extra_info):
        """Set extra info for the given user.

        @param username The username to update.
        @param info The extra info as a JSON encoded string, or as a Python
            dictionary like object.

        Raise a ServerError if an error occurs in the request process.
        """
        url = self._get_extra_info_url(username)
        make_request(
            url, method='PUT', body=extra_info, auth=self.auth,
            timeout=self.timeout)

    def get_extra_info(self, username):
        """Get extra info for the given user.

        @param username The username to get.

        Raise a ServerError if an error occurs in the request process.
        """
        url = self._get_extra_info_url(username)
        return make_request(url, auth=self.auth, timeout=self.timeout)
